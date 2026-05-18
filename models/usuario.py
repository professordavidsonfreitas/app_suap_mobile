from sqlalchemy import ( # type: ignore
    Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Enum
)


from sqlalchemy.orm import ( # type: ignore
    relationship,
)

from database import Base

from sqlalchemy.sql import func # type: ignore



# =========================================================
# TABELA PRINCIPAL DE USUÁRIOS
# =========================================================

class Usuario(Base):
    __tablename__ = "usuarios"

    STATUS_PERFIL = (
        "estudante",
        "professor",
        "tae",
        "responsavel",
        "externo"
    )

    TIPO_LOGIN = (
        "suap",
        "cpf"
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # Identificador de login
    # matrícula, siape ou cpf
    login = Column(
        String(20),
        unique=True,
        nullable=False
    )

    # ID interno do SUAP
    suap_id = Column(
        Integer,
        unique=True
    )

    nome = Column(
        String(150),
        nullable=False
    )

    email_pessoal = Column(
        String(150),
        unique=True
    )

    telefone = Column(
        String(20)
    )

    cpf = Column(
        String(11),
        unique=True,
        nullable=False
    )

    nascimento = Column(
        Date,
        nullable=True
    )

    # Apenas para usuários externos
    senha_hash = Column(
        String
    )

    perfil = Column(
        Enum(
            *STATUS_PERFIL,
            name="perfil_usuario"
        ),
        nullable=False
    )

    tipo_login = Column(
        Enum(
            *TIPO_LOGIN,
            name="tipo_login_usuario"
        ),
        nullable=False
    )
    
    status = Column(
        Boolean,
        default=True
    )

    admin = Column(
        Boolean,
        default=False
    )

    ultimo_login = Column(
        DateTime
    )
    
    sincronizado_em = Column(
        DateTime
    )

    ultima_atualizacao = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


    # =====================================================
    # RELACIONAMENTOS
    # =====================================================
    estudante = relationship(
        "UsuarioEstudante",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    professor = relationship(
        "UsuarioProfessor",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    tae = relationship(
        "UsuarioTAE",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    externo = relationship(
        "UsuarioExterno",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    credencial_suap = relationship(
        "CredencialSUAP",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )

    responsavel = relationship(
        "UsuarioResponsavel",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )


# =========================================================
# ESTUDANTE
# =========================================================

class UsuarioEstudante(Base):

    __tablename__ = "usuarios_estudantes"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        unique=True,
        nullable=False
    )

    matricula = Column(
        String(20),
        unique=True,
        nullable=False
    )

    email_institucional = Column(
        String,
        unique=True
    )

    curso = Column(String)

    matriz = Column(String)

    ira = Column(String)

    ano_ingresso = Column(Integer)

    usuario = relationship(
        "Usuario",
        back_populates="estudante"
    )


# =========================================================
# PROFESSOR
# =========================================================

class UsuarioProfessor(Base):

    __tablename__ = "usuarios_professores"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        unique=True,
        nullable=False
    )

    matricula = Column(
        String(20),
        unique=True,
        nullable=False
    )

    email_institucional = Column(
        String,
        unique=True
    )

    cargo = Column(String)

    setor = Column(String)

    campus = Column(String)

    area_atuacao = Column(String)

    nucleo = Column(String)

    usuario = relationship(
        "Usuario",
        back_populates="professor"
    )
    

# =========================================================
# TAE
# =========================================================
class UsuarioTAE(Base):

    __tablename__ = "usuarios_tae"

    id = Column(Integer, primary_key=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        unique=True,
        nullable=False
    )

    matricula = Column(
        String(20),
        unique=True,
        nullable=False
    )

    email_institucional = Column(
        String,
        unique=True
    )

    cargo = Column(String)

    setor = Column(String)

    campus = Column(String)

    usuario = relationship(
        "Usuario",
        back_populates="tae"
    )


# =========================================================
# RESPONSÁVEL
# =========================================================

class UsuarioResponsavel(Base):

    __tablename__ = "usuarios_responsaveis"

    id = Column(
        Integer,
        primary_key=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    codigo_responsavel = Column(
        String(30),
        nullable=False
    )

    usuario = relationship(
        "Usuario",
        back_populates="responsavel"
    )

# =========================================================
# EXTERNO
# =========================================================

class UsuarioExterno(Base):
    __tablename__ = "usuarios_externos"

    id = Column(
        Integer,
        primary_key=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    interesse = Column(
        String(100)
    )

    usuario = relationship(
        "Usuario",
        back_populates="externo"
    )

# =========================================================
# CREDENCIAIS SUAP
# =========================================================
class CredencialSUAP(Base):

    __tablename__ = "credenciais_suap"

    id = Column(
        Integer,
        primary_key=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            ondelete="CASCADE"
        ),
        unique=True,
        nullable=False
    )

    usuario_suap = Column(
        String(30),
        nullable=False
    )

    credenciais_validas = Column(
        Boolean,
        default=True
    )

    erro_autenticacao = Column(
        Boolean,
        default=False
    )

    senha_suap_criptografada = Column(
        String
    )

    access_token = Column(
        String
    )

    refresh_token = Column(
        String
    )

    session_id = Column(
        String
    )

    expiracao_token = Column(
        DateTime
    )

    ultimo_login_suap = Column(
        DateTime
    )

    sincronizado_em = Column(
        DateTime
    )

    ativo = Column(
        Boolean,
        default=True
    )

    usuario = relationship(
        "Usuario",
        back_populates="credencial_suap"
    )