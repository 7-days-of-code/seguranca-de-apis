"""Saldo da conta. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Usuario
from app.security import usuario_logado

rotas = APIRouter(prefix="/contas", tags=["conta"])


@rotas.get("/{usuario_id}/saldo")
def saldo(
    usuario_id: int,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Mostra o saldo de uma conta."""
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="conta não encontrada")
    return {"usuario_id": usuario.id, "nome": usuario.nome, "saldo": usuario.saldo}
