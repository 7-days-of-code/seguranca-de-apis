"""Cliente da API de cotação do parceiro.

O "parceiro" não é um serviço de fora: é o arquivo parceiro/resposta.json, lido
a cada chamada. Assim o desafio do Dia 6 roda sem internet e sem chave de API —
e dá para simular um fornecedor invadido só editando o arquivo.
"""

import json

from app.config import ARQUIVO_PARCEIRO


def consultar_cotacao() -> dict:
    """Busca a cotação do dólar no parceiro e devolve a resposta como veio."""
    with open(ARQUIVO_PARCEIRO, encoding="utf-8") as arquivo:
        return json.load(arquivo)
