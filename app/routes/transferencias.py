"""Transferência entre contas. Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import pegar_sessao
from app.models import Lancamento, Transferencia, Usuario, todos_os_campos
from app.parceiro import consultar_cotacao
from app.schemas import TransferenciaEntrada
from app.security import usuario_logado

rotas = APIRouter(prefix="/transferencias", tags=["transferência"])


@rotas.post("", status_code=201)
def transferir(
    dados: TransferenciaEntrada,
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Move dinheiro de uma conta para outra."""
    origem = sessao.get(Usuario, dados.origem_id)
    destino = sessao.get(Usuario, dados.destino_id)
    if origem is None or destino is None:
        raise HTTPException(status_code=404, detail="conta não encontrada")

    # O teto por transferência vem da API do parceiro.
    limite = consultar_cotacao()["limite_transferencia"]
    if dados.valor > limite:
        raise HTTPException(
            status_code=400, detail=f"valor acima do limite de {limite}"
        )

    origem.saldo = origem.saldo - dados.valor
    destino.saldo = destino.saldo + dados.valor

    transferencia = Transferencia(
        origem_id=origem.id,
        destino_id=destino.id,
        valor=dados.valor,
        chave_idempotencia=dados.chave_idempotencia,
    )
    sessao.add(transferencia)
    sessao.add(
        Lancamento(
            dono_id=origem.id,
            tipo="debito",
            valor=dados.valor,
            descricao=f"transferência para {destino.nome}",
        )
    )
    sessao.add(
        Lancamento(
            dono_id=destino.id,
            tipo="credito",
            valor=dados.valor,
            descricao=f"transferência de {origem.nome}",
        )
    )
    sessao.commit()
    sessao.refresh(transferencia)

    resposta = todos_os_campos(transferencia)
    resposta["saldo_da_origem"] = origem.saldo
    return resposta


@rotas.get("")
def historico(
    sessao: Session = Depends(pegar_sessao),
    logado: Usuario = Depends(usuario_logado),
):
    """Lista as transferências em que a conta de quem está logado aparece."""
    transferencias = (
        sessao.query(Transferencia)
        .filter(
            (Transferencia.origem_id == logado.id)
            | (Transferencia.destino_id == logado.id)
        )
        .all()
    )
    return [todos_os_campos(item) for item in transferencias]
