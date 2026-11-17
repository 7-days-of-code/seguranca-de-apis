"""Mostra que o login não limita tentativas — a falha que o Dia 2 corrige.

O script manda várias tentativas de login seguidas para a conta de teste `ana`
(criada pelo seed.py) e imprime o código de status de cada uma. O ponto não é
descobrir a senha: é ver que a API responde a todas na mesma velocidade, sem
nunca travar depois de muitos erros. Depois da correção do Dia 2, as tentativas
seguidas passam a receber 429.

    python ataques/tentativas_de_login.py

Use apenas contra a API rodando em http://127.0.0.1:8000 na sua máquina.
"""

import urllib.error
import urllib.parse
import urllib.request

API = "http://127.0.0.1:8000/login"
USUARIO = "ana"

# Uma senha certa (do seed) e várias erradas, só para gerar tentativas.
TENTATIVAS = ["errada1", "errada2", "errada3", "errada4", "errada5", "ana123"]

for senha in TENTATIVAS:
    corpo = urllib.parse.urlencode({"username": USUARIO, "password": senha}).encode()
    pedido = urllib.request.Request(API, data=corpo)
    try:
        with urllib.request.urlopen(pedido) as resposta:
            print(f"{senha:<10} -> {resposta.status} (login aceito)")
    except urllib.error.HTTPError as erro:
        print(f"{senha:<10} -> {erro.code}")

print(
    "\nHoje: as tentativas erradas devolvem 401 sem nenhum limite.\n"
    "Depois do Dia 2: depois de poucos erros, a API devolve 429 e faz esperar."
)
