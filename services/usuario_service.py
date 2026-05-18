# Esse arquivo é responsável por lidar com a integração com o SUAP, como autenticação e obtenção de dados do usuário.
# Ele fará:
# 1. Autenticação do usuário no SUAP
# 2. Obtenção de dados do usuário autenticado
# 3. Buscar perfil do usuário no SUAP
# 4. Buscar Token
# 5. Scraping de dados adicionais do SUAP, se necessário





async def autenticar_usuario_suap(
    login: str,
    senha: str
):
    # =====================================================
    # AQUI VAI A LÓGICA DE AUTENTICAÇÃO COM O SUAP
    # =====================================================

    

    if login == "2025101102340005":

        return {

            "sucesso": True,

            "perfil": "estudante",

            "nome": "Aluno Teste",

            "cpf": "12345678900",

            "email": "aluno@ifgoiano.edu.br"
        }

    # Exemplo de resposta simulada
    return {
        "usuario": {
            "login": login,
            "nome": "Usuário SUAP",
            "perfil": "estudante"
        },
        "token": "token_simulado_suap"
    }