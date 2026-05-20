from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from sqlalchemy.sql import func
from database import Base

class AppVersion(Base):
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    versao = Column(String, unique=True, index=True)
    build = Column(Integer, unique=True, nullable=False)
    obrigatoria = Column(Boolean, default=False)
    apk_url = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())