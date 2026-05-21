from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from sqlalchemy.orm import Session

from database import SessionLocal

from utils.jwt import validar_token

from models.usuario import Usuario


security = HTTPBearer()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


async def get_current_user(

    credenciais: HTTPAuthorizationCredentials = Depends(security),

    db: Session = Depends(get_db)
):
    token = credenciais.credentials
    
    payload = validar_token(token)

    if not payload:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token inválido"
        )

    login = payload.get("sub")

    usuario = db.query(Usuario).filter(
        Usuario.login == login
    ).first()

    if not usuario:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="usuário não encontrado"
        )

    return usuario

async def get_current_admin(
    usuario: Usuario = Depends(get_current_user)
):
    if not usuario.admin:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="acesso negado"
        )

    return usuario