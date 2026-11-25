# Dia 6: Configuração segura, rota legada e resposta do parceiro

## Arquivos editados

### `app/config.py`

Confirme que há `import os` no topo e troque as definições de `DEBUG` e das origens por:

```python
DEBUG = os.getenv("BANCO_POP_DEBUG") == "1"

ORIGENS_LIBERADAS = os.getenv(
    "BANCO_POP_ORIGENS", "http://localhost:3000"
).split(",")
```

### `app/main.py`

Tire o `legado` do import das rotas:

```python
from app.routes import (
    admin,
    auth,
    contas,
    cotacao,
    extratos,
    transferencias,
    usuarios,
)
```

Apague a linha `app.include_router(legado.rotas)` e, no `CORSMiddleware`, use as origens da configuração e `allow_credentials=False` (o token vai no cabeçalho, não em cookie):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_LIBERADAS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### `app/routes/legado.py`

Apague o arquivo. A lista de `include_router` do `main.py` é o inventário real da API: o que não está nela não existe.

### `app/parceiro.py`

Descreva o que se espera do parceiro e valide antes de usar:

```python
import json

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.config import ARQUIVO_PARCEIRO


class Cotacao(BaseModel):
    taxa: float = Field(gt=0, lt=100)
    limite_transferencia: float = Field(gt=0, le=10000)


def consultar_cotacao() -> dict:
    """Busca a cotação no parceiro e só aceita o que tem formato e faixa esperados."""
    with open(ARQUIVO_PARCEIRO, encoding="utf-8") as arquivo:
        bruto = json.load(arquivo)
    try:
        return Cotacao.model_validate(bruto).model_dump()
    except ValidationError:
        raise HTTPException(status_code=502, detail="o parceiro respondeu algo inesperado")
```

### `app/routes/cotacao.py`

Apague a linha `"parceiro": resposta,` do dicionário de retorno. Ela repassava ao cliente tudo o que o parceiro mandava.

## Conferência

Rode `pytest -v`: **7 passando**. Depois de `python seed.py` e do `uvicorn` no ar, com um token do bruno em `$t`:

| Chamada | Antes | Depois |
|---|---|---|
| Preflight CORS de `https://site-malicioso.example` | 200, origem liberada, `allow-credentials: true` | 400, sem cabeçalho de liberação |
| Preflight CORS de `http://localhost:3000` | 200 | 200 |
| `GET /v1/usuarios/1` e `/v1/extratos/1`, sem token | 200, com dados e hash da senha | 404 |
| Cotação com `"taxa": "5,42"` | 500 com exceção, rastro e caminhos de arquivo | 502 |
| Cotação com `"taxa": -5.42` | 200, valor em reais negativo | 502 |
| Transferência com `"limite_transferencia": "sem limite"` | 500 com rastro | 502 |
| `GET /cotacao/dolar?valor=100` normal | 200, repassa a resposta inteira do parceiro | 200, só valor, conversão e taxa |

Para as três linhas do parceiro, edite `parceiro/resposta.json`, salve e chame:

```powershell
curl.exe -s -w "  -> %{http_code}`n" -H "Authorization: Bearer $t" "http://127.0.0.1:8000/cotacao/dolar?valor=100"
```

Para o CORS (no PowerShell, use `curl.exe`):

```powershell
curl.exe -i -X OPTIONS http://127.0.0.1:8000/extratos -H "Origin: https://site-malicioso.example" -H "Access-Control-Request-Method: GET"
```

Ao terminar, devolva o `resposta.json` ao original (`git restore parceiro\resposta.json`).