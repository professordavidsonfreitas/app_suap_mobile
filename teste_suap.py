import asyncio
from datetime import datetime

from services.suap_service import (
    autenticar_suap
)


async def main():

    resultado = await autenticar_suap(
        "2025101102340005",
        "O19k8m18!@"
    )

    print(resultado)


hora_criacao = datetime.now()
asyncio.run(main())
hora_depois = datetime.now()
print(f"Tempo total: {hora_depois - hora_criacao}")