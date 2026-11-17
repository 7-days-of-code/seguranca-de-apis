"""As três tabelas do Banco Pop: usuários, lançamentos do extrato e transferências."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import Column

from app.database import Base


def agora():
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(40), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    senha = Column(String(255), nullable=False)
    papel = Column(String(20), nullable=False, default="cliente")
    saldo = Column(Float, nullable=False, default=0.0)
    criado_em = Column(DateTime, default=agora)

    lancamentos = relationship("Lancamento", back_populates="dono")


class Lancamento(Base):
    """Uma linha do extrato: um crédito ou um débito na conta de alguém."""

    __tablename__ = "extratos"

    id = Column(Integer, primary_key=True)
    dono_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = Column(String(20), nullable=False)  # credito | debito
    valor = Column(Float, nullable=False)
    descricao = Column(String(120), nullable=False)
    criado_em = Column(DateTime, default=agora)

    dono = relationship("Usuario", back_populates="lancamentos")


class Transferencia(Base):
    __tablename__ = "transferencias"

    id = Column(Integer, primary_key=True)
    origem_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    destino_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    valor = Column(Float, nullable=False)
    chave_idempotencia = Column(String(80), nullable=True)
    criado_em = Column(DateTime, default=agora)


def todos_os_campos(registro) -> dict:
    """Transforma um registro do banco em dicionário, com todas as colunas."""
    return {
        coluna.name: getattr(registro, coluna.name)
        for coluna in registro.__table__.columns
    }
