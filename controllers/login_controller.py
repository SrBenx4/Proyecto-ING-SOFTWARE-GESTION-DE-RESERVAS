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
            remaining = self.database.get_lock_remaining(username)
            if remaining:
                minutes, seconds = divmod(remaining, 60)
                raise ValueError(
                    f"Cuenta bloqueada. Espere {minutes:02d}:{seconds:02d} minutos."
                )
            return None
        self.current_user = Usuario(**data)
        return self.current_user

    def lock_remaining(self, username: str) -> int:
        return self.database.get_lock_remaining(username)

    def logout(self) -> None:
        self.current_user = None
