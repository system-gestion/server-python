
### 🚀 Guía de Despliegue en Google Cloud (Paso a Paso)

Sigue estos bloques de comandos en tu terminal SSH.

#### Paso 1: Preparar el Sistema e Instalar Docker

Primero actualizamos todo e instalamos Docker.

```bash
# 1. Actualizar repositorios
sudo apt update

# 2. Instalar herramientas básicas y Docker
sudo apt install git python3-venv python3-pip docker.io -y

# 3. Dar permisos a tu usuario para usar Docker (Evita usar sudo siempre)
sudo usermod -aG docker $USER
```

🛑 **¡IMPORTANTE\!**
En este punto, **cierra la ventana de SSH y vuelve a conectarte**. Esto es obligatorio para que los permisos de Docker se apliquen. Si no lo haces, el siguiente paso fallará.

#### Paso 2: Crear la Base de Datos (PostgreSQL)

Una vez reconectado, levantamos la base de datos. He configurado las credenciales para que coincidan con el ejemplo del `.env` más abajo.

```bash
docker run -d \
  --name db_system_gestion \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password_seguro_123 \
  -e POSTGRES_DB=system_gestion_db \
  -p 5432:5432 \
  --restart always \
  postgres:15-alpine
```

#### Paso 3: Clonar y Preparar el Proyecto

Ahora traemos el código.

```bash
# 1. Clonar el repositorio
git clone https://github.com/system-gestion/server-python.git

# 2. Entrar a la carpeta
cd server-python

# 3. Crear entorno virtual
python3 -m venv venv

# 4. Activar entorno virtual
source venv/bin/activate

# 5. Instalar dependencias
pip install -r requirements.txt
```

#### Paso 4: Crear el archivo .env

Ahora creamos el archivo de configuración con los datos del Paso 2.

```bash
nano .env
```

**Pega este contenido dentro** (ajustado para producción):

```env
# --- Base de Datos (Conectada al Docker del Paso 2) ---
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_db
DATABASE_URL=postgresql://admin:password_seguro_123@localhost:5432/system_gestion_db

# --- Servidor ---
# DEBUG en False para producción (importante)
DEBUG=False
PORT=8000

# --- Seguridad ---
SECRET_KEY=cambia_esto_por_una_cadena_larga_y_aleatoria_super_secreta
```

*(Guarda con `Ctrl+O`, `Enter`, y sal con `Ctrl+X`)*.

#### Paso 5: Poblar la Base de Datos (Seeders)

Como ya tenemos conexión, inyectamos los datos de prueba.

```bash
python -m app.seeders.seed
```

#### Paso 6: Ejecutar el Servidor (Modo Producción)

Aquí está el cambio clave. No usaremos `--reload` (eso es para desarrollo) y usaremos `--host 0.0.0.0` para que Google Cloud permita la entrada de internet.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación de API

Una vez iniciado el servidor, puedes acceder a la documentación interactiva:

  - **Swagger UI:** `http://TU_IP_O_DOMINIO:8000/docs`
  - **ReDoc:** `http://TU_IP_O_DOMINIO:8000/redoc`

<!-- end list -->

```
```
