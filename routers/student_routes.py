from fastapi import APIRouter # type: ignore

student_router = APIRouter(prefix="/estudante", tags=["estudante"])

@student_router.get("/")
async def estudante():
    """
    Dados do usuário logado
    """
    return {"mensagem": "você acessou o estudante"}