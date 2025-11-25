# API REST con FastAPI y PostgreSQL

Proyecto completo de API REST desarrollado con **FastAPI** y **PostgreSQL**, que incluye gestión de clientes, pedidos, usuarios, artículos, monitoreo y sesiones.

## 📋 Características

- ✅ Framework: **FastAPI** con documentación automática (Swagger UI)
- ✅ Base de datos: **PostgreSQL** con SQLAlchemy 2.0
- ✅ Validación de datos con **Pydantic**
- ✅ Variables de entorno con **python-dotenv**
- ✅ Autenticación de usuarios con contraseñas hasheadas (bcrypt)
- ✅ Endpoints RESTful completos (CRUD) para clientes, pedidos y usuarios
- ✅ Relaciones entre modelos (Foreign Keys)
- ✅ Paginación en endpoints de listado

## 📁 Estructura del Proyecto

```
server-python/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal de FastAPI
│   ├── config.py            # Configuración y variables de entorno
│   ├── database.py          # Conexión a PostgreSQL con SQLAlchemy
│   ├── models/              # Modelos de base de datos (ORM)
│   │   ├── __init__.py
│   │   ├── cliente.py
│   │   ├── articulo.py
│   │   ├── pedido.py
│   │   ├── detalle_pedido.py
│   │   ├── monitoreo.py
│   │   ├── usuario.py
│   │   ├── sesion_log.py
│   │   └── detalle_sesion.py
│   ├── schemas/             # Schemas de validación (Pydantic)
│   │   ├── __init__.py
│   │   ├── cliente.py
│   │   ├── pedido.py
│   │   ├── usuario.py
│   │   ├── articulo.py
│   │   ├── auditoria.py
│   │   └── comision.py
│   ├── routes/              # Rutas de la API (endpoints)
│   │   ├── __init__.py
│   │   ├── auth.py          # Autenticación (login/logout)
│   │   ├── usuarios.py      # CRUD usuarios + búsqueda + online
│   │   ├── clientes.py      # CRUD clientes
│   │   ├── pedidos.py       # CRUD pedidos + filtros avanzados
│   │   ├── articulos.py     # CRUD artículos/ofertas
│   │   ├── auditoria.py     # Sesiones y acciones
│   │   └── comisiones.py    # Cálculo de comisiones
│   └── seeders/             # Datos de prueba
│       ├── __init__.py
│       └── seed.py
├── venv/                    # Entorno virtual (no se sube a git)
├── .env                     # Variables de entorno (no se sube a git)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore               # Archivos ignorados por git
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Este archivo
└── ENDPOINTS.md             # Documentación completa de endpoints
```

## 🗄️ Modelos de Base de Datos

### Cliente
- `cod_cliente` (VARCHAR) - PK
- `nombre` (VARCHAR)
- `direccion` (VARCHAR)
- `telefono` (VARCHAR)

### Articulo
- `cod_articulo` (INTEGER) - PK
- `nombre` (VARCHAR)
- `pvp` (DOUBLE)
- `stock` (INTEGER)

### Pedido
- `num_pedido` (INTEGER) - PK
- `fecha` (DATE)
- `importe` (DOUBLE)
- `cod_cliente` (VARCHAR) - FK → Cliente

### DetallePedido
- `num_pedido` (INTEGER) - PK, FK → Pedido
- `cod_articulo` (INTEGER) - PK, FK → Articulo
- `cantidad` (INTEGER)
- `subtotal` (DOUBLE)
- `estado` (INTEGER) - 0 = quitado, 1 = activo

### Monitoreo
- `num_registro` (INTEGER) - PK
- `fecha` (DATE)
- `estado_vps` (INTEGER) - 0 = inactivo, 1 = activo

### Usuario
- `cod_usuario` (INTEGER) - PK
- `apellidos` (VARCHAR)
- `nombres` (VARCHAR)
- `nivel` (INTEGER) - 1 = supervisor, 2 = vendedor, 3 = cliente
- `correo` (VARCHAR)
- `celular` (VARCHAR)
- `fecha_ingreso` (DATE)
- `estado` (INTEGER) - 0 = de baja, 1 = activo
- `fecha_baja` (DATE/NULL)
- `password` (VARCHAR) - Hasheada con bcrypt

