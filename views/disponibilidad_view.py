from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from controllers.mesa_controller import MesaController
from controllers.reserva_controller import ReservaController
from database.db_manager import DatabaseManager
from views.ui_helpers import BG, PRIMARY, configure_treeview, section_title


class DisponibilidadView(ctk.CTkToplevel):
    def __init__(self, master, database: DatabaseManager):
        super().__init__(master)
        self.controller = MesaController(database)
        self.title("Disponibilidad de mesas · Don Quelo")
        self.geometry("680x650")
        self.minsize(560, 500)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        section_title(self, "Disponibilidad de mesas").grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 12)
        )
        filters = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        filters.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.date_input = ctk.CTkEntry(filters, placeholder_text="AAAA-MM-DD", width=170)
        self.date_input.pack(side="left", padx=14, pady=14)
        self.date_input.insert(0, date.today().isoformat())
        self.time_input = ctk.CTkEntry(filters, placeholder_text="HH:MM", width=120)
        self.time_input.pack(side="left", padx=6, pady=14)
        self.time_input.insert(0, "18:00")
        ctk.CTkButton(
            filters, text="Consultar", fg_color=PRIMARY, command=self.refresh,
        ).pack(side="left", padx=10)
        panel = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        self.tree = configure_treeview(
            panel, ("numero", "capacidad", "ubicacion", "estado"),
            ("Número mesa", "Capacidad", "Ubicación", "Disponibilidad"),
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        self.refresh()
        self.transient(master)
        self.grab_set()

    def refresh(self):
        try:
            date_value = ReservaController.validate_date(self.date_input.get())
            time_value = ReservaController.validate_time(self.time_input.get())
            rows = self.controller.availability(date_value, time_value)
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert(
                    "", "end",
                    values=(
                        row["numero_mesa"], row["capacidad"],
                        row["ubicacion"], row["disponibilidad"],
                    ),
                    tags=(row["disponibilidad"],),
                )
            self.tree.tag_configure("Disponible", foreground="#087443")
            self.tree.tag_configure("Reservada", foreground="#B42318")
        except ValueError as exc:
            messagebox.showerror("Datos inválidos", str(exc), parent=self)
