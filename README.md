# Comandos del Proyecto

## Instalación

```bash
# Crear entorno virtual (Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

```bash
# Copiar variables de entorno
copy .env.example .env
```

## Ejecución

```bash
# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

## Seeders (Datos de prueba)

```bash
# Poblar base de datos
python -m app.seeders.seed
```

## Documentación

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
