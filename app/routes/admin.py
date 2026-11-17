"""Área administrativa. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Transferencia, Usuario, todos_os_campos
from app.security import usuario_logado

rotas = APIRouter(prefix="/admin", tags=["admin"])


@rotas.get("/usuarios")
def listar_usuarios(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Painel do banco: todas as contas, com saldo e papel."""
    return [todos_os_campos(usuario) for usuario in sessao.query(Usuario).all()]


@rotas.get("/transferencias")
def listar_transferencias(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Painel do banco: todas as transferências já feitas."""
    return [
        todos_os_campos(item) for item in sessao.query(Transferencia).all()
    ]


@rotas.post("/usuarios/{usuario_id}/credito")
def creditar(
    usuario_id: int,
    valor: float,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Põe dinheiro na conta de alguém (usado pelo suporte do banco)."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="usuário não encontrado")

    usuario.saldo = usuario.saldo + valor
    sessao.commit()
    return {"usuario_id": usuario.id, "saldo": usuario.saldo}


@rotas.delete("/usuarios/{usuario_id}", status_code=204)
def apagar_usuario(
    usuario_id: int,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Encerra uma conta."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="usuário não encontrado")

    sessao.delete(usuario)
    sessao.commit()
