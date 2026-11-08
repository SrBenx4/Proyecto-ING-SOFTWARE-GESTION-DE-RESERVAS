import hashlib
import hmac
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DEFAULT_DB_PATH = Path(__file__).with_name("database.db")
MESES_INICIALES = (
    (1, 2, "Salón"), (2, 2, "Salón"), (3, 2, "Salón"),
    (4, 4, "Salón"), (5, 4, "Salón"), (6, 4, "Salón"),
    (7, 8, "Terraza"), (8, 8, "Terraza"),
    (9, 2, "Terraza"), (10, 2, "Terraza"), (11, 2, "Terraza"),
    (12, 6, "Terraza"), (13, 6, "Terraza"), (14, 6, "Terraza"),
    (15, 6, "Terraza"), (16, 6, "Terraza"),
    (17, 4, "Terraza"), (18, 4, "Terraza"),
    (19, 4, "Terraza"), (20, 4, "Terraza"),
)


def hash_password(password: str) -> str:
    # PBKDF2 with a per-password random salt keeps credentials out of plaintext storage.
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)
    return f"pbkdf2_sha256${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, salt_hex, digest_hex = stored.split("$", 2)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 310_000
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


class DatabaseManager:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_database(self) -> None:
        with self.connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL CHECK (rol IN ('Administrador', 'Garzon', 'Jefe'))
                );
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mesas (
                    id_mesa INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_mesa INTEGER NOT NULL UNIQUE,
                    capacidad INTEGER NOT NULL CHECK (capacidad > 0),
                    ubicacion TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reservas (
                    id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
                    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
                    id_mesa INTEGER NOT NULL REFERENCES mesas(id_mesa),
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    cantidad_personas INTEGER NOT NULL CHECK (cantidad_personas > 0),
                    estado TEXT NOT NULL CHECK (estado IN ('Activa', 'Cancelada', 'Completada')),
                    observaciones TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_reservas_fecha_hora_estado
                    ON reservas(fecha, hora, estado);
                CREATE INDEX IF NOT EXISTS idx_reservas_cliente ON reservas(id_cliente);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_reserva_mesa_horario_activo
                    ON reservas(id_mesa, fecha, hora) WHERE estado = 'Activa';
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                ("Administrador", "admin", hash_password("admin123"), "Administrador"),
            )
            conn.executemany(
                "INSERT OR IGNORE INTO mesas (numero_mesa, capacidad, ubicacion) VALUES (?, ?, ?)",
                MESES_INICIALES,
            )
            conn.execute("UPDATE mesas SET ubicacion = 'Salón' WHERE ubicacion = 'Salon'")

    def authenticate(self, username: str, password: str) -> dict | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id_usuario, nombre, usuario, password, rol FROM usuarios WHERE usuario = ?",
                (username.strip(),),
            ).fetchone()
        if row is None or not verify_password(password, row["password"]):
            return None
        return {key: row[key] for key in ("id_usuario", "nombre", "usuario", "rol")}

    def list_users(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id_usuario, nombre, usuario, rol FROM usuarios ORDER BY nombre"
            ).fetchall()
        return [dict(row) for row in rows]

    def create_user(self, name: str, username: str, password: str, role: str) -> None:
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (?, ?, ?, ?)",
                (name.strip(), username.strip(), hash_password(password), role),
            )

    def list_tables(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id_mesa, numero_mesa, capacidad, ubicacion FROM mesas ORDER BY numero_mesa"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_available_tables(
        self, date: str, time: str, people: int, exclude_reservation_id: int | None = None
    ) -> list[dict]:
        sql = """
            SELECT m.id_mesa, m.numero_mesa, m.capacidad, m.ubicacion
            FROM mesas AS m
            WHERE m.capacidad >= ?
              AND NOT EXISTS (
                  SELECT 1 FROM reservas AS r
                  WHERE r.id_mesa = m.id_mesa AND r.fecha = ? AND r.hora = ?
                    AND r.estado = 'Activa'
                    AND (? IS NULL OR r.id_reserva != ?)
              )
            ORDER BY m.capacidad, m.numero_mesa
        """
        with self.connection() as conn:
            rows = conn.execute(
                sql, (people, date, time, exclude_reservation_id, exclude_reservation_id)
            ).fetchall()
        return [dict(row) for row in rows]

    def create_reservation(
        self, name: str, phone: str, user_id: int, table_id: int, date: str,
        time: str, people: int, notes: str,
    ) -> int:
        with self.connection() as conn:
            table = conn.execute(
                "SELECT capacidad FROM mesas WHERE id_mesa = ?", (table_id,)
            ).fetchone()
            if table is None or table["capacidad"] < people:
                raise ValueError("La mesa seleccionada no tiene capacidad suficiente.")
            occupied = conn.execute(
                """
                SELECT 1 FROM reservas
                WHERE id_mesa = ? AND fecha = ? AND hora = ? AND estado = 'Activa'
                """,
                (table_id, date, time),
            ).fetchone()
            if occupied:
                raise ValueError("La mesa ya está reservada para esa fecha y hora.")
            # Client creation and reservation insertion share one transaction.
            client = conn.execute(
                "SELECT id_cliente FROM clientes WHERE telefono = ? ORDER BY id_cliente LIMIT 1",
                (phone.strip(),),
            ).fetchone()
            if client:
                client_id = int(client["id_cliente"])
                conn.execute(
                    "UPDATE clientes SET nombre = ? WHERE id_cliente = ?",
                    (name.strip(), client_id),
                )
            else:
                client_cursor = conn.execute(
                    "INSERT INTO clientes (nombre, telefono) VALUES (?, ?)",
                    (name.strip(), phone.strip()),
                )
                client_id = int(client_cursor.lastrowid)
            cursor = conn.execute(
                """
                INSERT INTO reservas
                    (id_cliente, id_usuario, id_mesa, fecha, hora,
                     cantidad_personas, estado, observaciones)
                VALUES (?, ?, ?, ?, ?, ?, 'Activa', ?)
                """,
                (client_id, user_id, table_id, date, time, people, notes.strip()),
            )
            return int(cursor.lastrowid)

    def update_reservation(
        self, reservation_id: int, name: str, phone: str, table_id: int,
        date: str, time: str, people: int, notes: str,
    ) -> None:
        with self.connection() as conn:
            reservation = conn.execute(
                "SELECT id_cliente, estado FROM reservas WHERE id_reserva = ?",
                (reservation_id,),
            ).fetchone()
            if reservation is None or reservation["estado"] != "Activa":
                raise ValueError("La reserva no existe o ya no está activa.")
            table = conn.execute(
                "SELECT capacidad FROM mesas WHERE id_mesa = ?", (table_id,)
            ).fetchone()
            if table is None or table["capacidad"] < people:
                raise ValueError("La mesa seleccionada no tiene capacidad suficiente.")
            occupied = conn.execute(
                """
                SELECT 1 FROM reservas
                WHERE id_mesa = ? AND fecha = ? AND hora = ? AND estado = 'Activa'
                  AND id_reserva != ?
                """,
                (table_id, date, time, reservation_id),
            ).fetchone()
            if occupied:
                raise ValueError("La mesa ya está reservada para esa fecha y hora.")
            conn.execute(
                "UPDATE clientes SET nombre = ?, telefono = ? WHERE id_cliente = ?",
                (name.strip(), phone.strip(), reservation["id_cliente"]),
            )
            conn.execute(
                """
                UPDATE reservas
                SET id_mesa = ?, fecha = ?, hora = ?, cantidad_personas = ?, observaciones = ?
                WHERE id_reserva = ?
                """,
                (table_id, date, time, people, notes.strip(), reservation_id),
            )

    def cancel_reservation(self, reservation_id: int) -> None:
        with self.connection() as conn:
            cursor = conn.execute(
                "UPDATE reservas SET estado = 'Cancelada' "
                "WHERE id_reserva = ? AND estado = 'Activa'",
                (reservation_id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("La reserva no existe o ya está cancelada.")

    def list_reservations(
        self, date: str = "", customer: str = "", state: str = "", past_only: bool = False
    ) -> list[dict]:
        conditions = []
        params: list = []
        if date:
            conditions.append("r.fecha = ?")
            params.append(date)
        if customer.strip():
            conditions.append("c.nombre LIKE ?")
            params.append(f"%{customer.strip()}%")
        if state and state != "Todos":
            conditions.append("r.estado = ?")
            params.append(state)
        if past_only:
            conditions.append("(r.fecha < date('now', 'localtime') OR r.estado = 'Completada')")
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.connection() as conn:
            rows = conn.execute(
                f"""
                SELECT r.id_reserva, c.nombre AS cliente, c.telefono,
                       m.numero_mesa, m.capacidad, m.ubicacion, r.fecha, r.hora,
                       r.cantidad_personas, r.estado, r.observaciones, u.nombre AS responsable,
                       u.id_usuario
                FROM reservas AS r
                JOIN clientes AS c ON c.id_cliente = r.id_cliente
                JOIN mesas AS m ON m.id_mesa = r.id_mesa
                JOIN usuarios AS u ON u.id_usuario = r.id_usuario
                {where}
                ORDER BY r.fecha DESC, r.hora DESC, r.id_reserva DESC
                """,
                params,
            ).fetchall()
        return [dict(row) for row in rows]
