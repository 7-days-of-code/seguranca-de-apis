"""Rotas de usuário. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Usuario, todos_os_campos
from app.security import exigir_admin, usuario_logado

rotas = APIRouter(prefix="/usuarios", tags=["usuários"])


@rotas.get("")
def listar(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(exigir_admin),
):
    """Lista as contas do banco."""
    usuarios = sessao.query(Usuario).all()
    return [todos_os_campos(usuario) for usuario in usuarios]


@rotas.get("/eu")
def eu(usuario: Usuario = Depends(usuario_logado)):
    """Devolve os dados de quem está logado."""
    return todos_os_campos(usuario)


@rotas.get("/{usuario_id}")
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


@rotas.put("/{usuario_id}")
def atualizar(
    usuario_id: int,
    dados: dict,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Atualiza o cadastro de uma conta com os campos enviados no corpo."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None or usuario.id != logado.id:
        raise HTTPException(status_code=404, detail="usuário não encontrado")

    for campo, valor in dados.items():
        setattr(usuario, campo, valor)

    sessao.commit()
    sessao.refresh(usuario)
    return todos_os_campos(usuario)
