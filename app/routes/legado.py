"""Primeira versão da API, de quando o Banco Pop era um protótipo.

O app de celular antigo ainda aponta para cá, então ninguém desligou.
Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Lancamento, Usuario, todos_os_campos

rotas = APIRouter(prefix="/v1", include_in_schema=False)


@rotas.get("/extratos/{lancamento_id}")
def detalhe_v1(lancamento_id: int, sessao: Session = Depends(pegar_sessao)):
    lancamento = sessao.get(Lancamento, lancamento_id)
    if lancamento is None:
        raise HTTPException(status_code=404, detail="lançamento não encontrado")
    return todos_os_campos(lancamento)


@rotas.get("/usuarios/{usuario_id}")
def usuario_v1(usuario_id: int, sessao: Session = Depends(pegar_sessao)):
    usuario = sessao.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="usuário não encontrado")
    return todos_os_campos(usuario)
