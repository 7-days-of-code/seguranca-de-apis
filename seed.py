"""Recria o banco do Banco Pop com os usuários e extratos de teste.

Rode com:  python seed.py
Pode rodar quantas vezes quiser: o banco é apagado e refeito do zero.
"""

from app.database import Base, Sessao, motor
from app.models import Lancamento, Usuario
from app.security import guardar_senha

USUARIOS = [
    {"nome": "ana", "email": "ana@bancopop.test", "senha": "ana123", "papel": "cliente", "saldo": 1200.00},
    {"nome": "bruno", "email": "bruno@bancopop.test", "senha": "bruno123", "papel": "cliente", "saldo": 350.00},
    {"nome": "admin", "email": "admin@bancopop.test", "senha": "admin123", "papel": "admin", "saldo": 0.00},
]

EXTRATOS = {
    "ana": [
        ("credito", 2000.00, "salário"),
        ("debito", 650.00, "aluguel"),
        ("debito", 150.00, "mercado"),
    ],
    "bruno": [
        ("credito", 500.00, "freela de design"),
        ("debito", 150.00, "internet"),
    ],
}


def semear():
    Base.metadata.drop_all(bind=motor)
    Base.metadata.create_all(bind=motor)

    sessao = Sessao()
    try:
        criados = {}
        for dados in USUARIOS:
            usuario = Usuario(
                nome=dados["nome"],
                email=dados["email"],
                senha=guardar_senha(dados["senha"]),
                papel=dados["papel"],
                saldo=dados["saldo"],
            )
            sessao.add(usuario)
            criados[dados["nome"]] = usuario

        sessao.flush()

        for nome, lancamentos in EXTRATOS.items():
            for tipo, valor, descricao in lancamentos:
                sessao.add(
                    Lancamento(
                        dono_id=criados[nome].id,
                        tipo=tipo,
                        valor=valor,
                        descricao=descricao,
                    )
                )

        sessao.commit()

        print("Banco do Banco Pop recriado.\n")
        print("usuário  senha      papel    saldo      extratos")
        print("-------  --------   -------  ---------  --------")
        for dados in USUARIOS:
            nome = dados["nome"]
            ids = [
                str(lancamento.id)
                for lancamento in sessao.query(Lancamento)
                .filter(Lancamento.dono_id == criados[nome].id)
                .all()
            ]
            print(
                f"{nome:<8} {dados['senha']:<10} {dados['papel']:<8} "
                f"R$ {dados['saldo']:>7.2f}  {', '.join(ids) or '-'}"
            )
        print("\nAgora rode:  uvicorn app.main:app --reload")
        print("E abra:      http://127.0.0.1:8000/docs")
    finally:
        sessao.close()


if __name__ == "__main__":
    semear()
