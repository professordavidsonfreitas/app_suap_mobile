from datetime import (datetime, timedelta)

from jose import jwt


SECRET_KEY = "SUA_CHAVE_SUPER_SECRETA"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 1140


def gerar_token(dados: dict):
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    dados_copia.update({
        "exp": expiracao
    })

    token = jwt.encode(
        dados_copia,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def validar_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.JWTError:
        return None