import customtkinter as ctk

from controllers.login_controller import LoginController
from views.ui_helpers import BG, MUTED, PRIMARY, TEXT


class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller: LoginController, on_success):
        super().__init__(master, fg_color=BG)
        self.controller = controller
        self.on_success = on_success
        self.pack(fill="both", expand=True)

        panel = ctk.CTkFrame(self, width=440, corner_radius=18, fg_color="white")
        panel.place(relx=0.5, rely=0.5, anchor="center")
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Don Quelo", text_color=PRIMARY,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, padx=38, pady=(36, 4))
        ctk.CTkLabel(
            panel, text="Sistema de Gestión de Reservas", text_color=MUTED,
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, padx=30, pady=(0, 24))

        self.username = ctk.CTkEntry(panel, width=340, height=42, placeholder_text="Usuario")
        self.username.grid(row=2, column=0, padx=38, pady=8)
        self.password = ctk.CTkEntry(
            panel, width=340, height=42, placeholder_text="Contraseña", show="•"
        )
        self.password.grid(row=3, column=0, padx=38, pady=8)
        self.password.bind("<Return>", lambda _event: self.submit())
        self.message = ctk.CTkLabel(panel, text="", text_color="#B42318", wraplength=330)
        self.message.grid(row=4, column=0, padx=25, pady=(4, 0))
        ctk.CTkButton(
            panel, text="Iniciar sesión", height=44, width=340,
            fg_color=PRIMARY, hover_color="#194784", command=self.submit,
        ).grid(row=5, column=0, padx=38, pady=(14, 34))
        self.username.focus_set()

    def submit(self):
        try:
            user = self.controller.login(self.username.get(), self.password.get())
            if user is None:
                self.message.configure(text="Usuario o contraseña incorrectos.")
                return
            self.on_success(user)
        except ValueError as exc:
            self.message.configure(text=str(exc))
