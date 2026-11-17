# Banco Pop — 7 Days of Code: Segurança de APIs

Uma API de mini-banco que **já vem com falhas de segurança de propósito**. No Dia 1
você invade a sua própria cópia; nos dias seguintes fecha uma família de falhas por dia,
até ter uma API que se defende e testes que provam isso.

> ⚠️ **Só na sua máquina.** Esta API é um alvo de treino e é insegura de propósito.
> Rode apenas em `localhost` e nunca a coloque no ar. Os ataques deste desafio são
> **só** contra a API rodando no seu computador.

---

## Como rodar

Você precisa de **Python 3.10 ou mais novo**. Dentro desta pasta:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (CMD)
.venv\Scripts\activate.bat
# Linux / macOS
source .venv/bin/activate
```

> **Windows:** se o PowerShell recusar o script ("execução de scripts foi desabilitada"),
> ou use o CMD, ou libere só para o seu usuário:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
> Documentação: <https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_execution_policies>

Instale as dependências, crie os dados de teste e suba a API:

```bash
pip install -r requirements.txt
```

```bash
python seed.py
```

```bash
uvicorn app.main:app --reload
```

Abra a tela de testes (Swagger UI): **<http://127.0.0.1:8000/docs>**

### Usuários de teste

| usuário | senha | papel | saldo |
|---|---|---|---|
| `ana` | `ana123` | cliente | R$ 1200,00 |
| `bruno` | `bruno123` | cliente | R$ 350,00 |
| `admin` | `admin123` | admin | R$ 0,00 |

Para logar no Swagger UI, clique em **Authorize** (cadeado no topo), informe usuário e
senha e confirme. O token passa a ir no cabeçalho `Authorization: Bearer ...` sozinho.
Rode `python seed.py` de novo sempre que quiser voltar os dados ao estado inicial.

---

## Os 7 dias

| Dia | Tema | O que você faz |
|---|---|---|
| 1 | 🔓 Atacando a própria API | Explora as falhas: troca um ID na URL e vê o extrato de outra pessoa |
| 2 | 🔑 Login que resiste a ataques | Hash de senha com salt, token assinado com validade, limite de tentativas |
| 3 | 🚪 Cada pessoa vê só o que é dela | BOLA e BFLA: conferir o dono do recurso e o papel nas rotas de admin |
| 4 | 🎭 Respostas sem dados demais | `response_model` para não vazar `senha`/`papel`; barrar `saldo`/`papel` no cadastro |
| 5 | 🚦 Limites contra abuso e fraude | Rate limit, paginação com teto, saldo e idempotência na transferência |
| 6 | 🧱 Configuração, versões e terceiros | CORS, erros que vazam, rota `/v1` esquecida, validar a resposta do parceiro |
| 7 | 🏁 Testes que travam as falhas | Transformar os ataques em testes de regressão (`pytest`) |

As falhas seguem o **OWASP API Security Top 10 (2023)**: <https://owasp.org/www-project-api-security/>

---

## O mapa da API

```
app/
├── main.py            ← cria o app, CORS e o handler de erro
├── config.py          ← segredo, banco, CORS, caminho do parceiro
├── database.py        ← conexão com o SQLite
├── models.py          ← tabelas: usuários, extratos, transferências
├── schemas.py         ← formatos de entrada (Pydantic)
├── security.py        ← login, token e "quem está logado"
├── parceiro.py        ← cliente da cotação (lê parceiro/resposta.json)
└── routes/
    ├── auth.py            /cadastro, /login
    ├── usuarios.py        /usuarios ...
    ├── contas.py          /contas/{id}/saldo
    ├── extratos.py        /extratos ...
    ├── transferencias.py  /transferencias
    ├── admin.py           /admin ...
    ├── cotacao.py         /cotacao/dolar
    └── legado.py          /v1 ... (versão antiga, escondida do Swagger)

seed.py                 ← recria usuários e extratos de teste
ataques/                ← scripts que o Swagger UI não dá conta de fazer
testes/                 ← onde os ataques viram testes, no Dia 7
parceiro/resposta.json  ← a "API de terceiro" simulada, em disco
```

### Scripts da pasta `ataques/`

O Swagger UI não consegue mandar muitas requisições rápidas. Para os dias que precisam
disso, rode (com a API no ar, em outra janela):

```bash
python ataques/muitas_requisicoes.py SEU_TOKEN
```

```bash
python ataques/tentativas_de_login.py
```

---

## Dia 7: rodar os testes

```bash
pytest -v
```

Os testes em [testes/test_seguranca.py](testes/test_seguranca.py) começam marcados com
`skip` porque falham de propósito — é a prova de que a falha existe. Conforme você corrige
cada dia, tire o `skip` do teste correspondente: ele passa a verde e nunca mais deixa a
falha voltar sem avisar.

---

## Antes e depois (para o portfólio)

No fim da trilha, conte no README a história de cada falha: **o ataque, por que funcionava
e como você fechou**. Um projeto com esse "antes e depois" versionado é o que poucos
projetos de iniciante têm — e é o que vale mostrar.
