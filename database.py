# =========================================================
# CONFIGURAÇÃO DO BANCO: CRIANDO O BANCO DE DADOS NO ENDEREÇO "sqlite:///banco.db"
# ========================================================

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# =========================================================
# DATABASE URL
# =========================================================

DATABASE_URL = os.getenv(

    "DATABASE_URL",

    "sqlite:///banco.db"
)

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