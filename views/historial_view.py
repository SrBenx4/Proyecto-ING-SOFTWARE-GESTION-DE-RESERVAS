from tkinter import messagebox

import customtkinter as ctk

from controllers.reserva_controller import ReservaController
from database.db_manager import DatabaseManager
from views.ui_helpers import BG, PRIMARY, configure_treeview, section_title


class HistorialView(ctk.CTkToplevel):
    def __init__(self, master, database: DatabaseManager):
        super().__init__(master)
        self.controller = ReservaController(database)
        self.title("Historial · Don Quelo")
        self.geometry("1100x680")
        self.minsize(900, 550)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        section_title(self, "Historial de reservas").grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 12)
        )
        filters = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        filters.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.date_input = ctk.CTkEntry(filters, width=150, placeholder_text="Fecha AAAA-MM-DD")
        self.date_input.pack(side="left", padx=(14, 6), pady=14)
        self.customer_input = ctk.CTkEntry(filters, width=190, placeholder_text="Cliente")
        self.customer_input.pack(side="left", padx=6, pady=14)
        self.state_filter = ctk.CTkOptionMenu(
            filters, values=["Todos", "Activa", "Cancelada", "Completada"],
            fg_color=PRIMARY, button_color=PRIMARY, width=130,
        )
        self.state_filter.pack(side="left", padx=6, pady=14)
        self.state_filter.set("Todos")
        ctk.CTkButton(
            filters, text="Filtrar", fg_color=PRIMARY, command=self.refresh,
        ).pack(side="left", padx=8)
        panel = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        panel.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 24))
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        self.tree = configure_treeview(
            panel,
            ("id", "cliente", "telefono", "mesa", "fecha", "hora", "personas", "estado", "responsable"),
            ("ID", "Cliente", "Teléfono", "Mesa", "Fecha", "Hora", "Personas", "Estado", "Garzón responsable"),
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.refresh()
        self.transient(master)
        self.grab_set()

    def refresh(self):
        try:
            rows = self.controller.reservations(
                date=self.date_input.get().strip(),
                customer=self.customer_input.get(),
                state=self.state_filter.get(),
                past_only=True,
            )
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in rows:
                self.tree.insert(
                    "", "end",
                    values=(
                        row["id_reserva"], row["cliente"], row["telefono"],
                        f"Mesa {row['numero_mesa']}", row["fecha"], row["hora"],
                        row["cantidad_personas"], row["estado"], row["responsable"],
                    ),
                )
        except ValueError as exc:
            messagebox.showerror("Filtro inválido", str(exc), parent=self)
