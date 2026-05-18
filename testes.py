import requests
from bs4 import BeautifulSoup

BASE_URL = "https://suap.ifgoiano.edu.br"


#Função create_session(): criar um client HTTP persistente usando requests.Session() para manter cookies e sessões entre requisições.
# Na prática: simula uma aba do navegador, permitindo que o usuário faça login e mantenha a sessão ativa para acessar outras páginas do SUAP sem precisar autenticar novamente a cada requisição.
def create_session() -> requests.Session:
    """
    Cria uma sessão HTTP persistente.
    """

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    })

    return session

def fetch_login_page_SUAP(
        session: requests.Session
        ) -> str:
    """Baixa a página de login para obter cookies e tokens necessários."""
    
    login_url = f"{BASE_URL}/accounts/login/"

    response = session.get(
        login_url,
        timeout=30
    )

    return response.text

def extract_csrf_token(html: str) -> str:
    """Extrai o token CSRF da página de login."""
    
    soup = BeautifulSoup(html, "html.parser")

    csrf_input = soup.find(
        "input",
        {"name": "csrfmiddlewaretoken"}
    )

    if not csrf_input:
        raise Exception("Token CSRF não encontrado na página de login.")

    return csrf_input["value"]

def perform_login(
        session: requests.Session,
        usuario: str,
        senha: str,
        csrf_token: str
        ) -> str:
    """Realiza o login no SUAP usando as credenciais fornecidas."""
    
    login_url = f"{BASE_URL}/accounts/login/"

    payload = {
        "username": usuario,
        "password": senha,
        "csrfmiddlewaretoken": csrf_token
    }

    headers = {
        "Referer": login_url
    }

    response = session.post(
        login_url,
        data=payload,
        headers=headers,
        timeout=30,
        allow_redirects=True
    )

    return response.text

def validate_login(html: str) -> bool:
    """Valida se o login foi bem-sucedido verificando a presença de elementos específicos na página."""
    return "user-profile" in html 


def extract_profile_link(
    html: str
) -> str:
    """
    Extrai URL do perfil.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    profile = soup.select_one(
        "a.user-profile"
    )

    if not profile:
        raise Exception(
            "Perfil não encontrado"
        )

    return profile["href"]


def detect_role(
    profile_url: str
) -> str:
    """
    Detecta tipo estrutural do perfil.
    """

    if "/edu/aluno/" in profile_url:
        return "student"

    if "/rh/servidor/" in profile_url:
        return "server"

    return "unknown"

def fetch_profile_page(
    session: requests.Session,
    profile_url: str
) -> str:
    """
    Baixa página do perfil.
    """

    full_url = BASE_URL + profile_url

    response = session.get(
        full_url,
        timeout=30
    )

    return response.text

def extract_definition_list(
    html: str
) -> dict:
    """
    Extrai pares dt/dd do HTML.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    data = {}

    items = soup.select(
        "dl.definition-list div.list-item"
    )

    for item in items:

        dt = item.find("dt")
        dd = item.find("dd")

        if not dt or not dd:
            continue

        key = dt.get_text(
            strip=True
        )

        value = dd.get_text(
            " ",
            strip=True
        )

        data[key] = value

    return data


def normalize_server_profile(
    raw_data: dict
) -> dict:
    """
    Normaliza perfil de servidor.
    """

    return {
        "tipo_perfil": "servidor",

        "matricula":
            raw_data.get("Matrícula"),

        "nome":
            raw_data.get("Nome Usual"),

        "cpf":
            raw_data.get("CPF"),

        "data_nascimento":
            raw_data.get("Nascimento"),

        "email_pessoal":
            raw_data.get("E-mail SIAPE"),

        "email_institucional":
            raw_data.get(
                "E-mail Institucional"
            ),

        "telefone":
            raw_data.get(
                "Telefones Pessoais"
            ),

        "cargo":
            raw_data.get("Cargo"),

        "setor":
            raw_data.get(
                "Setor SUAP"
            ),

        "area": 
            raw_data.get(
                "Matéria/Disciplina Ingresso"
            ),
    }


def normalize_student_profile(
    raw_data: dict
) -> dict:
    """
    Normaliza perfil de estudante.
    """

    return {
        "tipo_perfil": "estudante",

        "matricula":
            raw_data.get("Matrícula"),

        "nome":
            raw_data.get("Nome"),

        "cpf":
            raw_data.get("CPF"),

        "email_institucional":
            raw_data.get(
                "E-mail Acadêmico"
            ),

        "curso":
            raw_data.get("Curso"),

        "matriz":
            raw_data.get("Matriz"),

        "ira":
            raw_data.get("I.R.A."),

        "ano_ingresso":
            raw_data.get(
                "Ano de Ingresso"
            ),
    }

def detect_server_subrole(
    normalized_data: dict
) -> str:
    """
    Detecta se servidor é docente ou TAE.
    """

    cargo = (
        normalized_data.get(
            "cargo",
            ""
        )
        .upper()
    )

    if "PROFESSOR" in cargo:
        return "docente"

    return "tae"


def main():

    usuario = input("Usuário: ")
    senha = input("Senha: ")

    # 1. Criar sessão HTTP
    session = create_session()

    print("Sessão criada.")

    # 2. Baixar página de login
    login_html = fetch_login_page_SUAP(
        session
    )

    print("Página de login carregada.")

    # 3. Extrair CSRF token
    csrf_token = extract_csrf_token(
        login_html
    )

    print("CSRF token extraído.")

    # 4. Realizar login
    home_html = perform_login(
        session,
        usuario,
        senha,
        csrf_token
    )

    print("Login enviado.")

    # 5. Validar login
    if not validate_login(home_html):
        raise Exception(
            "Falha no login."
        )

    print("Login validado.")

    # 6. Extrair URL do perfil
    profile_url = extract_profile_link(
        home_html
    )

    print(f"URL do perfil: {profile_url}")

    # 7. Detectar tipo estrutural
    role = detect_role(profile_url)

    print(f"Tipo estrutural: {role}")

    # 8. Baixar página do perfil
    profile_html = fetch_profile_page(
        session,
        profile_url
    )

    print("Página do perfil carregada.")

    # 9. Extrair dados brutos
    raw_data = extract_definition_list(
        profile_html
    )

    print("\n=== DADOS BRUTOS ===")
    print(raw_data)

    # 10. Normalizar perfil
    if role == "student":

        perfil = normalize_student_profile(
            raw_data
        )

    elif role == "server":

        perfil = normalize_server_profile(
            raw_data
        )

        # Detectar subtipo
        subrole = detect_server_subrole(
            perfil
        )

        perfil["subtipo_perfil"] = subrole

    else:
        raise Exception(
            "Tipo de perfil desconhecido."
        )

    # Resultado final
    print("\n=== PERFIL NORMALIZADO ===")
    print(perfil)



if __name__ == "__main__":
    main()