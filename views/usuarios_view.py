import sqlite3
from tkinter import messagebox

import customtkinter as ctk

from database.db_manager import DatabaseManager
from models.usuario import ROLES
from views.ui_helpers import BG, MUTED, PRIMARY, configure_treeview, section_title


class UsuariosView(ctk.CTkToplevel):
    def __init__(self, master, database: DatabaseManager):
        super().__init__(master)
        self.database = database
        self.title("Gestionar usuarios · Don Quelo")
        self.geometry("720x580")
        self.minsize(600, 480)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        section_title(self, "Gestionar usuarios").grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 12)
        )
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.name = ctk.CTkEntry(form, placeholder_text="Nombre")
        self.username = ctk.CTkEntry(form, placeholder_text="Usuario")
        self.password = ctk.CTkEntry(form, placeholder_text="Contraseña", show="•")
        for column, entry in enumerate((self.name, self.username, self.password)):
            entry.grid(row=0, column=column, sticky="ew", padx=8, pady=(14, 8))
        self.role = ctk.CTkOptionMenu(form, values=list(ROLES), fg_color=PRIMARY)
        self.role.grid(row=0, column=3, sticky="ew", padx=8, pady=(14, 8))
        self.message = ctk.CTkLabel(form, text="", text_color="#B42318")
        self.message.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 8))
        ctk.CTkButton(
            form, text="Crear usuario", fg_color=PRIMARY, command=self.create,
        ).grid(row=1, column=3, sticky="ew", padx=8, pady=(0, 8))
        panel = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        self.tree = configure_treeview(
            panel, ("id", "nombre", "usuario", "rol"),
            ("ID", "Nombre", "Usuario", "Rol"),
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.refresh()
        self.transient(master)
        self.grab_set()

    def create(self):
        name, username, password = self.name.get().strip(), self.username.get().strip(), self.password.get()
        if not name or not username or not password:
            self.message.configure(text="Todos los campos son obligatorios.")
            return
        if len(password) < 6:
            self.message.configure(text="La contraseña debe tener al menos 6 caracteres.")
            return
        try:
            self.database.create_user(name, username, password, self.role.get())
            for entry in (self.name, self.username, self.password):
                entry.delete(0, "end")
            self.message.configure(text="Usuario creado correctamente.", text_color="#087443")
            self.refresh()
        except sqlite3.IntegrityError:
            self.message.configure(text="Ese nombre de usuario ya existe.", text_color="#B42318")
        except sqlite3.Error as exc:
            messagebox.showerror("Error de base de datos", str(exc), parent=self)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for user in self.database.list_users():
            self.tree.insert(
                "", "end", values=(
                    user["id_usuario"], user["nombre"], user["usuario"], user["rol"],
                )
            )
