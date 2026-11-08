from datetime import date
import sqlite3
from tkinter import messagebox

import customtkinter as ctk

from controllers.reserva_controller import ReservaController
from database.db_manager import DatabaseManager
from models.usuario import Usuario
from views.ui_helpers import BG, MUTED, PRIMARY, TEXT, configure_treeview, section_title


class ReservasView(ctk.CTkToplevel):
    def __init__(
        self, master, database: DatabaseManager, user: Usuario, mode: str = "view",
        on_change=None,
    ):
        super().__init__(master)
        self.database = database
        self.controller = ReservaController(database)
        self.user = user
        self.mode = mode
        self.on_change = on_change or (lambda: None)
        self.editing_id: int | None = None
        self.table_options: dict[str, int] = {}
        self.title("Reservas · Don Quelo")
        self.geometry("1120x760")
        self.minsize(940, 650)
        self.configure(fg_color=BG)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        section_title(self, self._title_for_mode()).grid(
            row=0, column=0, sticky="w", padx=24, pady=(20, 10)
        )
        if mode in ("register", "edit"):
            self._build_form()
        self._build_list()
        self.refresh()
        self.transient(master)
        self.grab_set()

    def _title_for_mode(self):
        return {
            "register": "Registrar reserva",
            "edit": "Modificar reserva",
            "cancel": "Cancelar reserva",
        }.get(self.mode, "Reservas")

    def _build_form(self):
        form = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        for col in range(4):
            form.grid_columnconfigure(col, weight=1)
        fields = (
            ("Cliente", "name", "Nombre completo"),
            ("Teléfono", "phone", "Teléfono"),
            ("Fecha", "date", "AAAA-MM-DD"),
            ("Hora", "time", "HH:MM"),
            ("Personas", "people", "Cantidad"),
            ("Observaciones", "notes", "Observaciones"),
        )
        self.inputs = {}
        for index, (label, key, placeholder) in enumerate(fields):
            row, col = divmod(index, 3)
            cell = ctk.CTkFrame(form, fg_color="transparent")
            cell.grid(row=row, column=col, sticky="ew", padx=10, pady=(12 if row == 0 else 6, 4))
            cell.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(cell, text=label, text_color=MUTED, anchor="w").grid(
                row=0, column=0, sticky="w", pady=(0, 4)
            )
            entry = ctk.CTkEntry(cell, height=36, placeholder_text=placeholder)
            entry.grid(row=1, column=0, sticky="ew")
            self.inputs[key] = entry
        self.inputs["date"].insert(0, date.today().isoformat())
        self.inputs["time"].insert(0, "18:00")
        self.inputs["people"].insert(0, "2")
        self.inputs["date"].bind("<FocusOut>", lambda _event: self.refresh_tables())
        self.inputs["time"].bind("<FocusOut>", lambda _event: self.refresh_tables())
        self.inputs["people"].bind("<FocusOut>", lambda _event: self.refresh_tables())

        table_cell = ctk.CTkFrame(form, fg_color="transparent")
        table_cell.grid(row=2, column=0, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(table_cell, text="Mesa disponible", text_color=MUTED, anchor="w").pack(
            anchor="w", pady=(0, 4)
        )
        self.table_menu = ctk.CTkOptionMenu(
            table_cell, values=["Seleccione fecha, hora y personas"],
            fg_color=PRIMARY, button_color=PRIMARY, height=36,
        )
        self.table_menu.pack(fill="x")
        self.table_menu.set("Seleccione fecha, hora y personas")

        self.form_message = ctk.CTkLabel(form, text="", text_color="#B42318", anchor="w")
        self.form_message.grid(row=2, column=1, columnspan=2, sticky="ew", padx=12)
        self.save_button = ctk.CTkButton(
            form, text="Guardar reserva", height=38, fg_color=PRIMARY,
            command=self.save,
        )
        self.save_button.grid(row=2, column=3, sticky="ew", padx=10, pady=10)

    def _build_list(self):
        panel = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        panel.grid(
            row=2 if self.mode in ("register", "edit") else 1,
            column=0, sticky="nsew", padx=24, pady=(0, 24),
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        toolbar = ctk.CTkFrame(panel, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        self.filter_date = ctk.CTkEntry(toolbar, width=145, placeholder_text="Fecha AAAA-MM-DD")
        self.filter_date.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            toolbar, text="Filtrar", width=85, height=34, fg_color=PRIMARY,
            command=self.refresh,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            toolbar, text="Todas", width=85, height=34, fg_color="#E9EFF7",
            text_color=TEXT, command=lambda: (self.filter_date.delete(0, "end"), self.refresh()),
        ).pack(side="left", padx=4)
        self.tree = configure_treeview(
            panel,
            ("id", "cliente", "telefono", "mesa", "fecha", "hora", "personas", "estado", "responsable"),
            ("ID", "Cliente", "Teléfono", "Mesa", "Fecha", "Hora", "Personas", "Estado", "Responsable"),
        )
        self.tree.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.tree.column("id", width=48)
        self.tree.column("cliente", width=150)
        self.tree.column("telefono", width=110)
        self.tree.column("responsable", width=150)
        if self.mode in ("edit", "cancel"):
            action_text = "Cargar seleccionada" if self.mode == "edit" else "Cancelar seleccionada"
            ctk.CTkButton(
                panel, text=action_text, height=38, fg_color=PRIMARY,
                command=self.selected_action,
            ).grid(row=2, column=0, sticky="e", padx=12, pady=(0, 12))

    def refresh_tables(self):
        try:
            count = int(self.inputs["people"].get())
            available = self.controller.available_tables(
                self.inputs["date"].get(), self.inputs["time"].get(), count,
                self.editing_id,
            )
            self.table_options = {
                f"Mesa {row['numero_mesa']} · {row['capacidad']} pers. · {row['ubicacion']}":
                    row["id_mesa"]
                for row in available
            }
            options = list(self.table_options) or ["Sin mesas disponibles"]
            self.table_menu.configure(values=options)
            self.table_menu.set(options[0])
            self.form_message.configure(
                text="" if self.table_options else "No hay mesas compatibles y disponibles."
            )
        except ValueError as exc:
            self.table_options = {}
            self.table_menu.configure(values=["Revise los datos ingresados"])
            self.table_menu.set("Revise los datos ingresados")
            self.form_message.configure(text=str(exc))

    def refresh(self):
        try:
            date_filter = self.filter_date.get().strip()
            rows = self.controller.reservations(date=date_filter)
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

    def save(self):
        try:
            label = self.table_menu.get()
            table_id = self.table_options.get(label)
            if table_id is None:
                raise ValueError("Seleccione una mesa disponible.")
            values = (
                self.inputs["name"].get(), self.inputs["phone"].get(),
                self.inputs["date"].get(), self.inputs["time"].get(),
                self.inputs["people"].get(), table_id, self.inputs["notes"].get(),
            )
            if self.editing_id is None:
                self.controller.create(self.user, *values)
                message = "La reserva se registró correctamente."
            else:
                self.controller.update(self.editing_id, *values)
                message = "La reserva se modificó correctamente."
            messagebox.showinfo("Don Quelo", message, parent=self)
            self._clear_form()
            self.refresh()
            self.on_change()
        except (ValueError, sqlite3.Error) as exc:
            self.form_message.configure(text=str(exc))

    def _clear_form(self):
        self.editing_id = None
        for key in ("name", "phone", "notes"):
            self.inputs[key].delete(0, "end")
        self.inputs["date"].delete(0, "end")
        self.inputs["date"].insert(0, date.today().isoformat())
        self.inputs["time"].delete(0, "end")
        self.inputs["time"].insert(0, "18:00")
        self.inputs["people"].delete(0, "end")
        self.inputs["people"].insert(0, "2")
        self.save_button.configure(text="Guardar reserva")
        self.refresh_tables()

    def selected_action(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Reservas", "Seleccione una reserva de la tabla.", parent=self)
            return
        reservation_id = int(self.tree.item(selection[0], "values")[0])
        rows = self.controller.reservations()
        row = next(item for item in rows if item["id_reserva"] == reservation_id)
        if self.mode == "cancel":
            if not messagebox.askyesno(
                "Cancelar reserva", f"¿Cancelar la reserva #{reservation_id}?",
                parent=self,
            ):
                return
            try:
                self.database.cancel_reservation(reservation_id)
                self.refresh()
                self.on_change()
            except ValueError as exc:
                messagebox.showerror("No se pudo cancelar", str(exc), parent=self)
            return
        if row["estado"] != "Activa":
            messagebox.showwarning("Reservas", "Solo se pueden modificar reservas activas.", parent=self)
            return
        self.editing_id = reservation_id
        for key, value in (
            ("name", row["cliente"]), ("phone", row["telefono"]),
            ("date", row["fecha"]), ("time", row["hora"]),
            ("people", str(row["cantidad_personas"])), ("notes", row["observaciones"]),
        ):
            self.inputs[key].delete(0, "end")
            self.inputs[key].insert(0, value)
        self.save_button.configure(text="Guardar cambios")
        self.refresh_tables()
        desired = next(
            (
                label for label, table_id in self.table_options.items()
                if table_id == next(
                    table["id_mesa"] for table in self.database.list_tables()
                    if table["numero_mesa"] == row["numero_mesa"]
                )
            ),
            None,
        )
        if desired:
            self.table_menu.set(desired)
