import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from controllers.login_controller import LoginController
from controllers.reserva_controller import ReservaController
from database.db_manager import DatabaseManager
from database.seed_test_data import seed_test_data


class DatabaseAndReservationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = DatabaseManager(Path(self.temp_dir.name) / "test.db")
        self.login = LoginController(self.database)
        self.reservations = ReservaController(self.database)
        self.admin = self.login.login("admin", "admin123")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initialization_creates_admin_and_twenty_tables(self):
        tables = self.database.list_tables()
        self.assertEqual(len(tables), 20)
        self.assertEqual(sum(table["ubicacion"] == "Salón" for table in tables), 6)
        self.assertEqual(sum(table["ubicacion"] == "Terraza" for table in tables), 14)
        self.assertEqual(self.database.authenticate("admin", "admin123")["rol"], "Administrador")
        self.assertIsNone(self.database.authenticate("admin", "incorrecta"))

    def test_required_fields_and_invalid_login_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "usuario y contraseña"):
            self.login.login("", "")
        with self.assertRaisesRegex(ValueError, "teléfono"):
            self.reservations.validate_fields("Cliente", "", "2")
        with self.assertRaisesRegex(ValueError, "AAAA-MM-DD"):
            self.reservations.validate_date("31/12/2030")
        with self.assertRaisesRegex(ValueError, "HH:MM"):
            self.reservations.validate_time("25:10")

    def test_create_reservation_checks_capacity_and_occupied_table(self):
        table = self.database.list_tables()[0]
        future = (date.today() + timedelta(days=1)).isoformat()
        self.reservations.create(
            self.admin, "Cliente Uno", "123456", future, "18:00", "2",
            table["id_mesa"], "",
        )
        available = self.reservations.available_tables(future, "18:00", 2)
        self.assertNotIn(table["id_mesa"], [row["id_mesa"] for row in available])
        with self.assertRaisesRegex(ValueError, "ya está reservada"):
            self.reservations.create(
                self.admin, "Cliente Dos", "654321", future, "18:00", "2",
                table["id_mesa"], "",
            )
        self.assertEqual(len(self.database.list_reservations()), 1)

    def test_cancel_keeps_record_and_releases_table(self):
        table = self.database.list_tables()[0]
        future = (date.today() + timedelta(days=1)).isoformat()
        self.reservations.create(
            self.admin, "Cliente", "123456", future, "17:00", "2",
            table["id_mesa"], "",
        )
        reservation = self.database.list_reservations()[0]
        self.database.cancel_reservation(reservation["id_reserva"])
        self.assertEqual(self.database.list_reservations()[0]["estado"], "Cancelada")
        self.assertIn(
            table["id_mesa"],
            [row["id_mesa"] for row in self.reservations.available_tables(future, "17:00", 2)],
        )

    def test_history_can_filter_past_dates(self):
        rows = self.reservations.reservations(date="2000-01-01", past_only=True)
        self.assertEqual(rows, [])

    def test_sample_data_script_is_idempotent(self):
        seed_test_data(self.database)
        first_count = len(self.database.list_reservations())
        seed_test_data(self.database)
        self.assertEqual(first_count, 3)
        self.assertEqual(len(self.database.list_reservations()), 3)
        self.assertIsNotNone(self.database.authenticate("jefe", "jefe123"))


if __name__ == "__main__":
    unittest.main()
