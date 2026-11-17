"""Conexão com o SQLite e a sessão que as rotas recebem por injeção."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import URL_BANCO

motor = create_engine(URL_BANCO, connect_args={"check_same_thread": False})
Sessao = sessionmaker(bind=motor, autoflush=False, autocommit=False)
Base = declarative_base()


def pegar_sessao():
    """Abre uma sessão por requisição e fecha no fim."""
    sessao = Sessao()
    try:
        yield sessao
    finally:
        sessao.close()
