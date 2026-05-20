from pydantic import BaseModel


class AppVersionCreate(BaseModel):

    versao: str
    build: int
    obrigatoria: bool = False
    apk_url: str
    descricao: str | None = None


class AppVersionResponse(BaseModel):

    versao: str
    build: int
    obrigatoria: bool
    apk_url: str
    descricao: str | None = None