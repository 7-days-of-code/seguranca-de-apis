# Dia 5: Rate limit e regras da transferência

Solução testada sobre o estado do Dia 4 (arquivos de `solucoes/dia-03` e `solucoes/dia-04` aplicados), com Python 3.12 e `slowapi==0.1.9`. Depois dela, `pytest` mostra 7 testes passando e nenhum com skip. As conferências dos dias 3 e 4 continuam iguais.

## O desafio

1. **A catraca e a bandeja.** Rate limit de 10 por minuto com `slowapi` no `GET /extratos` e um teto de 50 no `?limite=`.
2. **As regras da transferência.** A origem passa a ser sempre quem está logado, e o valor precisa ser positivo e caber no saldo.
3. **Idempotência.** Se a mesma chave chegar de novo, a API devolve a transferência que já fez, em vez de fazer outra.

## Instalar

```powershell
pip install slowapi==0.1.9
```

## Arquivos editados

### `app/limites.py` (novo)

```python
"""Limites de uso da API (rate limit)."""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### `app/main.py`

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limites import limiter

# logo depois de app = FastAPI(...)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### `app/routes/extratos.py`

O `slowapi` exige `request: Request` na rota decorada. Sem ele, a API nem sobe.

```python
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.limites import limiter


@rotas.get("")
@limiter.limit("10/minute")
def listar(
    request: Request,
    limite: int = Query(default=20, ge=1, le=50),
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Lista os lançamentos da conta de quem está logado."""
    consulta = sessao.query(Lancamento).filter(Lancamento.dono_id == logado.id)
    consulta = consulta.limit(limite)
    return [todos_os_campos(lancamento) for lancamento in consulta.all()]
```

### `app/routes/transferencias.py`

Na função `transferir`, troque as 4 linhas logo abaixo do docstring (do `origem = sessao.get(...)` até o `raise` de "conta não encontrada") por este bloco. O resto da função, a partir do limite do parceiro, fica igual:

```python
    origem = logado  # a origem é sempre quem está logado; origem_id é ignorado
    destino = sessao.get(Usuario, dados.destino_id)
    if destino is None:
        raise HTTPException(status_code=404, detail="conta não encontrada")

    if dados.chave_idempotencia:
        repetida = (
            sessao.query(Transferencia)
            .filter_by(origem_id=logado.id, chave_idempotencia=dados.chave_idempotencia)
            .first()
        )
        if repetida:
            return todos_os_campos(repetida)

    if dados.valor <= 0 or dados.valor > origem.saldo:
        raise HTTPException(status_code=400, detail="valor inválido ou saldo insuficiente")
```

### `testes/test_seguranca.py`

Remova o `@pytest.mark.skip` de `test_transferencia_acima_do_saldo_e_recusada` e troque `"valor": 99999` por `"valor": 1000`.

O limite de R$ 5.000 do parceiro já recusava 99999, então o teste passava mesmo sem correção. Um teste que passa pelo motivo errado não protege nada. Com 1000, só a regra do saldo pode barrar.

## Conferência

Rode `pytest -v`: **7 passando e nenhum skip**. Depois de `python seed.py` e do `uvicorn` no ar (como bruno, saldo inicial R$ 350):

| Chamada | Antes | Depois |
|---|---|---|
| Transferir 1000 para a Ana | 201, saldo do Bruno −650 | 400, saldo 350 |
| `origem_id: 1` (Ana) → destino, 100 | 201, Ana perde 100 | origem vira o Bruno, a Ana não é afetada |
| Transferir −200 para a Ana | 201, Ana perde 200 | 400 |
| 2× transferência de 10 com `chave_idempotencia: "pix-123"` | desconta 20 | desconta 10, uma transferência só |
| `GET /extratos?limite=100000` | 200 | 422 |
| `ataques/muitas_requisicoes.py` | 20× 200 | 10× 200, depois 10× 429 |

Para o rate limit, pegue um token e passe para o script (rode uma vez por reinício do uvicorn, porque o contador fica em memória):

```powershell
$t = (Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/login" -Body @{username="bruno"; password="bruno123"}).access_token
python ataques\muitas_requisicoes.py $t
```