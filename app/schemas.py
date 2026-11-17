"""Os formatos de entrada e saída da API (Pydantic).

Hoje a API usa estes modelos só para ler o corpo das requisições. Nenhuma rota
declara `response_model`: o que sai é o dicionário montado pela rota.
"""

from pydantic import BaseModel, Field


class CadastroEntrada(BaseModel):
    nome: str = Field(min_length=3, max_length=40)
    email: str
    senha: str = Field(min_length=3)
    saldo: float = 0.0
    papel: str = "cliente"


class TransferenciaEntrada(BaseModel):
    origem_id: int
    destino_id: int
    valor: float
    chave_idempotencia: str | None = None


class LancamentoEntrada(BaseModel):
    tipo: str
    valor: float
    descricao: str
