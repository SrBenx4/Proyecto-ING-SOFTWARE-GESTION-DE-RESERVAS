from dataclasses import dataclass


@dataclass(frozen=True)
class Reserva:
    id_reserva: int
    id_cliente: int
    id_usuario: int
    id_mesa: int
    fecha: str
    hora: str
    cantidad_personas: int
    estado: str
    observaciones: str


ESTADOS_RESERVA = ("Activa", "Cancelada", "Completada")
