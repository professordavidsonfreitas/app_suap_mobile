from sqlalchemy.orm import Session # type: ignore
from utils.jwt import gerar_token

from models.usuario import (
    Usuario,
    UsuarioEstudante,
    UsuarioProfessor,
    UsuarioTAE
)

import os

from schemas.auth import (RegistroExternoRequest)
from services.suap_service import autenticar_suap

from utils.security import gerar_hash, verificar_senha

def limpar_cpf(cpf: str) -> str:
    """Remove formatação do CPF (pontos e hífens)"""
    if not cpf:
        return cpf
    return cpf.replace(".", "").replace("-", "")

async def registrar_usuario_externo(
    db: Session,
    dados: RegistroExternoRequest
):
    # =====================================================
    # LIMPA CPF
    # =====================================================
    cpf_limpo = limpar_cpf(dados.cpf)
    
    # =====================================================
    # VERIFICA SE CPF JÁ EXISTE
    # =====================================================
    usuario_existente = db.query(Usuario).filter(
        Usuario.cpf == cpf_limpo
    ).first()
    if usuario_existente:
        raise Exception(
            "CPF já cadastrado"
        )
    # =====================================================
    # CRIA USUÁRIO PRINCIPAL
    # =====================================================
    usuario = Usuario(
        login=cpf_limpo,  # ← USE CPF LIMPO
        nome=dados.nome,
        cpf=cpf_limpo,  # ← USE CPF LIMPO
        nascimento=dados.nascimento,
        email_pessoal=dados.email_pessoal,
        telefone=dados.telefone,
        senha_hash=gerar_hash(dados.senha),
        perfil="externo",
        tipo_login="cpf"
    )

    db.add(usuario)

    db.flush()

    # =====================================================
    # CRIA PERFIL EXTERNO
    # =====================================================

    usuario_externo = UsuarioExterno(

        usuario_id=usuario.id
    )

    db.add(usuario_externo)

    db.commit()

    db.refresh(usuario)

    return usuario

async def autenticar_usuario(
    db,
    login,
    senha
):

    # =====================================================
    # BUSCA USUÁRIO
    # =====================================================

    usuario = db.query(Usuario).filter(
        Usuario.login == login
    ).first()

    # =====================================================
    # PRIMEIRO LOGIN SUAP
    # =====================================================

    if not usuario:

        resultado_suap = await autenticar_suap(
            login,
            senha
        )

        if not resultado_suap["sucesso"]:

            raise Exception(
                "usuário não encontrado"
            )

        dados = resultado_suap["dados"]

        usuario = await criar_usuario_suap(
            db,
            dados
        )

        # =====================================
        # GERA JWT IMEDIATAMENTE
        # =====================================

        token = gerar_token({

            "sub": usuario.login,

            "usuario_id": usuario.id,

            "perfil": usuario.perfil
        })

        return {

            "usuario": {

                "id": usuario.id,

                "nome": usuario.nome,

                "perfil": usuario.perfil
            },

            "token": token
        }

    # =====================================================
    # LOGIN EXTERNO
    # =====================================================

    if usuario.tipo_login == "cpf":

        senha_valida = verificar_senha(
            senha,
            usuario.senha_hash
        )

        if not senha_valida:

            raise Exception(
                "senha inválida"
            )

    # =====================================================
    # LOGIN SUAP
    # =====================================================

    elif usuario.tipo_login == "suap":

        resultado_suap = await autenticar_suap(
            login,
            senha
        )

        if not resultado_suap["sucesso"]:

            raise Exception(
                "credenciais SUAP inválidas"
            )

    # =====================================================
    # GERA TOKEN JWT
    # =====================================================

    token = gerar_token({

        "sub": usuario.login,

        "usuario_id": usuario.id,

        "perfil": usuario.perfil
    })

    # =====================================================
    # RETORNO
    # =====================================================

    return {

        "usuario": {

            "id": usuario.id,

            "nome": usuario.nome,

            "perfil": usuario.perfil
        },

        "token": token
    }


