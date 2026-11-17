"""Dispara 20 requisições seguidas e mostra o código de status de cada uma.

Serve para testar, na sua própria máquina, se o rate limit do Dia 5 está de pé.
O Swagger UI não consegue mandar requisições rápidas o bastante para isso.

    python ataques/muitas_requisicoes.py SEU_TOKEN

Use apenas contra a API rodando em http://127.0.0.1:8000 na sua máquina.
"""

import sys
import urllib.error
import urllib.request

API = "http://127.0.0.1:8000/extratos"
token = sys.argv[1] if len(sys.argv) > 1 else ""

for tentativa in range(1, 21):
    pedido = urllib.request.Request(API, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(pedido) as resposta:
            codigo = resposta.status
    except urllib.error.HTTPError as erro:
        codigo = erro.code
    print(f"requisição {tentativa:>2}: {codigo}")

print(
    "\nAntes do Dia 5: todas devolvem 200.\n"
    "Depois do Dia 5: as primeiras passam e as seguintes devolvem 429."
)
