import customtkinter as ctk

from controllers.login_controller import LoginController
from views.ui_helpers import BG, MUTED, PRIMARY, TEXT


class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller: LoginController, on_success):
        super().__init__(master, fg_color=BG)
        self.controller = controller
        self.on_success = on_success
        self.lock_after_id = None
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
        password_frame = ctk.CTkFrame(panel, fg_color="transparent")
        password_frame.grid(row=3, column=0, padx=38, pady=8, sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)
        self.password = ctk.CTkEntry(
            password_frame, height=42, placeholder_text="Contraseña", show="•"
        )
        self.password.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.password_visible = False
        self.toggle_password_button = ctk.CTkButton(
            password_frame, text="Ver", width=54, height=42,
            fg_color="#E9EFF7", text_color=TEXT, hover_color="#DCE6F2",
            command=self.toggle_password_visibility,
        )
        self.toggle_password_button.grid(row=0, column=1)
        self.password.bind("<Return>", lambda _event: self.submit())
        self.message = ctk.CTkLabel(panel, text="", text_color="#B42318", wraplength=330)
        self.message.grid(row=4, column=0, padx=25, pady=(4, 0))
        ctk.CTkButton(
            panel, text="Iniciar sesión", height=44, width=340,
            fg_color=PRIMARY, hover_color="#194784", command=self.submit,
        ).grid(row=5, column=0, padx=38, pady=(14, 34))
        self.username.focus_set()

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.password.configure(show="" if self.password_visible else "•")
        self.toggle_password_button.configure(
            text="Ocultar" if self.password_visible else "Ver"
        )

    def submit(self):
        try:
            user = self.controller.login(self.username.get(), self.password.get())
            if user is None:
                self.message.configure(text="Usuario o contraseña incorrectos.")
                return
            if self.lock_after_id is not None:
                self.after_cancel(self.lock_after_id)
                self.lock_after_id = None
            self.on_success(user)
        except ValueError as exc:
            self.message.configure(text=str(exc))
            username = self.username.get().strip()
            if self.controller.lock_remaining(username) > 0:
                self._update_lock_countdown(username)

    def _update_lock_countdown(self, username: str):
        remaining = self.controller.lock_remaining(username)
        if remaining <= 0:
            self.lock_after_id = None
            self.message.configure(text="Puede intentar iniciar sesión nuevamente.")
            return
        minutes, seconds = divmod(remaining, 60)
        self.message.configure(
            text=f"Cuenta bloqueada. Intente nuevamente en {minutes:02d}:{seconds:02d}."
        )
        self.lock_after_id = self.after(
            1000, lambda: self._update_lock_countdown(username)
        )
