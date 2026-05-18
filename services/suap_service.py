# Esse arquivo é responsável por lidar com a integração com o SUAP, como autenticação e obtenção de dados do usuário.
# Ele fará:
# 1. Autenticação do usuário no SUAP
# 2. Obtenção de dados do usuário autenticado
# 3. Buscar perfil do usuário no SUAP
# 4. Buscar Token
# 5. Scraping de dados adicionais do SUAP, se necessário


import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


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

def parse_suap_date(texto):

    if not texto:
        return None

    data = texto.split("\n")[0].strip()

    return datetime.strptime(
        data,
        "%d/%m/%Y"
    ).date()

def parse_setor_campus(texto):

    if not texto:

        return None, None

    texto = texto.strip()

    pattern = r"^(.*?)\s*\(campus:\s*(.*?)\)$"

    match = re.search(
        pattern,
        texto
    )

    if match:

        setor = match.group(1).strip()

        campus = match.group(2).strip()

        return setor, campus

    return texto, None

def normalize_server_profile(
    raw_data: dict
) -> dict:
    """
    Normaliza perfil de servidor.
    """

    setor, campus = parse_setor_campus(
        raw_data.get(
            "Setor SUAP"
        )
    )
    
    return {

    "tipo_perfil": "servidor",

    "matricula":
        raw_data.get("Matrícula"),

    "nome":
        raw_data.get("Nome Usual"),

    "cpf":
        raw_data.get("CPF"),

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

    "setor": setor,

    "campus": campus,

    "area_atuacao":
        raw_data.get(
            "Matéria/Disciplina Ingresso"
        )
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



async def autenticar_suap(
    login,
    senha
):

    # 1. Criar sessão HTTP persistente
    session = create_session()

    # 2. Baixar página de login para obter token CSRF
    html_login = fetch_login_page_SUAP(
        session
    )

    # 3. Extrair token CSRF da página de login
    csrf = extract_csrf_token(
        html_login
    )

    # 4. Realizar login com as credenciais e token CSRF
    resposta = perform_login(
        session,
        login,
        senha,
        csrf
    )

    # 5. Validar se o login foi bem-sucedido
    sucesso = validate_login(
        resposta
    )

    # 6. Se login falhou, retornar resposta de erro
    if not sucesso:

        return {
            "sucesso": False
        }

    # 7. Extrair URL do perfil do usuário
    profile_url = extract_profile_link(
        resposta
    )

    # 8. Detectar tipo estrutural do perfil (estudante, docente, tae)
    role = detect_role(
        profile_url
    )

    # 9. Baixar página do perfil
    html_profile = fetch_profile_page(
        session,
        profile_url
    )

    # 10. Extrair dados do perfil a partir da página (pares dt/dd)
    raw_data = extract_definition_list(
        html_profile
    )

    # =========================================
    # ESTUDANTE
    # =========================================

    # Se for estudante, normalizar dados e retornar resposta
    if role == "student":
        # Normalizar dados do perfil de estudante
        normalized = normalize_student_profile(
            raw_data
        )

        return {
            "sucesso": True,
            "dados": normalized
        }

    # =========================================
    # SERVIDOR
    # =========================================

    # Se for servidor, normalizar dados, detectar subtipo (docente/tae) e retornar resposta
    if role == "server":

        # Normalizar dados do perfil de servidor
        normalized = normalize_server_profile(
            raw_data
        )

        # Detectar subtipo de servidor (docente ou TAE)
        subtipo = detect_server_subrole(
            normalized
        )

        # Adicionar subtipo ao perfil normalizado
        normalized["subtipo_perfil"] = subtipo

        return {
            "sucesso": True,
            "dados": normalized
        }

    return {
        "sucesso": False
    }