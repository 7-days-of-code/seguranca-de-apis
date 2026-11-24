"""Cadastro e login. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

import time

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Usuario, todos_os_campos
from app.schemas import CadastroEntrada, UsuarioSaida
from app.security import conferir_senha, criar_token, guardar_senha

rotas = APIRouter(tags=["acesso"])

MAX_ERROS = 5
SEGUNDOS_DE_ESPERA = 300

erros_de_login: dict[str, list[float]] = {}


@rotas.post(
    "/cadastro", status_code=status.HTTP_201_CREATED, response_model=UsuarioSaida
)
def cadastrar(dados: CadastroEntrada, sessao: Session = Depends(pegar_sessao)):
    """Cria uma conta nova no Banco Pop."""
    ja_existe = sessao.query(Usuario).filter(Usuario.nome == dados.nome).first()
    if ja_existe:
        raise HTTPException(status_code=409, detail="esse nome já está em uso")

    usuario = Usuario(**dados.model_dump())
    usuario.senha = guardar_senha(dados.senha)

    sessao.add(usuario)
    sessao.commit()
    sessao.refresh(usuario)
    return todos_os_campos(usuario)


@rotas.post("/login")
def login(
    formulario: OAuth2PasswordRequestForm = Depends(),
    sessao: Session = Depends(pegar_sessao),
):
    """Troca nome e senha por um token. No Swagger UI, use o botão Authorize."""
    agora = time.time()
    recentes = [
        t
        for t in erros_de_login.get(formulario.username, [])
        if agora - t < SEGUNDOS_DE_ESPERA
    ]
    if len(recentes) >= MAX_ERROS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="muitas tentativas, tente mais tarde",
        )

    usuario = (
        sessao.query(Usuario).filter(Usuario.nome == formulario.username).first()
    )
    if usuario is None or not conferir_senha(formulario.password, usuario.senha):
        erros_de_login[formulario.username] = recentes + [agora]
        raise HTTPException(status_code=401, detail="nome ou senha incorretos")

    erros_de_login.pop(formulario.username, None)
    return {"access_token": criar_token(usuario), "token_type": "bearer"}


