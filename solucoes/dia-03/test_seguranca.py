"""Testes de regressão de segurança do Banco Pop (Dia 7).

Cada ataque dos dias 1 a 6 vira um teste aqui. Um teste que passa significa
"a porta continua fechada"; se alguém reabrir a falha, o teste quebra.

    pytest -v

Os testes marcados com @pytest.mark.skip falham hoje de propósito: é esse o
ponto. Tire o skip de cada um quando chegar o dia dele e tiver feito a correção.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from seed import semear

cliente = TestClient(app)


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria os usuários de teste antes de cada teste."""
    semear()


def entrar(nome: str, senha: str) -> str:
    resposta = cliente.post("/login", data={"username": nome, "password": senha})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()["access_token"]


def cabecalho(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---- Testes que já passam (servem de fumaça e de rede de proteção) ----


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


# ---- Testes que você liga conforme corrige cada falha ----


def test_bruno_nao_ve_extrato_da_ana():
    token_ana = entrar("ana", "ana123")
    extrato_da_ana = cliente.get("/extratos", headers=cabecalho(token_ana)).json()[0]

    token_bruno = entrar("bruno", "bruno123")
    resposta = cliente.get(
        f"/extratos/{extrato_da_ana['id']}", headers=cabecalho(token_bruno)
    )
    assert resposta.status_code == 404


def test_cliente_nao_entra_na_area_de_admin():
    token = entrar("bruno", "bruno123")
    resposta = cliente.get("/admin/usuarios", headers=cabecalho(token))
    assert resposta.status_code == 403


@pytest.mark.skip(reason="Dia 4 (BOPLA): a API ainda devolve a senha")
def test_resposta_nao_traz_senha():
    token = entrar("ana", "ana123")
    corpo = cliente.get("/usuarios/eu", headers=cabecalho(token)).json()
    assert "senha" not in corpo


@pytest.mark.skip(reason="Dia 4 (mass assignment): o cadastro aceita saldo e papel")
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


@pytest.mark.skip(reason="Dia 5: a transferência ainda não confere o saldo")
def test_transferencia_acima_do_saldo_e_recusada():
    token = entrar("bruno", "bruno123")
    resposta = cliente.post(
        "/transferencias",
        headers=cabecalho(token),
        json={"origem_id": 2, "destino_id": 1, "valor": 99999},
    )
    assert resposta.status_code == 400