### SesionLog
- `num_sesion` (INTEGER) - PK
- `fecha_inicio` (DATE)
- `fecha_fin` (DATE)
- `estado` (INTEGER) - 0 = inactivo, 1 = activo

### DetalleSesion
- `num_detalle` (INTEGER) - PK
- `tabla` (VARCHAR)
- `accion` (INTEGER) - 0 = consulta, 1 = edición, 2 = inserción, 3 = eliminación
- `cod_usuario` (INTEGER) - FK → Usuario
- `num_sesion` (INTEGER) - FK → SesionLog

## 🚀 Instalación y Configuración

### 1. Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

### 2. Crear Entorno Virtual

#### En Windows (PowerShell):
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### En Linux/macOS:
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

2. Editar el archivo `.env` con tus configuraciones:
```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/nombre_bd
DEBUG=True
PORT=8000
SECRET_KEY=tu_clave_secreta_aqui
```

### 5. Crear Base de Datos en PostgreSQL

```sql
-- Conectarse a PostgreSQL
psql -U postgres

-- Crear base de datos
CREATE DATABASE nombre_bd;

-- Crear usuario (opcional)
CREATE USER usuario WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE nombre_bd TO usuario;
```

### 6. Ejecutar la Aplicación

```bash
# Opción 1: Usando Python directamente
python -m app.main

# Opción 2: Usando uvicorn
uvicorn app.main:app --reload --port 8000

# Opción 3: Desde el archivo main.py
cd app
python main.py
```

La aplicación estará disponible en: `http://localhost:8000`

### 7. Poblar la Base de Datos (Seeders)

Para insertar datos de prueba en la base de datos:

```bash
python -m app.seeders.seed
```

Este comando insertará datos de ejemplo en todas las tablas:
- 5 Clientes
- 10 Artículos
- 5 Usuarios con credenciales:
  - **Supervisor**: maria.garcia@example.com / `supervisor123`
  - **Vendedor**: carlos.rodriguez@example.com / `vendedor123`
  - **Cliente**: roberto.torres@example.com / `cliente123`
- 4 Pedidos con detalles
- 10 Registros de monitoreo
- 3 Sesiones con detalles

⚠️ **Nota**: Por defecto, este comando limpiará todas las tablas antes de insertar los datos.

## 📚 Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a la documentación interactiva:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔌 Endpoints Disponibles

### 🔐 Autenticación (`/auth`)
- `POST /auth/login` - Iniciar sesión
- `POST /auth/logout` - Cerrar sesión
- `GET /auth/me` - Obtener usuario actual

### 👤 Usuarios (`/usuarios`)
- `POST /usuarios/` - Crear usuario
- `GET /usuarios/` - Listar usuarios (filtros: estado, nivel)
- `GET /usuarios/search` - Buscar usuarios
- `GET /usuarios/online` - Usuarios con sesiones activas
- `GET /usuarios/{cod_usuario}` - Obtener usuario
- `PUT /usuarios/{cod_usuario}` - Actualizar usuario
- `PATCH /usuarios/{cod_usuario}/deactivate` - Dar de baja
- `PATCH /usuarios/{cod_usuario}/activate` - Reactivar usuario
- `DELETE /usuarios/{cod_usuario}` - Eliminar usuario

### 👥 Clientes (`/clientes`)
- `POST /clientes/` - Crear cliente
- `GET /clientes/` - Listar clientes
- `GET /clientes/search` - Buscar clientes
- `GET /clientes/{cod_cliente}` - Obtener cliente
- `PUT /clientes/{cod_cliente}` - Actualizar cliente
- `DELETE /clientes/{cod_cliente}` - Eliminar cliente

