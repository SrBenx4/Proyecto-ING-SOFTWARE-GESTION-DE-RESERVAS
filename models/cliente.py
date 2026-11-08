from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id_cliente: int
    nombre: str
    telefono: str