async def criar_usuario_suap(db, dados):
    # =====================================================
    # LIMPA CPF
    # =====================================================
    cpf_limpo = limpar_cpf(dados.get("cpf"))
    
    tipo_perfil = dados.get("tipo_perfil")
    subtipo_perfil = dados.get("subtipo_perfil")
    # =====================================================
    # DEFINE PERFIL BASE
    # =====================================================
    perfil_usuario = "estudante"
    if (tipo_perfil == "servidor" and subtipo_perfil == "docente"):
        perfil_usuario = "professor"
    elif (tipo_perfil == "servidor" and subtipo_perfil == "tae"):
        perfil_usuario = "tae"
    # =====================================================
    # CRIA USUÁRIO BASE
    # =====================================================
    usuario = Usuario(
        login=dados.get("matricula"),
        nome=dados.get("nome"),
        cpf=cpf_limpo,  # ← USE CPF LIMPO
        nascimento=None,
        email_pessoal=dados.get("email_pessoal"),
        telefone=dados.get("telefone"),
        senha_hash=None,
        perfil=perfil_usuario,
        tipo_login="suap"
    )

    BOOTSTRAP_ADMIN = os.getenv("BOOTSTRAP_ADMIN")

    if usuario.login == BOOTSTRAP_ADMIN:
        usuario.admin = True
        
    db.add(usuario)
    db.flush()

    

    # =====================================================
    # ESTUDANTE
    # =====================================================

    if tipo_perfil == "estudante":
        estudante = UsuarioEstudante(
            usuario_id=usuario.id,
            matricula=dados.get("matricula"),
            email_institucional=dados.get("email_institucional"),
            curso=dados.get("curso"),
            matriz=dados.get("matriz"),
            ira=dados.get("ira"),
            ano_ingresso=dados.get("ano_ingresso")
        )

        db.add(estudante)

    # =====================================================
    # DOCENTE
    # =====================================================

    elif (tipo_perfil == "servidor" and subtipo_perfil == "docente"):
        professor = UsuarioProfessor(
            usuario_id=usuario.id,
            matricula=dados.get("matricula"),
            email_institucional=dados.get("email_institucional"),
            cargo=dados.get("cargo"),
            setor=dados.get("setor"),
            campus=dados.get("campus"),
            area_atuacao=dados.get("area_atuacao")
        )
        db.add(professor)

    # =====================================================
    # TAE
    # =====================================================

    elif (tipo_perfil == "servidor" and subtipo_perfil == "tae"):
        tae = UsuarioTAE(
            usuario_id=usuario.id,
            matricula=dados.get("matricula"),
            email_institucional=dados.get("email_institucional"),
            cargo=dados.get("cargo"),
            setor=dados.get("setor"),
            campus=dados.get("campus")
        )
        db.add(tae)

    # =====================================================
    # SALVA
    # =====================================================

    db.commit()

    db.refresh(usuario)

    return usuario


async def sincronizar_usuario_suap(
    db,
    usuario,
    dados
):
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario.id
    ).first()
    # =========================================
    # BASE
    # =========================================
    usuario.email_pessoal = dados.get("email_pessoal")
    usuario.telefone = dados.get("telefone")

    if usuario.perfil == "professor":

        professor = usuario.professor
        professor.email_institucional = (dados.get("email_institucional"))
        professor.setor = dados.get("setor")
        professor.campus = dados.get("campus")

    elif usuario.perfil == "estudante":

        estudante = usuario.estudante
        estudante.email_institucional = (dados.get("email_institucional"))
        estudante.matriz = dados.get("matriz")
        estudante.ira = dados.get("ira")

    elif usuario.perfil == "tae":

        tae = usuario.tae
        tae.email_institucional = (dados.get("email_institucional"))
        tae.setor = dados.get("setor")
        tae.campus = dados.get("campus")

    db.commit()
    return usuario



