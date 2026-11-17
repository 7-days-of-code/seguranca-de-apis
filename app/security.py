"""Login, token de sessão e a dependência que diz quem está chamando a API.

Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer.
"""

import base64
import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Usuario

esquema_token = OAuth2PasswordBearer(tokenUrl="login")


def conferir_senha(senha_enviada: str, senha_guardada: str) -> bool:
    return senha_enviada == senha_guardada


def guardar_senha(senha: str) -> str:
    return senha


def criar_token(usuario: Usuario) -> str:
    """Empacota os dados do usuário em um texto que viaja no cabeçalho."""
    conteudo = {
        "sub": usuario.id,
        "nome": usuario.nome,
        "papel": usuario.papel,
    }
    bruto = json.dumps(conteudo).encode("utf-8")
    return base64.urlsafe_b64encode(bruto).decode("utf-8")


def ler_token(token: str) -> dict | None:
    try:
        bruto = base64.urlsafe_b64decode(token.encode("utf-8"))
        return json.loads(bruto)
    except Exception:
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

    usuario = sessao.get(Usuario, conteudo.get("sub"))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
