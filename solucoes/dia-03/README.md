# Solução do Dia 3

Testada sobre a branch `solucoes` (estado do Dia 2), com Python 3.12. Depois dela, o `pytest` mostra 4 testes passando e 3 com `skip` (os dos Dias 4 e 5).

## `app/security.py`: no fim do arquivo

```python
def exigir_admin(logado: Usuario = Depends(usuario_logado)) -> Usuario:
    """Deixa passar só quem tem o papel admin."""
    if logado.papel != "admin":
        raise HTTPException(status_code=403, detail="área restrita")
    return logado
```

## `app/routes/extratos.py`: em `detalhe`, `atualizar` e `apagar`

```python
    if lancamento is None or lancamento.dono_id != logado.id:
```

## `app/routes/contas.py` (`saldo`) e `app/routes/usuarios.py` (`detalhe` e `atualizar`)

```python
    if usuario is None or usuario.id != logado.id:
```

## `app/routes/usuarios.py`: a lista passa a exigir admin

```python
from app.security import exigir_admin, usuario_logado


@rotas.get("")
def listar(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(exigir_admin),
):
    """Lista as contas do banco."""
    usuarios = sessao.query(Usuario).all()
    return [todos_os_campos(usuario) for usuario in usuarios]
```

## `app/routes/admin.py`

```python
from app.security import exigir_admin, usuario_logado

rotas = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(exigir_admin)]
)
```

## `testes/test_seguranca.py`

Remova o `@pytest.mark.skip` de `test_bruno_nao_ve_extrato_da_ana` e de `test_cliente_nao_entra_na_area_de_admin`.

## Conferido

Logado como bruno, depois de `python seed.py`:

| Chamada | Status |
|:---|:---:|
| `GET`, `PUT` e `DELETE /extratos/1` | 404 |
| `GET /extratos/4` | 200 |
| `GET /contas/1/saldo` · `GET` e `PUT /usuarios/1` | 404 |
| `GET /contas/2/saldo` · `GET /usuarios/2` | 200 |
| `GET /usuarios` sem token / bruno / admin | 401 / 403 / 200 |
| `/admin/usuarios`, `/admin/transferencias`, `POST .../credito`, `DELETE /admin/usuarios/1` | 403 |
| `GET /admin/usuarios` como admin | 200 |