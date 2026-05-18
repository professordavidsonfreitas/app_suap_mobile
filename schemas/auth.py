from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class LoginRequest(BaseModel):
    login: str
    senha: str


class RegistroExternoRequest(BaseModel):
    nome: str
    cpf: str
    email_pessoal: EmailStr
    telefone: Optional[str] = None
    senha: str = Field(
        min_length=6,
        max_length=72
    )
    nascimento: date

class UsuarioMeResponse(BaseModel):
    id: int
    nome: str
    perfil: str
    cpf: Optional[str]
    email_pessoal: Optional[str]
    telefone: Optional[str]
    class Config:
        from_attributes = True

class SincronizarRequest(
    BaseModel
):

    senha: str