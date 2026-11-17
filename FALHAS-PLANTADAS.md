# Falhas plantadas no Banco Pop (gabarito do instrutor)

> ⚠️ **Este arquivo é para quem mantém a trilha, não para quem a faz.** Ele lista,
> uma por uma, as falhas que foram colocadas de propósito, onde cada uma mora e
> em que dia ela é corrigida. Mantenha-o fora do repositório que a pessoa clona
> (ou em uma branch separada), para não entregar as respostas.

O Banco Pop é um alvo de treino. Ele mapeia o **OWASP API Security Top 10 (2023)**.
Cada falha abaixo é reproduzível já na primeira execução, depois de `python seed.py`.

| Dia | Risco OWASP | Falha | Onde |
|---|---|---|---|
| 1 | — (reconhecimento) | A pessoa explora tudo abaixo de uma vez | toda a API |
| 2 | API2 — Autenticação quebrada | Senha salva em texto puro; "token" é só base64, sem assinatura nem validade; login sem limite de tentativas | [app/security.py](app/security.py) |
| 3 | API1 — BOLA | Rotas por ID não conferem o dono | [app/routes/extratos.py](app/routes/extratos.py), [app/routes/contas.py](app/routes/contas.py), [app/routes/usuarios.py](app/routes/usuarios.py) |
| 3 | API5 — BFLA | `/admin/*` só exige estar logado, não o papel admin | [app/routes/admin.py](app/routes/admin.py) |
| 4 | API3 — BOPLA (exposição) | Respostas montadas com `todos_os_campos`, inclusive `senha` e `papel` | todas as rotas |
| 4 | API3 — BOPLA (mass assignment) | Cadastro e `PUT /usuarios/{id}` copiam o corpo inteiro, aceitando `saldo` e `papel` | [app/routes/auth.py](app/routes/auth.py), [app/routes/usuarios.py](app/routes/usuarios.py) |
| 5 | API4 — Consumo sem limite | Sem rate limit; `GET /extratos?limite=` sem teto | [app/routes/extratos.py](app/routes/extratos.py) |
| 5 | API6 — Fluxo sensível | Transferência não confere saldo, não ignora origem ≠ logado, e repete com a mesma `chave_idempotencia` | [app/routes/transferencias.py](app/routes/transferencias.py) |
| 6 | API8 — Má configuração | CORS com `*` e `allow_credentials=True`; erros 500 vazam traceback e URL | [app/main.py](app/main.py), [app/config.py](app/config.py) |
| 6 | API9 — Inventário | Rotas antigas `/v1/*` sem autenticação, escondidas do Swagger | [app/routes/legado.py](app/routes/legado.py) |
| 6 | API10 — Consumo inseguro de terceiros | A cotação do parceiro é usada sem validar (taxa e limite entram direto) | [app/parceiro.py](app/parceiro.py), [app/routes/cotacao.py](app/routes/cotacao.py), [app/routes/transferencias.py](app/routes/transferencias.py) |
| 2 | API8 — Segredo no código | `SEGREDO` escrito em [app/config.py](app/config.py); a correção move para `.env` | [app/config.py](app/config.py) |
| 7 | API7 — regressão | Os ataques viram testes | [testes/test_seguranca.py](testes/test_seguranca.py) |

## Detalhe por falha

**Autenticação (Dia 2).** `conferir_senha` e `guardar_senha` em `security.py` não usam
hash — comparam texto puro. `criar_token`/`ler_token` só fazem base64 de um JSON, então
qualquer pessoa forja um token trocando o `sub`. Correção esperada: hash com salt
(ex.: `passlib`/`bcrypt`), JWT assinado com validade (`PyJWT`), e um limite de tentativas
no login (`slowapi`). O `SEGREDO` sai do código e vai para `.env`.

**BOLA (Dia 3).** `GET/PUT/DELETE /extratos/{id}`, `GET /contas/{id}/saldo` e
`GET/PUT /usuarios/{id}` carregam o registro pelo ID sem comparar com `logado.id`.
A dica do e-mail pede para listar todas as rotas que recebem um ID — de propósito,
porque o erro clássico é corrigir só o `GET` e esquecer `PUT`/`DELETE`.

**BFLA (Dia 3).** Nenhuma rota de `/admin` confere `logado.papel == "admin"`.

**Exposição e mass assignment (Dia 4).** `todos_os_campos` devolve a linha inteira do
banco (inclui `senha`). A correção é usar `response_model` do Pydantic. No cadastro e no
`PUT /usuarios/{id}`, o corpo é copiado inteiro, então dá para mandar `saldo` e `papel`.

**Consumo e fluxo sensível (Dia 5).** Sem rate limit em lugar nenhum; `?limite=` aceita
qualquer número e não tem teto; a transferência não verifica saldo, deixa transferir a
partir de conta que não é a sua (`origem_id` livre) e não trata idempotência.

**Configuração e terceiros (Dia 6).** CORS liberado com `*`; handler de erro devolve
`traceback` e a URL; `/v1/*` continua no ar sem token; a resposta do parceiro (taxa e
`limite_transferencia`) é usada sem validar tipo nem faixa.
