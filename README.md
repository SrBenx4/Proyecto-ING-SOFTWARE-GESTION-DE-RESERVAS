# Sistema de Gestión de Reservas para Cafetería Don Quelo

Aplicación de escritorio académica para administrar reservas de la cafetería. Está desarrollada con Python 3, CustomTkinter y SQLite, con separación de modelos, vistas, controladores y persistencia.

## 1. Requisitos

- Python 3.10 o superior.
- Windows, macOS o Linux con entorno gráfico.
- Conexión a Internet durante la instalación de CustomTkinter.

## 2. Instalación y primer inicio

Abre PowerShell o una terminal y cambia a la carpeta `Proyecto`. Por ejemplo, si descargaste el proyecto en la ruta indicada:

```powershell
cd "C:\Users\bsanh\Desktop\Archivos\Ingenieria en software\Proyecto"
```

Crea un entorno virtual, actívalo e instala las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell impide activar el entorno por la política de ejecución, puedes usar `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos siguientes, sin cambiar la política del equipo.

En macOS/Linux, activa el entorno con:

```bash
source .venv/bin/activate
```

Inicia la aplicación desde la carpeta `Proyecto`:

```bash
python main.py
```

En el primer inicio se crea automáticamente `database/database.db`, sus tablas, el usuario inicial y las 20 mesas. La cuenta inicial es:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin123` | Administrador |

Escribe el nombre de usuario y la contraseña en el login y pulsa **Iniciar sesión**. El menú muestra el nombre y el rol de la sesión activa. Para salir de la cuenta sin cerrar la aplicación, pulsa **Cerrar sesión**.

## 3. Menú y permisos por rol

| Acción | Administrador | Garzon | Jefe |
|---|:---:|:---:|:---:|
| Registrar reserva | Sí | Sí | No |
| Ver reservas | Sí | Sí | Sí |
| Modificar reserva | Sí | Sí | No |
| Cancelar reserva | Sí | Sí | No |
| Consultar disponibilidad de mesas | Sí | Sí | Sí |
| Consultar historial | Sí | No | Sí |
| Gestionar usuarios | Sí | No | No |

Las opciones no permitidas para el rol no aparecen en el menú.

## 4. Uso de reservas

Las fechas se ingresan en formato `AAAA-MM-DD` (por ejemplo, `2026-12-24`) y las horas en formato de 24 horas `HH:MM` (por ejemplo, `18:30`). La cantidad de personas debe ser un entero mayor que cero. No se aceptan fechas pasadas para crear o modificar reservas.

### Registrar una reserva

1. Inicia sesión como **Administrador** o **Garzon** y pulsa **Registrar reserva**.
2. Completa el nombre del cliente, teléfono, fecha, hora y cantidad de personas. Las observaciones son opcionales.
3. Al cambiar los datos de fecha, hora o cantidad, el formulario actualiza la lista de mesas compatibles y disponibles.
4. Selecciona una mesa de la lista y pulsa **Guardar reserva**.
5. La reserva se guarda en estado **Activa** y registra al usuario que la creó como responsable.

El sistema requiere nombre y teléfono, y verifica que la mesa tenga capacidad suficiente y no tenga otra reserva activa para la misma fecha y hora. La búsqueda de mesas muestra primero las de menor capacidad que sirven para el grupo. El cliente se identifica por su teléfono; si el teléfono ya existe, se actualiza el nombre asociado.

### Consultar reservas

1. Pulsa **Ver reservas**.
2. Para consultar una fecha específica, escribe una fecha válida y pulsa **Filtrar**.
3. Pulsa **Todas** para quitar el filtro.

La tabla presenta identificador, cliente, teléfono, mesa, fecha, hora, número de personas, estado y responsable.

### Modificar una reserva

1. Pulsa **Modificar reserva**.
2. Selecciona una reserva de la tabla y pulsa **Cargar seleccionada**.
3. Cambia los datos necesarios y selecciona una mesa disponible.
4. Pulsa **Guardar cambios**.

Solo se pueden modificar reservas **Activas**. Al editar, la mesa asignada a esa misma reserva se considera disponible para evitar que la reserva se bloquee a sí misma. El teléfono y el nombre del cliente se actualizan junto con la reserva.

### Cancelar una reserva

1. Pulsa **Cancelar reserva**.
2. Selecciona la reserva que quieres cancelar y pulsa **Cancelar seleccionada**.
3. Confirma la acción.

La cancelación cambia el estado a **Cancelada**; no borra la reserva ni su historial. Una reserva cancelada libera la mesa para ese horario.

## 5. Disponibilidad de mesas

1. Pulsa **Disponibilidad de mesas**.
2. Ingresa la fecha y hora que quieres consultar.
3. Pulsa **Consultar**.

La tabla muestra el número de cada mesa, su capacidad, ubicación y si está **Disponible** o **Reservada** en ese horario. La consulta de disponibilidad contempla cualquier tamaño de grupo y marca como reservada una mesa que tenga una reserva activa en la fecha y hora exactas indicadas.

