import customtkinter as ctk

from models.usuario import Usuario
from views.ui_helpers import BG, MUTED, PRIMARY, TEXT


class MenuView(ctk.CTkFrame):
    def __init__(self, master, user: Usuario, actions: dict, on_logout):
        super().__init__(master, fg_color=BG)
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=76)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Cafetería Don Quelo", text_color=PRIMARY,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=28, pady=20)
        ctk.CTkLabel(
            header, text=f"{user.nombre}  ·  {user.rol}", text_color=MUTED,
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, padx=20)
        ctk.CTkButton(
            header, text="Cerrar sesión", width=125, fg_color="#E9EFF7",
            text_color=TEXT, hover_color="#DCE6F2", command=on_logout,
        ).grid(row=0, column=2, padx=(0, 26), pady=16)

        body = ctk.CTkFrame(self, fg_color=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=36, pady=30)
        body.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(
            body, text="Panel principal", text_color=TEXT,
            font=ctk.CTkFont(size=26, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(5, 20))

        buttons = [
            ("Registrar reserva", "register", "Crear una reserva nueva"),
            ("Ver reservas", "view", "Consultar reservas registradas"),
            ("Modificar reserva", "edit", "Actualizar una reserva activa"),
            ("Cancelar reserva", "cancel", "Cancelar sin borrar el registro"),
            ("Disponibilidad de mesas", "availability", "Consultar mesas por fecha y hora"),
            ("Historial", "history", "Consultar reservas pasadas"),
            ("Gestionar usuarios", "users", "Crear cuentas y asignar roles"),
        ]
        visible = [item for item in buttons if item[1] in actions]
        for index, (label, action, subtitle) in enumerate(visible):
            row, col = divmod(index, 3)
            card = ctk.CTkFrame(body, fg_color="white", corner_radius=14)
            card.grid(row=row + 1, column=col, sticky="nsew", padx=8, pady=8)
            card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                card, text=label, text_color=TEXT,
                font=ctk.CTkFont(size=16, weight="bold"),
            ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 5))
            ctk.CTkLabel(
                card, text=subtitle, text_color=MUTED, anchor="w",
                wraplength=220, justify="left",
            ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 14))
            ctk.CTkButton(
                card, text="Abrir", height=38, fg_color=PRIMARY,
                command=actions[action],
            ).grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
