import json

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.config import ARQUIVO_PARCEIRO


class Cotacao(BaseModel):
    taxa: float = Field(gt=0, lt=100)
    limite_transferencia: float = Field(gt=0, le=10000)


def consultar_cotacao() -> dict:
    """Busca a cotação no parceiro e só aceita o que tem formato e faixa esperados."""
    with open(ARQUIVO_PARCEIRO, encoding="utf-8") as arquivo:
        bruto = json.load(arquivo)
    try:
        return Cotacao.model_validate(bruto).model_dump()
    except ValidationError:
        raise HTTPException(status_code=502, detail="o parceiro respondeu algo inesperado")