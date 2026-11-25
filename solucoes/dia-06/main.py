"""A aplicação do Banco Pop.

⚠️ Esta API é um alvo de treino do 7 Days of Code e nasce com falhas de
segurança de propósito. Rode apenas em localhost e nunca a coloque no ar.
"""

import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limites import limiter

from app.config import DEBUG, ORIGENS_LIBERADAS
from app.database import Base, motor
from app.routes import (
    admin,
    auth,
    contas,
    cotacao,
    extratos,
    transferencias,
    usuarios,
)

Base.metadata.create_all(bind=motor)

app = FastAPI(
    title="Banco Pop",
    version="2.0.0",
    description=(
        "API de treino do 7 Days of Code — Segurança de APIs.\n\n"
        "**Use somente na sua máquina.** Faça login pelo botão *Authorize*, "
        "com um dos usuários criados pelo `seed.py`."
    ),
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_LIBERADAS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.rotas)
app.include_router(usuarios.rotas)
app.include_router(contas.rotas)
app.include_router(extratos.rotas)
app.include_router(transferencias.rotas)
app.include_router(admin.rotas)
app.include_router(cotacao.rotas)


@app.exception_handler(Exception)
async def erro_inesperado(requisicao: Request, excecao: Exception):
    """Devolve o erro em JSON. Com DEBUG ligado, vai o detalhe técnico junto."""
    corpo = {"erro": "algo deu errado ao processar a requisição"}
    if DEBUG:
        corpo["excecao"] = repr(excecao)
        corpo["rastro"] = traceback.format_exc().splitlines()
        corpo["rota"] = str(requisicao.url)
    return JSONResponse(status_code=500, content=corpo)


@app.get("/", tags=["serviço"])
def inicio():
    return {
        "banco": "Banco Pop",
        "versao": app.version,
        "documentacao": "/docs",
        "aviso": "API de treino, com falhas de propósito. Rode só em localhost.",
    }
