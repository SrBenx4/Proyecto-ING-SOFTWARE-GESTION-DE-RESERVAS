from dataclasses import dataclass


@dataclass(frozen=True)
class Mesa:
    id_mesa: int
    numero_mesa: int
    capacidad: int
    ubicacion: str
