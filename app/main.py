"""
Aplicación principal FastAPI.
Configura la aplicación, inicializa la base de datos y registra las rutas.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.database import init_db
from app.routes import auth, clientes, pedidos, usuarios, articulos, auditoria, comisiones, storage, ofertas, ws_users
from app.routes.auth import get_current_user_from_token

# Crear la instancia de FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# Configurar CORS (permite peticiones desde otros orígenes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("🚀 Iniciando aplicación FastAPI...")
    print(f"📊 Conectando a la base de datos...")
    init_db()
    print("✅ Aplicación lista para recibir peticiones")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Cerrando aplicación FastAPI...")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Bienvenido a la API REST con FastAPI",
        "version": settings.VERSION,
        "documentation": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "message": "La API está funcionando correctamente"
    }


# Registrar los routers de las diferentes rutas
# Rutas públicas
app.include_router(auth.router)

# Rutas protegidas (requieren token)
app.include_router(usuarios.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(clientes.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(pedidos.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(articulos.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(auditoria.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(comisiones.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(ofertas.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(storage.router, dependencies=[Depends(get_current_user_from_token)])
app.include_router(ws_users.router)


# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG  # Hot reload en modo desarrollo
    )
