import customtkinter as ctk

from models.usuario import Usuario
from views.ui_helpers import BG, MUTED, PRIMARY, TEXT


class MenuView(ctk.CTkFrame):
    def __init__(self, master, user: Usuario, actions: dict, on_logout):
        super().__init__(master, fg_color=BG)
        self.pack(fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Cafetería Don Quelo", text_color=PRIMARY,
            font=ctk.CTkFont(size=23, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=30, pady=22)
        user_badge = ctk.CTkFrame(header, fg_color="#E9EFF7", corner_radius=12)
        user_badge.grid(row=0, column=1, padx=(12, 18), pady=16)
        ctk.CTkLabel(
            user_badge, text=f"{user.nombre}  ·  {user.rol}", text_color=TEXT,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(padx=14, pady=8)
        ctk.CTkButton(
            header, text="Cerrar sesión", width=130, height=38, fg_color="#E9EFF7",
            text_color=TEXT, hover_color="#DCE6F2", command=on_logout,
        ).grid(row=0, column=2, padx=(0, 30), pady=16)

        body = ctk.CTkFrame(self, fg_color=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=34, pady=26)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(
            body, text=f"Hola, {user.nombre}", text_color=TEXT,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=4, pady=(2, 2))
        ctk.CTkLabel(
            body, text="¿Qué necesitas hacer hoy?", text_color=MUTED,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="nw", padx=4, pady=(0, 16))

        buttons = [
            ("Registrar reserva", "register", "Crear una reserva nueva"),
            ("Ver reservas", "view", "Consultar reservas registradas"),
            ("Modificar reserva", "edit", "Actualizar una reserva activa"),
            ("Cancelar reserva", "cancel", "Cancelar sin borrar el registro"),
            ("Eliminar reserva", "delete", "Eliminar permanentemente un registro"),
            ("Disponibilidad de mesas", "availability", "Consultar mesas por fecha y hora"),
            ("Historial", "history", "Consultar reservas pasadas"),
            ("Gestionar usuarios", "users", "Crear cuentas y asignar roles"),
        ]
        visible = [item for item in buttons if item[1] in actions]
        cards = ctk.CTkScrollableFrame(
            body, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#C5D1E0",
            scrollbar_button_hover_color="#9EADC0",
        )
        cards.grid(row=2, column=0, sticky="nsew")
        cards.grid_columnconfigure((0, 1), weight=1, uniform="action")
        for index, (label, action, subtitle) in enumerate(visible):
            row, col = divmod(index, 2)
            card = ctk.CTkFrame(
                cards, fg_color="white", corner_radius=16,
                border_width=1, border_color="#E3EAF2",
            )
            card.grid(row=row, column=col, sticky="ew", padx=8, pady=7)
            card.grid_columnconfigure(1, weight=1)
            ctk.CTkFrame(
                card, width=4, height=58, fg_color=PRIMARY, corner_radius=2,
            ).grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16)
            ctk.CTkLabel(
                card, text=label, text_color=TEXT,
                font=ctk.CTkFont(size=16, weight="bold"),
            ).grid(row=0, column=1, sticky="w", padx=(0, 12), pady=(16, 4))
            ctk.CTkLabel(
                card, text=subtitle, text_color=MUTED, anchor="w",
                wraplength=300, justify="left",
            ).grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 16))
            ctk.CTkButton(
                card, text="Abrir", width=92, height=36, fg_color=PRIMARY,
                hover_color="#194784", command=actions[action],
            ).grid(row=0, column=2, rowspan=2, padx=(4, 16), pady=16)
