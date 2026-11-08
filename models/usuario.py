from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id_usuario: int
    nombre: str
    usuario: str
    rol: str


ROLES = ("Administrador", "Garzon", "Jefe")
