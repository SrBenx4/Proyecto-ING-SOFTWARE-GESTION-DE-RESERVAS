from datetime import date, timedelta

from database.db_manager import DatabaseManager


def seed_test_data(database: DatabaseManager) -> None:
    existing_users = {row["usuario"] for row in database.list_users()}
    if "garzon" not in existing_users:
        database.create_user("Garzón de prueba", "garzon", "garzon123", "Garzon")
    if "jefe" not in existing_users:
        database.create_user("Jefe de prueba", "jefe", "jefe123", "Jefe")

    with database.connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM reservas").fetchone()[0]
    # Keep reruns safe and avoid mixing demo fixtures with a live reservation set.
    if count:
        return

    waiter = database.authenticate("garzon", "garzon123")
    if waiter is None:
        raise RuntimeError("No fue posible obtener el usuario de prueba Garzon.")
    samples = (
        ("Camila Rojas", "+56911112222", 1, date.today() + timedelta(days=1), "12:00", 2),
        ("Diego Pérez", "+56933334444", 7, date.today() + timedelta(days=2), "18:30", 6),
        ("Antonia Silva", "+56955556666", 4, date.today() + timedelta(days=3), "20:00", 4),
    )
    for name, phone, table_number, reservation_date, time, people in samples:
        table = next(
            item for item in database.list_tables()
            if item["numero_mesa"] == table_number
        )
        database.create_reservation(
            name, phone, waiter["id_usuario"], table["id_mesa"],
            reservation_date.isoformat(), time, people, "Reserva de demostración",
        )


def main() -> None:
    seed_test_data(DatabaseManager())
    print("Datos de prueba listos. Usuario: garzon / garzon123; jefe / jefe123")


if __name__ == "__main__":
    main()