### 📦 Pedidos (`/pedidos`)
- `POST /pedidos/` - Crear pedido (con detalles)
- `GET /pedidos/` - Listar todos
- `GET /pedidos/search` - Búsqueda avanzada (múltiples filtros)
- `GET /pedidos/by-date` - Pedidos por fecha
- `GET /pedidos/by-number/{num}` - Pedido por número
- `GET /pedidos/pending` - Pedidos pendientes
- `GET /pedidos/completed` - Pedidos completados
- `GET /pedidos/cancelled` - Pedidos cancelados
- `GET /pedidos/cliente/{cod}` - Pedidos de un cliente
- `GET /pedidos/estadisticas` - Estadísticas generales
- `PUT /pedidos/{num_pedido}` - Actualizar pedido
- `PATCH /pedidos/{num_pedido}/cancel` - Anular pedido
- `DELETE /pedidos/{num_pedido}` - Eliminar pedido

### 🏷️ Artículos/Ofertas (`/articulos`)
- `POST /articulos/` - Crear artículo
- `GET /articulos/` - Listar artículos (filtro: stock_min)
- `GET /articulos/search` - Buscar por nombre
- `GET /articulos/ofertas` - Ofertas activas (stock > 0)
- `GET /articulos/{cod_articulo}` - Obtener artículo
- `PUT /articulos/{cod_articulo}` - Actualizar artículo
- `PATCH /articulos/{cod_articulo}/stock` - Actualizar stock
- `DELETE /articulos/{cod_articulo}` - Eliminar artículo/oferta

### 🔍 Auditoría (`/auditoria`)
- `GET /auditoria/sesiones` - Listar sesiones (filtros: fecha, estado)
- `GET /auditoria/sesiones/{num_sesion}` - Detalle de sesión
- `GET /auditoria/acciones` - Listar acciones (filtros: usuario, tabla, acción)
- `GET /auditoria/usuarios/{cod}/actividad` - Actividad de usuario
- `GET /auditoria/resumen` - Resumen de actividad de todos

### 💰 Comisiones (`/comisiones`)
- `GET /comisiones/vendedor/{cod}` - Calcular comisión de vendedor
- `GET /comisiones/vendedor/{cod}/detalles` - Detalle por pedido
- `GET /comisiones/resumen` - Comisiones de todos los vendedores

### ⚕️ Health Check
- `GET /` - Información básica de la API
- `GET /health` - Verificar estado de la API

> 📚 **Documentación completa**: Ver archivo `ENDPOINTS.md` para detalles y mapeo con frontend

## 🧪 Ejemplo de Uso

### Crear un Cliente

```bash
curl -X POST "http://localhost:8000/clientes/" \
  -H "Content-Type: application/json" \
  -d '{
    "cod_cliente": "CLI001",
    "nombre": "Juan Pérez",
    "direccion": "Calle Principal 123",
    "telefono": "555-1234"
  }'
```

### Crear un Usuario

```bash
curl -X POST "http://localhost:8000/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "cod_usuario": 1,
    "apellidos": "García",
    "nombres": "María",
    "nivel": 1,
    "correo": "maria@example.com",
    "celular": "555-5678",
    "password": "mipassword123"
  }'
```

### Login de Usuario

```bash
curl -X POST "http://localhost:8000/usuarios/login" \
  -H "Content-Type: application/json" \
  -d '{
    "correo": "maria@example.com",
    "password": "mipassword123"
  }'
```

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para construir APIs
- **SQLAlchemy 2.0**: ORM para Python
- **PostgreSQL**: Base de datos relacional
- **Pydantic**: Validación de datos y configuración
- **Uvicorn**: Servidor ASGI de alto rendimiento
- **Passlib**: Hashing de contraseñas con bcrypt
- **python-dotenv**: Gestión de variables de entorno

## 📝 Notas Adicionales

### Generar requirements.txt

Si añades más dependencias, actualiza el archivo:

```bash
pip freeze > requirements.txt
```

### Desactivar Entorno Virtual

```bash
# Windows y Linux/macOS
deactivate
```

### Modo Producción

Para producción, modifica las siguientes configuraciones:

1. En `.env`:
```env
DEBUG=False
SECRET_KEY=clave_segura_aleatoria_muy_larga
```

2. En `app/main.py`, actualiza CORS:
```python
allow_origins=["https://tudominio.com"],  # Dominios específicos
```

3. Usa un servidor de producción como Gunicorn:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias o mejoras.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**Desarrollado con ❤️ usando FastAPI y PostgreSQL**
