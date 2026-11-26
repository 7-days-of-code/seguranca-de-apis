# Dia 7: O alarme de cada porta


## Passo 1: a fixture `banco_limpo`

```python
from app.limites import limiter
from app.routes.auth import erros_de_login


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria os usuários de teste e zera o que a API guarda na memória."""
    semear()
    erros_de_login.clear()
    limiter.reset()
```

## Passo 2: um teste por ataque

Seguem o padrão `entrar`, chamar a rota, conferir o status. Quando o mesmo ataque vale para várias rotas, o `parametrize` evita repetir o teste:

```python
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
```

Os outros testes cobrem: a senha no banco começa com `$argon2`, o token forjado do Dia 1 recebe 401, a sexta tentativa de login dá 429, `{"papel": "admin"}` no PUT não abre o `/admin`, a 11ª chamada de `/extratos` dá 429, `limite=100000` dá 422, a mesma chave de idempotência desconta uma vez só, `/v1/usuarios/1` dá 404, o preflight de outro site volta sem `access-control-allow-origin` e o parceiro com `"taxa": "5,42"` dá 502.

Um dos testes do parceiro troca o arquivo com `monkeypatch.setattr("app.parceiro.ARQUIVO_PARCEIRO", ...)`. O alvo precisa ser `app.parceiro`, que é onde o nome é usado. Em `app.config`, o teste receberia 200.

## Passo 3: ver o alarme tocar

Desfaça uma correção por vez, rode `pytest -v` e depois `git restore` no arquivo:

| Correção desfeita | Testes que falham |
|---|---|
| Dia 3: em `extratos.py`, trocar `if lancamento is None or lancamento.dono_id != logado.id:` por `if lancamento is None:` nas 3 rotas (detalhe, PUT e DELETE) | `test_bruno_nao_ve_extrato_da_ana` e os 3 casos de `/extratos/1` do `parametrize` (4 falhas) |
| Dia 5: comentar o `@limiter.limit("10/minute")` do `GET /extratos` | `test_lista_de_extratos_tem_catraca` |
| Dia 4: tirar o `response_model=UsuarioSaida` de `GET /usuarios/eu` | `test_resposta_nao_traz_senha` |

## Antes e depois

| Falha | Antes | Depois |
|---|---|---|
| Dia 1: token forjado | um token montado à mão abria a conta da Ana | 401 |
| Dia 2: senha | guardada em texto puro | hash argon2 |
| Dia 2: login | tentativas ilimitadas | trava depois de 5 erros (429) |
| Dia 3: extratos, saldo e usuários de outra pessoa | o Bruno lia, alterava e apagava dados da Ana | 404 |
| Dia 3: área de admin | qualquer cliente entrava | 403 |
| Dia 4: `GET /usuarios/eu` | trazia a senha (hash) e o papel | só `id`, `nome`, `email` e `saldo` |
| Dia 4: cadastro com `saldo` e `papel: "admin"` | nascia admin com R$ 1.000.000 | nasce cliente com saldo 0 |
| Dia 4: `PUT /usuarios/{id}` com `papel` | o cliente virava admin | só o e-mail muda |
| Dia 5: transferência acima do saldo | passava e deixava o saldo negativo | 400 |
| Dia 5: `GET /extratos` em sequência | 20× 200 | 10× 200, depois 429 |
| Dia 5: `?limite=100000` | 200 | 422 |
| Dia 5: mesma chave de idempotência | descontava duas vezes | desconta uma vez |
| Dia 6: rotas `/v1` | 200, com dados e hash da senha | 404 |
| Dia 6: preflight de site de fora | origem liberada | sem `access-control-allow-origin` |
| Dia 6: parceiro com `"taxa": "5,42"` | 500 com rastro e caminhos de arquivo | 502 |
| Dia 6: erro 500 | mostrava exceção e rastro | só a mensagem genérica |