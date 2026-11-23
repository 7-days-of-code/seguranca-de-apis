"""Login, token de sessão e a dependência que diz quem está chamando a API."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import MINUTOS_DO_TOKEN, SEGREDO
from app.database import pegar_sessao
from app.models import Usuario

esquema_token = OAuth2PasswordBearer(tokenUrl="login")
hasher = PasswordHash.recommended()


def conferir_senha(senha_enviada: str, senha_guardada: str) -> bool:
    return hasher.verify(senha_enviada, senha_guardada)


def guardar_senha(senha: str) -> str:
    return hasher.hash(senha)


def criar_token(usuario: Usuario) -> str:
    """Gera um JWT assinado com o SEGREDO e com prazo de validade."""
    conteudo = {
        "sub": str(usuario.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_DO_TOKEN),
    }
    return jwt.encode(conteudo, SEGREDO, algorithm="HS256")


def ler_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SEGREDO, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


def usuario_logado(
    token: str = Depends(esquema_token),
    sessao: Session = Depends(pegar_sessao),
) -> Usuario:
    """Devolve o usuário dono do token enviado no cabeçalho Authorization."""
    conteudo = ler_token(token)
    if conteudo is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    usuario = sessao.get(Usuario, int(conteudo["sub"]))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario