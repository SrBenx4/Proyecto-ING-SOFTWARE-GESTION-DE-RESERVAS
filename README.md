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

### Inicio con un clic en Windows

Haga doble clic en `iniciar.bat`, ubicado en la carpeta del proyecto. La primera vez,
prepara el entorno virtual e instala las dependencias; después abre la aplicación
directamente. Se requiere Python 3.10 o superior. Si Windows no reconoce el archivo,
haga clic derecho y seleccione **Abrir**.

### Inicio manual

Desde PowerShell, ubíquese en la carpeta del proyecto y ejecute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Ver la base de datos interna

La aplicación guarda sus datos en el archivo SQLite `database\database.db`, dentro
de la carpeta del proyecto. Para consultar las tablas gráficamente:

1. Instale **DB Browser for SQLite** desde su sitio oficial.
2. Abra el programa y seleccione **Open Database**.
3. Elija `database\database.db` en la carpeta del proyecto.
4. En **Browse Data**, seleccione la tabla que desea consultar.

También puede abrir ese archivo con una extensión de SQLite en Visual Studio Code.
Para evitar dañar los datos, cierre la aplicación antes de modificar la base y haga
una copia de seguridad. Las contraseñas de usuarios se almacenan como hashes, no
como texto legible.

### Tablas

| Tabla | Para qué sirve |
|---|---|
| `usuarios` | Guarda las cuentas que acceden al sistema, sus roles y los datos necesarios para controlar intentos fallidos y bloqueos. Las contraseñas se guardan como hashes. |
| `clientes` | Guarda el nombre y teléfono de las personas que realizan reservas. |
| `mesas` | Mantiene el catálogo de mesas, incluyendo su número, capacidad y ubicación. |
| `reservas` | Registra cada reserva: cliente, usuario responsable, mesa, fecha, hora, cantidad de personas, estado y observaciones. |

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