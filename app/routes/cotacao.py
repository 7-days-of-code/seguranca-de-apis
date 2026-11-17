"""Conversão de valores usando a cotação do parceiro.

Alvo de treino: leia o FALHAS-PLANTADAS.md antes de mexer.
"""

from fastapi import APIRouter, Depends

from app.models import Usuario
from app.parceiro import consultar_cotacao
from app.security import usuario_logado

rotas = APIRouter(prefix="/cotacao", tags=["cotação"])


@rotas.get("/dolar")
def converter(valor: float, logado: Usuario = Depends(usuario_logado)):
    """Converte um valor em dólares para reais com a cotação do parceiro."""
    resposta = consultar_cotacao()
    taxa = resposta["taxa"]

    return {
        "valor_em_dolares": valor,
        "valor_em_reais": valor * taxa,
        "taxa_usada": taxa,
        "parceiro": resposta,
    }
