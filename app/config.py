"""Configuração do Banco Pop.

Atenção, time de conteúdo: este projeto é um alvo de treino e nasce inseguro
de propósito. Antes de "arrumar" qualquer coisa aqui, leia o FALHAS-PLANTADAS.md.
"""

import os

# Segredo usado para assinar o token de sessão.
SEGREDO = "banco-pop-123"

# O banco é um arquivo SQLite na raiz do projeto. Apagar o arquivo e rodar o
# seed.py de novo volta tudo ao estado inicial.
ARQUIVO_BANCO = os.getenv("BANCO_POP_BANCO", "banco_pop.db")
URL_BANCO = f"sqlite:///{ARQUIVO_BANCO}"

# Quando ligado, as respostas de erro trazem o detalhe técnico da exceção.
DEBUG = True

# Origens autorizadas a chamar a API pelo navegador.
ORIGENS_LIBERADAS = ["*"]

# Arquivo que simula a resposta da API de cotação de um parceiro. Fica em disco
# para que o desafio do Dia 6 não dependa de nenhum serviço de fora.
ARQUIVO_PARCEIRO = os.path.join("parceiro", "resposta.json")
