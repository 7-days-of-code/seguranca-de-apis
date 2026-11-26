"""Testes de regressão de segurança do Banco Pop (Dia 7).

Cada ataque dos dias 1 a 6 vira um teste aqui. Um teste que passa significa
"a porta continua fechada"; se alguém reabrir a falha, o teste quebra.

    pytest -v
"""

import base64
import json

import pytest
from fastapi.testclient import TestClient

from app.database import Sessao
from app.limites import limiter
from app.main import app
from app.models import Usuario
from app.routes.auth import erros_de_login
from seed import semear

cliente = TestClient(app)


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria os usuários de teste e zera o que a API guarda na memória."""
    semear()
    erros_de_login.clear()
    limiter.reset()


def entrar(nome: str, senha: str) -> str:
    resposta = cliente.post("/login", data={"username": nome, "password": senha})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["access_token"]


def cabecalho(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---- Fumaça: o uso normal continua funcionando ----


def test_login_funciona():
    """O login da Ana devolve um token."""
    assert entrar("ana", "ana123")


def test_extrato_proprio_continua_visivel():
    """Nenhuma correção pode impedir a pessoa de ver o próprio extrato."""
    token = entrar("ana", "ana123")
    meus = cliente.get("/extratos", headers=cabecalho(token)).json()
    assert len(meus) == 3

    primeiro = meus[0]["id"]
    resposta = cliente.get(f"/extratos/{primeiro}", headers=cabecalho(token))
    assert resposta.status_code == 200


# ---- Dia 2: login ----


def test_senha_fica_guardada_como_hash():
    """O banco guarda a mistura, não a senha."""
    sessao = Sessao()
    ana = sessao.query(Usuario).filter_by(nome="ana").first()
    sessao.close()
    assert ana.senha.startswith("$argon2")


def test_token_forjado_e_recusado():
    """O token montado à mão do opcional do Dia 1 não abre a conta da Ana."""
    forjado = base64.urlsafe_b64encode(json.dumps({"sub": 1}).encode()).decode()
    resposta = cliente.get("/usuarios/eu", headers=cabecalho(forjado))
    assert resposta.status_code == 401


def test_login_trava_depois_de_cinco_erros():
    """Depois de cinco erros, nem a senha certa entra."""
    for _ in range(5):
        cliente.post("/login", data={"username": "ana", "password": "errada"})
    resposta = cliente.post("/login", data={"username": "ana", "password": "ana123"})
    assert resposta.status_code == 429


# ---- Dia 3: cada pessoa vê só o que é dela ----


def test_bruno_nao_ve_extrato_da_ana():
    token_ana = entrar("ana", "ana123")
    extrato_da_ana = cliente.get("/extratos", headers=cabecalho(token_ana)).json()[0]

    token_bruno = entrar("bruno", "bruno123")
    resposta = cliente.get(
        f"/extratos/{extrato_da_ana['id']}", headers=cabecalho(token_bruno)
    )
    assert resposta.status_code == 404


@pytest.mark.parametrize(
    "metodo, rota",
    [
        ("get", "/extratos/1"),
        ("put", "/extratos/1"),
        ("delete", "/extratos/1"),
        ("get", "/contas/1/saldo"),
        ("get", "/usuarios/1"),
        ("put", "/usuarios/1"),
    ],
)
def test_bruno_nao_alcanca_nada_da_ana(metodo, rota):
    """Toda rota com o ID da Ana responde 404 para o Bruno."""
    token = entrar("bruno", "bruno123")
    corpo = {"tipo": "debito", "valor": 1, "descricao": "x"}
    resposta = cliente.request(metodo, rota, headers=cabecalho(token), json=corpo)
    assert resposta.status_code == 404


def test_cliente_nao_entra_na_area_de_admin():
    token = entrar("bruno", "bruno123")
    resposta = cliente.get("/admin/usuarios", headers=cabecalho(token))
    assert resposta.status_code == 403


# ---- Dia 4: o que entra e o que sai ----


def test_resposta_nao_traz_senha():
    token = entrar("ana", "ana123")
    corpo = cliente.get("/usuarios/eu", headers=cabecalho(token)).json()
    assert "senha" not in corpo


def test_cadastro_nao_aceita_saldo_nem_papel():
    resposta = cliente.post(
        "/cadastro",
        json={
            "nome": "esperta",
            "email": "esperta@bancopop.test",
            "senha": "esperta123",
            "saldo": 1000000,
            "papel": "admin",
        },
    )
    criado = resposta.json()
    assert criado.get("saldo") == 0
    assert criado.get("papel") != "admin"


def test_cliente_nao_se_promove_a_admin():
    """Mandar papel no PUT não muda o papel."""
    token = entrar("bruno", "bruno123")
    cliente.put("/usuarios/2", headers=cabecalho(token), json={"papel": "admin"})
    resposta = cliente.get("/admin/usuarios", headers=cabecalho(token))
    assert resposta.status_code == 403


# ---- Dia 5: limites ----


def test_transferencia_acima_do_saldo_e_recusada():
    token = entrar("bruno", "bruno123")
    resposta = cliente.post(
        "/transferencias",
        headers=cabecalho(token),
        json={"origem_id": 2, "destino_id": 1, "valor": 1000},
    )
    assert resposta.status_code == 400


def test_lista_de_extratos_tem_catraca():
    """A 11ª chamada no mesmo minuto recebe 429."""
    token = entrar("ana", "ana123")
    codigos = [
        cliente.get("/extratos", headers=cabecalho(token)).status_code
        for _ in range(11)
    ]
    assert codigos == [200] * 10 + [429]


def test_lista_de_extratos_tem_teto():
    """Ninguém pede 100 mil registros de uma vez."""
    token = entrar("ana", "ana123")
    resposta = cliente.get("/extratos?limite=100000", headers=cabecalho(token))
    assert resposta.status_code == 422


def test_transferencia_repetida_desconta_uma_vez():
    """A mesma chave de idempotência não cobra duas vezes."""
    token = entrar("bruno", "bruno123")
    pedido = {"origem_id": 2, "destino_id": 1, "valor": 10, "chave_idempotencia": "pix-1"}
    for _ in range(2):
        cliente.post("/transferencias", headers=cabecalho(token), json=pedido)
    saldo = cliente.get("/contas/2/saldo", headers=cabecalho(token)).json()["saldo"]
    assert saldo == 340


# ---- Dia 6: configuração, versões e terceiros ----


def test_rota_antiga_nao_existe_mais():
    """A porta dos fundos /v1 continua trancada."""
    assert cliente.get("/v1/usuarios/1").status_code == 404


def test_cors_nao_libera_site_de_fora():
    """O navegador de um site qualquer não recebe permissão."""
    resposta = cliente.options(
        "/extratos",
        headers={
            "Origin": "https://site-malicioso.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in resposta.headers


def test_parceiro_estranho_vira_502(monkeypatch, tmp_path):
    """Resposta fora do formato do parceiro não entra na API."""
    arquivo = tmp_path / "resposta.json"
    arquivo.write_text('{"taxa": "5,42", "limite_transferencia": 5000}', encoding="utf-8")
    monkeypatch.setattr("app.parceiro.ARQUIVO_PARCEIRO", str(arquivo))
    token = entrar("ana", "ana123")
    resposta = cliente.get("/cotacao/dolar?valor=10", headers=cabecalho(token))
    assert resposta.status_code == 502


def test_erro_500_nao_mostra_o_rastro(monkeypatch, tmp_path):
    """Um erro inesperado responde só a mensagem genérica."""
    arquivo = tmp_path / "resposta.json"
    arquivo.write_text("isso nao e json", encoding="utf-8")
    monkeypatch.setattr("app.parceiro.ARQUIVO_PARCEIRO", str(arquivo))
    sem_explodir = TestClient(app, raise_server_exceptions=False)
    token = entrar("ana", "ana123")
    resposta = sem_explodir.get("/cotacao/dolar?valor=10", headers=cabecalho(token))
    assert resposta.status_code == 500
    assert "rastro" not in resposta.json()