### Distribución inicial del local

| Ubicación | Mesas | Capacidades |
|---|---|---|
| Salón | 1, 2 y 3 | 2 personas cada una |
| Salón | 4, 5 y 6 | 4 personas cada una |
| Terraza | 7 y 8 | 8 personas cada una |
| Terraza | 9, 10 y 11 | 2 personas cada una |
| Terraza | 12, 13, 14, 15 y 16 | 6 personas cada una |
| Terraza | 17, 18, 19 y 20 | 4 personas cada una |

## 6. Historial

El **Administrador** y el **Jefe** pueden abrir **Historial**. Opcionalmente, filtra por fecha, parte del nombre del cliente y estado (**Todos**, **Activa**, **Cancelada** o **Completada**) y pulsa **Filtrar**.

El historial incluye las reservas de fechas anteriores a hoy y todas las reservas marcadas **Completadas**, incluso si tienen fecha de hoy o futura. No permite marcar una reserva como completada desde la interfaz: los estados disponibles para la operación normal son **Activa** y **Cancelada**.

## 7. Gestión de usuarios

Solo el **Administrador** tiene la opción **Gestionar usuarios**:

1. Ingresa nombre, nombre de usuario, contraseña y rol.
2. Pulsa **Crear usuario**.
3. La nueva cuenta aparecerá en la tabla de usuarios.

Todos los campos son obligatorios; el nombre de usuario debe ser único y la contraseña debe tener al menos 6 caracteres. Los roles disponibles son `Administrador`, `Garzon` y `Jefe`. Las contraseñas se guardan como hashes PBKDF2; no se muestran en la tabla.

## 8. Base de datos, respaldo y reinicio

El archivo de datos está en `database/database.db`. Se crea automáticamente al ejecutar `main.py`; `database/db_manager.py` contiene el esquema y la inicialización de la base y las mesas.

Para respaldar los datos, cierra la aplicación y copia `database/database.db` a una ubicación segura. Para restaurarlos, cierra la aplicación y reemplaza el archivo por la copia. Para iniciar una base vacía, cierra la aplicación, respalda el archivo existente y renómbralo o muévelo fuera de `database`; al iniciar de nuevo se creará una base nueva con el administrador inicial y las mesas. Al reiniciar así se pierden los datos que no estén en el respaldo.

## 9. Datos de prueba y pruebas automatizadas

Para crear usuarios de prueba, clientes y tres reservas futuras, ejecuta desde la carpeta `Proyecto`:

```powershell
python -m database.seed_test_data
```

En macOS/Linux el mismo comando funciona con el entorno virtual activado. Las cuentas adicionales son:

| Usuario | Contraseña | Rol |
|---|---|---|
| `garzon` | `garzon123` | Garzon |
| `jefe` | `jefe123` | Jefe |

El script crea los usuarios de prueba si aún no existen. Solo agrega las reservas de demostración cuando la base de datos no contiene ninguna reserva. Para probar sin tocar la base de trabajo, conserva una copia de respaldo o usa una base temporal.

Ejecuta las pruebas automatizadas desde `Proyecto`:

```powershell
python -m unittest discover -s tests -v
```

Las pruebas usan una base temporal e incluyen inicialización, autenticación, validación de campos, compatibilidad y ocupación de mesas, cancelación, disponibilidad e idempotencia del script de datos.

## 10. Validaciones y solución de problemas

- **Usuario o contraseña incorrectos:** revisa las credenciales; para el administrador inicial usa `admin` / `admin123`.
- **Campos obligatorios o teléfono vacío:** completa nombre y teléfono del cliente.
- **Fecha u hora inválida:** usa exactamente `AAAA-MM-DD` y `HH:MM` en formato de 24 horas.
- **Fecha pasada:** selecciona hoy o una fecha posterior para crear o modificar una reserva.
- **No hay mesas disponibles:** cambia la fecha u hora, o reduce la cantidad de personas si corresponde.
- **Mesa ya reservada:** vuelve a cargar la lista de mesas y elige una mesa libre. No se permiten dos reservas activas de la misma mesa para el mismo horario.
- **No se encuentra `customtkinter`:** activa el entorno virtual e instala dependencias con `python -m pip install -r requirements.txt`.
- **La base está bloqueada o no se guardan cambios:** cierra otras instancias de la aplicación y verifica que el usuario tenga permiso de escritura en la carpeta `database`.

## 11. Alcance del prototipo

Cada reserva bloquea una mesa únicamente para la fecha y hora exactas registradas. El prototipo no gestiona duración de la reserva, intervalos horarios, pagos, recuperación de contraseñas ni cambios de estado a **Completada** desde la interfaz. La estructura de la base y las reglas de negocio están preparadas para ampliaciones futuras.

## 12. Estructura del proyecto

```text
Proyecto/
├── main.py
├── requirements.txt
├── README.md
├── assets/
├── database/
│   ├── database.db
│   ├── db_manager.py
│   └── seed_test_data.py
├── models/
├── controllers/
├── views/
└── tests/
```
