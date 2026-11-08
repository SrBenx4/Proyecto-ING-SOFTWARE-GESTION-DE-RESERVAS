from datetime import datetime

from database.db_manager import DatabaseManager
from models.usuario import Usuario


class ReservaController:
    def __init__(self, database: DatabaseManager):
        self.database = database

    @staticmethod
    def validate_date(value: str) -> str:
        try:
            parsed = datetime.strptime(value.strip(), "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("La fecha debe ser válida y usar el formato AAAA-MM-DD.") from exc
        if parsed.strftime("%Y-%m-%d") != value.strip():
            raise ValueError("La fecha debe usar el formato AAAA-MM-DD.")
        if parsed.date() < datetime.now().date():
            raise ValueError("No se pueden registrar reservas en fechas pasadas.")
        return value.strip()

    @staticmethod
    def validate_time(value: str) -> str:
        try:
            parsed = datetime.strptime(value.strip(), "%H:%M")
        except ValueError as exc:
            raise ValueError("La hora debe ser válida y usar el formato HH:MM.") from exc
        if parsed.strftime("%H:%M") != value.strip():
            raise ValueError("La hora debe usar el formato HH:MM.")
        return value.strip()

    @staticmethod
    def validate_fields(name: str, phone: str, people: str) -> int:
        if not name.strip():
            raise ValueError("El nombre del cliente es obligatorio.")
        if not phone.strip():
            raise ValueError("El teléfono es obligatorio.")
        try:
            count = int(people)
        except (ValueError, TypeError) as exc:
            raise ValueError("La cantidad de personas debe ser un número entero.") from exc
        if count < 1:
            raise ValueError("La cantidad de personas debe ser al menos 1.")
        return count

    def available_tables(
        self, date: str, time: str, people: int, exclude_reservation_id: int | None = None
    ) -> list[dict]:
        date = self.validate_date(date)
        time = self.validate_time(time)
        return self.database.get_available_tables(date, time, people, exclude_reservation_id)

    def create(
        self, user: Usuario, name: str, phone: str, date: str, time: str,
        people: str, table_id: int, notes: str,
    ) -> int:
        count = self.validate_fields(name, phone, people)
        date = self.validate_date(date)
        time = self.validate_time(time)
        return self.database.create_reservation(
            name, phone, user.id_usuario, table_id, date, time, count, notes
        )

    def update(
        self, reservation_id: int, name: str, phone: str, date: str, time: str,
        people: str, table_id: int, notes: str,
    ) -> None:
        count = self.validate_fields(name, phone, people)
        self.database.update_reservation(
            reservation_id, name, phone, table_id,
            self.validate_date(date), self.validate_time(time), count, notes,
        )

    def reservations(
        self, date: str = "", customer: str = "", state: str = "", past_only: bool = False
    ) -> list[dict]:
        if date:
            try:
                parsed = datetime.strptime(date.strip(), "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("La fecha debe ser válida y usar el formato AAAA-MM-DD.") from exc
            if parsed.strftime("%Y-%m-%d") != date.strip():
                raise ValueError("La fecha debe usar el formato AAAA-MM-DD.")
        return self.database.list_reservations(date, customer, state, past_only)
