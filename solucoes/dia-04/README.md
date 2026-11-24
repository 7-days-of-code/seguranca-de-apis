# Dia 4: BOPLA e Mass Assignment

Solução testada sobre o estado do Dia 3, com Python 3.12. Depois dela, `pytest` mostra 6 testes passando e 1 com skip (o do Dia 5). As 14 chamadas de conferência do Dia 3 continuam com o mesmo status.


## Arquivos editados

### `app/schemas.py`

Em `CadastroEntrada`, apague as linhas `saldo` e `papel`, e acrescente `AtualizacaoEntrada` e `UsuarioSaida`:

```python
"""Os formatos de entrada e saída da API (Pydantic).

Hoje a API usa estes modelos só para ler o corpo das requisições. Nenhuma rota
declara `response_model`: o que sai é o dicionário montado pela rota.
"""

from pydantic import BaseModel, Field


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=3, max_length=40)
    email: str
    senha: str = Field(min_length=3)


class AtualizacaoEntrada(BaseModel):
    email: str | None = None


class UsuarioSaida(BaseModel):
    id: int
    nome: str
    email: str
    saldo: float


class TransferenciaEntrada(BaseModel):
    origem_id: int
    destino_id: int
    valor: float
    chave_idempotencia: str | None = None


class LancamentoEntrada(BaseModel):
    tipo: str
    valor: float
    descricao: str
```

### `app/routes/usuarios.py`

Substitua o arquivo inteiro (já inclui as mudanças do Dia 3):

```python
"""Rotas de usuário. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Usuario, todos_os_campos
from app.schemas import AtualizacaoEntrada, UsuarioSaida
from app.security import exigir_admin, usuario_logado

rotas = APIRouter(prefix="/usuarios", tags=["usuários"])


@rotas.get("", response_model=list[UsuarioSaida])
def listar(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(exigir_admin),
):
    """Lista as contas do banco."""
    usuarios = sessao.query(Usuario).all()
    return [todos_os_campos(usuario) for usuario in usuarios]


@rotas.get("/eu", response_model=UsuarioSaida)
def eu(usuario: Usuario = Depends(usuario_logado)):
    """Devolve os dados de quem está logado."""
    return todos_os_campos(usuario)


@rotas.get("/{usuario_id}", response_model=UsuarioSaida)
def detalhe(
    usuario_id: int,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Devolve os dados de uma conta."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None or usuario.id != logado.id:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    return todos_os_campos(usuario)


@rotas.put("/{usuario_id}", response_model=UsuarioSaida)
def atualizar(
    usuario_id: int,
    dados: AtualizacaoEntrada,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Atualiza o cadastro de uma conta com os campos enviados no corpo."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None or usuario.id != logado.id:
        raise HTTPException(status_code=404, detail="usuário não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)

    sessao.commit()
    sessao.refresh(usuario)
    return todos_os_campos(usuario)
```

### `app/routes/auth.py`

Duas trocas:

```python
from app.schemas import CadastroEntrada, UsuarioSaida
```

```python
@rotas.post(
    "/cadastro", status_code=status.HTTP_201_CREATED, response_model=UsuarioSaida
)
```

### `app/routes/admin.py`

Acrescente o import logo abaixo do `from app.models ...` e troque o decorator de `/usuarios`:

```python
from app.schemas import UsuarioSaida
```

```python
@rotas.get("/usuarios", response_model=list[UsuarioSaida])
```

### `testes/test_seguranca.py`

Apague só estas duas linhas, uma em cima de cada teste:

```python
@pytest.mark.skip(reason="Dia 4 (BOPLA): a API ainda devolve a senha")
@pytest.mark.skip(reason="Dia 4 (mass assignment): o cadastro aceita saldo e papel")
```

O skip do Dia 5 continua.

## Conferir o diff e rodar o pytest

```powershell
git --no-pager diff --stat
pytest -v
```

O `diff --stat` deve listar 5 arquivos: `schemas.py`, `usuarios.py`, `auth.py`, `admin.py` e `test_seguranca.py`. O `pytest` deve dar **6 passando e 1 com skip**.

## Testar na prática

Terminal 1:

```powershell
python seed.py
uvicorn app.main:app --reload
```

Terminal 2 (cole o bloco inteiro):

```powershell
$base = "http://127.0.0.1:8000"
function Token($u, $s) { (Invoke-RestMethod -Method Post -Uri "$base/login" -Body @{username=$u; password=$s}).access_token }
$bruno = Token "bruno" "bruno123"
$h = @{ Authorization = "Bearer $bruno" }

"--- 1. /usuarios/eu (bruno): só id, nome, email e saldo"
Invoke-RestMethod -Uri "$base/usuarios/eu" -Headers $h | ConvertTo-Json

"--- 2. cadastro com saldo 1000000 e papel admin: nasce com saldo 0"
$corpo = @{ nome="esperta"; email="esperta@bancopop.test"; senha="esperta123"; saldo=1000000; papel="admin" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/cadastro" -ContentType "application/json" -Body $corpo | ConvertTo-Json

"--- 3. a conta nova em /admin/usuarios: 403"
$nova = Token "esperta" "esperta123"
try { Invoke-RestMethod -Uri "$base/admin/usuarios" -Headers @{Authorization="Bearer $nova"} } catch { $_.Exception.Response.StatusCode.value__ }

"--- 4. PUT /usuarios/2 (bruno) com saldo, papel e email: só o e-mail muda"
$put = @{ saldo=999999; papel="admin"; email="novo@bancopop.test" } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri "$base/usuarios/2" -Headers $h -ContentType "application/json" -Body $put | ConvertTo-Json

"--- 5. /admin/usuarios (bruno) depois do PUT: 403"
try { Invoke-RestMethod -Uri "$base/admin/usuarios" -Headers $h } catch { $_.Exception.Response.StatusCode.value__ }
```

Esperado:

1. id 2, nome bruno, email e saldo 350, sem senha nem papel.
2. Conta nova com id 4, saldo 0 e sem papel na resposta.
3. Status 403
4. email trocado e saldo ainda 350.
5. Status 403

Para repetir, pare o uvicorn e rode `python seed.py` e o `uvicorn` de novo, porque a conta `esperta` já existirá e o cadastro devolveria 409.

| Chamada | Antes | Depois |
|---|---|---|
| `GET /usuarios/eu` (bruno) | traz senha (hash) e papel | só `id`, `nome`, `email`, `saldo` |
| `POST /cadastro` com `saldo: 1000000`, `papel: "admin"` | conta admin com R$ 1.000.000 | conta cliente com saldo 0 |
| `GET /admin/usuarios` com essa conta nova | 200 | 403 |
| `PUT /usuarios/2` (bruno) com `saldo`, `papel: "admin"`, `email` | vira admin com R$ 999.999 | só o e-mail muda |
| `GET /admin/usuarios` (bruno, depois do PUT) | 200 | 403 |

## Conferir que o Dia 3 continua valendo

Com o uvicorn no ar (depois de um `python seed.py`), rode de novo o script das 14 chamadas do Dia 3. As 14 linhas devem terminar em `OK`.