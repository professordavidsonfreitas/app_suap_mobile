# =========================================================
# CONFIGURAÇÃO DO BANCO: CRIANDO O BANCO DE DADOS NO ENDEREÇO "sqlite:///banco.db"
# ========================================================
from sqlalchemy import create_engine #type: ignore
from sqlalchemy.orm import declarative_base #type: ignore
from sqlalchemy.orm import sessionmaker #type: ignore
import os

# =========================================================
# DATABASE URL
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:VXEhPPBbFeClKNYjBiysvMgvxgLIGIsl@postgres.railway.internal:5432/railway")

# =========================================================
# SQLITE
# =========================================================
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )
# =========================================================
# POSTGRES / OUTROS
# =========================================================
else:
    engine = create_engine(
        DATABASE_URL
    )

# =========================================================
# SESSION
# =========================================================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================================================
# BASE ORM
# =========================================================
Base = declarative_base()

# =========================================================
# DEPENDENCY PARA USAR NAS ROTAS
# =========================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# IMPORTAR MODELS (para criar as tabelas)
# =========================================================
from models.usuario import Usuario, UsuarioEstudante, UsuarioProfessor, UsuarioTAE, UsuarioResponsavel, UsuarioExterno, CredencialSUAP
from models.app_version import AppVersion

# =========================================================
# CRIAR TABELAS (se não existirem)
# =========================================================
Base.metadata.create_all(bind=engine)