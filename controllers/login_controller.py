from database.db_manager import DatabaseManager
from models.usuario import Usuario


class LoginController:
    def __init__(self, database: DatabaseManager):
        self.database = database
        self.current_user: Usuario | None = None

    def login(self, username: str, password: str) -> Usuario | None:
        if not username.strip() or not password:
            raise ValueError("Ingrese usuario y contraseña.")
        data = self.database.authenticate(username, password)
        if data is None:
            return None
        self.current_user = Usuario(**data)
        return self.current_user

    def logout(self) -> None:
        self.current_user = None
