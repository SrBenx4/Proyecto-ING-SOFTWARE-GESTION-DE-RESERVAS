import customtkinter as ctk

from controllers.login_controller import LoginController
from controllers.reserva_controller import ReservaController
from database.db_manager import DatabaseManager
from models.usuario import Usuario
from views.disponibilidad_view import DisponibilidadView
from views.historial_view import HistorialView
from views.login_view import LoginView
from views.menu_view import MenuView
from views.reservas_view import ReservasView
from views.usuarios_view import UsuariosView


class DonQueloApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Don Quelo · Gestión de reservas")
        self.geometry("920x680")
        self.minsize(760, 580)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.database = DatabaseManager()
        self.login_controller = LoginController(self.database)
        self.reservation_controller = ReservaController(self.database)
        self.login_view = LoginView(self, self.login_controller, self.show_menu)

    def show_menu(self, user: Usuario):
        self.login_view.destroy()
        self.menu_view = MenuView(self, user, self._actions_for(user), self.logout)

    def _open_reservations(self, user: Usuario, mode: str):
        ReservasView(self, self.database, user, mode, on_change=lambda: None)

    def _actions_for(self, user: Usuario) -> dict:
        actions = {
            "view": lambda: self._open_reservations(user, "view"),
            "availability": lambda: DisponibilidadView(self, self.database),
        }
        if user.rol in ("Administrador", "Garzon"):
            actions.update({
                "register": lambda: self._open_reservations(user, "register"),
                "edit": lambda: self._open_reservations(user, "edit"),
                "cancel": lambda: self._open_reservations(user, "cancel"),
            })
        if user.rol in ("Administrador", "Jefe"):
            actions["history"] = lambda: HistorialView(self, self.database)
        if user.rol == "Administrador":
            actions["users"] = lambda: UsuariosView(self, self.database)
        return actions

    def logout(self):
        self.login_controller.logout()
        self.menu_view.destroy()
        self.login_view = LoginView(self, self.login_controller, self.show_menu)


if __name__ == "__main__":
    DonQueloApp().mainloop()
