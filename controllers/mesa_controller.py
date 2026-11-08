from database.db_manager import DatabaseManager
from controllers.reserva_controller import ReservaController


class MesaController:
    def __init__(self, database: DatabaseManager):
        self.database = database

    def availability(self, date: str, time: str) -> list[dict]:
        date = ReservaController.validate_date(date)
        time = ReservaController.validate_time(time)
        tables = self.database.list_tables()
        available_ids = {
            table["id_mesa"]
            for table in self.database.get_available_tables(date, time, 1)
        }
        return [
            {
                **table,
                "disponibilidad": "Disponible" if table["id_mesa"] in available_ids else "Reservada",
            }
            for table in tables
        ]
