from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal

from schemas.app_version import AppVersionCreate

from services.app_version_service import obter_ultima_versao, criar_versao

from auth.dependences import get_current_admin

router = APIRouter(prefix="/app", tags=["App"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/version")
async def app_version(db: Session = Depends(get_db)):
    versao = await obter_ultima_versao(db)
    return versao

@router.post("/version")
async def criar_app_version(dados: AppVersionCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    nova_versao = await criar_versao(db, dados)
    return nova_versao  