# Sistema de gestión de reservas - Cafetería Don Quelo

Aplicación de escritorio desarrollada con Python y CustomTkinter para registrar y administrar reservas de mesas.

## Integrantes

- Benjamin Sanhueza
- Valentin Mardones
- Rocio Lopez

## Requisitos

- Windows
- Python 3.10 o superior
- Pip

## Instalación y ejecución

Desde PowerShell, ubíquese en la carpeta del proyecto y cree un entorno virtual:

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inicie la aplicación con:

```powershell
python main.py
```

La base de datos SQLite se crea automáticamente en `database\database.db`. Al iniciar por primera vez también se crean el usuario administrador y las 20 mesas disponibles.

## Usuarios de acceso

| Rol | Usuario | Contraseña | Acceso |
|---|---|---|---|
| Administrador | `admin` | `Admin123!` | Acceso completo |
| Garzón | `garzon` | `Garzon123!` | Reservas y disponibilidad |
| Jefe | `jefe` | `Jefe123!` | Reservas, disponibilidad e historial |

Las cuentas de Garzón y Jefe se crean ejecutando la carga de datos de prueba:

```powershell
python -m database.seed_test_data
```

## Uso de la aplicación

1. Inicie sesión con una cuenta de la tabla anterior.
2. En el menú principal seleccione la operación que desea realizar.
3. Para registrar una reserva, ingrese el nombre y teléfono del cliente, la fecha (`AAAA-MM-DD`), la hora (`HH:MM`) y la cantidad de personas.
4. Seleccione una mesa disponible; el sistema mostrará solo las mesas compatibles con la cantidad de personas y el horario.
5. Use **Ver reservas** para consultar el listado y aplicar filtros por fecha.
6. Los usuarios Administrador y Garzón pueden modificar o cancelar reservas.
7. Los usuarios Administrador y Garzón pueden eliminar reservas registradas después de confirmar la acción.
8. Los usuarios Administrador y Jefe pueden consultar el historial.
9. Solo el Administrador puede gestionar cuentas de usuario.

Al cancelar una reserva, el registro no se elimina y la mesa vuelve a quedar disponible. Las reservas inactivas quedan registradas en el historial.

Las contraseñas creadas o modificadas deben tener al menos 8 caracteres e incluir mayúsculas, minúsculas, números y símbolos.

## Ejecutar pruebas

```powershell
python -m unittest discover -s tests -v
```