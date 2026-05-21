from fastapi import (APIRouter, Depends, HTTPException, status) # type: ignore
from sqlalchemy.orm import Session # type: ignore

from auth.dependences import get_current_user

from database import SessionLocal

from schemas.auth import (
    LoginRequest,
    RegistroExternoRequest,
    SincronizarRequest
)

from services.auth_service import (
    autenticar_usuario,
    registrar_usuario_externo,
    sincronizar_usuario_suap
)

from schemas.auth import (
    UsuarioMeResponse
)

from services.suap_service import (
    autenticar_suap
)

from models.usuario import Usuario

# =========================================================
# CONFIGURAÇÃO DA ROTA
# =========================================================

auth_router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"]
)



# =========================================================
# ROTA TESTE
# =========================================================

@auth_router.get("/")
async def rota_auth():

    return {
        "mensagem": "rota de autenticação"
    }

# =========================================================
# LOGIN
# =========================================================

@auth_router.post("/login")
async def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):

    try:

        resultado = await autenticar_usuario(
            db=db,
            login=dados.login,
            senha=dados.senha
        )

        return {
            "mensagem": "login realizado com sucesso",
            "usuario": resultado["usuario"],
            "token": resultado["token"]
        }

    except Exception as erro:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro)
        )


# =========================================================
# REGISTRO DE USUÁRIO EXTERNO
# =========================================================

@auth_router.post("/externo/registrar")
async def registrar_externo(
    dados: RegistroExternoRequest,
    db: Session = Depends(get_db)
):

    try:

        usuario = await registrar_usuario_externo(
            db=db,
            dados=dados
        )

        return {
            "mensagem": "usuário externo criado com sucesso",
            "usuario_id": usuario.id
        }

    except Exception as erro:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(erro)
        )
    
@auth_router.get("/me")
async def me(usuario: Usuario = Depends(get_current_user)):

    # =====================================================
    # BASE
    # =====================================================

    response = {
        "id": usuario.id,
        "nome": usuario.nome,
        "perfil": usuario.perfil,
        "cpf": usuario.cpf,
        "email_pessoal": usuario.email_pessoal,
        "telefone": usuario.telefone,
        "tipo_login": usuario.tipo_login,
        "admin": usuario.admin
    }

    # =====================================================
    # EXTERNO
    # =====================================================

    if usuario.perfil == "externo":

        return response

    # =====================================================
    # PROFESSOR
    # =====================================================

    if usuario.perfil == "professor":

        professor = usuario.professor
        response.update({
            "matricula": professor.matricula,
            "email_institucional": professor.email_institucional,
            "cargo": professor.cargo,
            "setor": professor.setor,
            "campus": professor.campus,
            "area_atuacao": professor.area_atuacao,
            "nucleo": professor.nucleo
        })

        return response

    # =====================================================
    # TAE
    # =====================================================

    if usuario.perfil == "tae":

        tae = usuario.tae

        response.update({
            "matricula": tae.matricula,
            "email_institucional": tae.email_institucional,
            "cargo": tae.cargo,
            "setor": tae.setor,
            "campus": tae.campus
        })

        return response

    # =====================================================
    # ESTUDANTE
    # =====================================================

    if usuario.perfil == "estudante":

        estudante = usuario.estudante

        response.update({
            "matricula": estudante.matricula,
            "email_institucional": estudante.email_institucional,
            "curso": estudante.curso,
            "matriz": estudante.matriz,
            "ira": estudante.ira,
            "ano_ingresso": estudante.ano_ingresso
        })

        return response

    return response

@auth_router.post("/sincronizar")
async def sincronizar(
    dados: SincronizarRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(
        get_current_user
    )
):

    # =========================================
    # EXTERNO NÃO SINCRONIZA
    # =========================================

    if usuario.tipo_login == "cpf":
        return {
            "mensagem":
                "usuário externo não necessita sincronização"
        }

    # =========================================
    # LOGIN SUAP + SCRAPING
    # =========================================

    resultado = await autenticar_suap(
        usuario.login,
        dados.senha
    )

    # =========================================
    # FALHA SUAP
    # =========================================

    if not resultado["sucesso"]:
        raise Exception(
            "falha ao autenticar no SUAP"
        )

    # =========================================
    # DADOS NORMALIZADOS
    # =========================================

    dados_suap = resultado["dados"]

    print(dados_suap)

    # =========================================
    # SINCRONIZA BANCO
    # =========================================

    usuario = await sincronizar_usuario_suap(
        db,
        usuario,
        dados_suap
    )

    # =========================================
    # RETORNO
    # =========================================

    return {
        "mensagem":
            "dados sincronizados com sucesso"
    }
