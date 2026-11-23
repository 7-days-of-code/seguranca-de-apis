"""Rotas do extrato. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Lancamento, Usuario, todos_os_campos
from app.schemas import LancamentoEntrada
from app.security import usuario_logado

rotas = APIRouter(prefix="/extratos", tags=["extrato"])


@rotas.get("")
def listar(
    limite: int | None = None,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Lista os lançamentos da conta de quem está logado."""
    consulta = sessao.query(Lancamento).filter(Lancamento.dono_id == logado.id)
    if limite is not None:
        consulta = consulta.limit(limite)
    return [todos_os_campos(lancamento) for lancamento in consulta.all()]


@rotas.post("", status_code=201)
def criar(
    dados: LancamentoEntrada,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Cria um lançamento na conta de quem está logado."""
    lancamento = Lancamento(dono_id=logado.id, **dados.model_dump())
    sessao.add(lancamento)
    sessao.commit()
    sessao.refresh(lancamento)
    return todos_os_campos(lancamento)


@rotas.get("/{lancamento_id}")
def detalhe(
    lancamento_id: int,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Devolve um lançamento do extrato."""
    lancamento = sessao.get(Lancamento, lancamento_id)
    if lancamento is None or lancamento.dono_id != logado.id:
        raise HTTPException(status_code=404, detail="lançamento não encontrado")
    return todos_os_campos(lancamento)


@rotas.put("/{lancamento_id}")
def atualizar(
    lancamento_id: int,
    dados: LancamentoEntrada,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Altera a descrição, o tipo e o valor de um lançamento."""
    lancamento = sessao.get(Lancamento, lancamento_id)
    if lancamento is None or lancamento.dono_id != logado.id:
        raise HTTPException(status_code=404, detail="lançamento não encontrado")

    lancamento.tipo = dados.tipo
    lancamento.valor = dados.valor
    lancamento.descricao = dados.descricao
    sessao.commit()
    sessao.refresh(lancamento)
    return todos_os_campos(lancamento)


@rotas.delete("/{lancamento_id}", status_code=204)
def apagar(
    lancamento_id: int,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Apaga um lançamento do extrato."""
    lancamento = sessao.get(Lancamento, lancamento_id)
    if lancamento is None or lancamento.dono_id != logado.id:
        raise HTTPException(status_code=404, detail="lançamento não encontrado")

    sessao.delete(lancamento)
    sessao.commit()
