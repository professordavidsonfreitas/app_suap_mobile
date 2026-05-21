from database import engine, Base
from models.usuario import Usuario, UsuarioEstudante, UsuarioProfessor, UsuarioTAE, UsuarioResponsavel, UsuarioExterno, CredencialSUAP
from models.app_version import AppVersion

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")