"""
Rutas de Autenticación
Login, Logout, Gestión de Sesiones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session, joinedload
import bcrypt
from datetime import date

from app.database import get_db
from app.models.usuario import Usuario
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.schemas.auth import UsuarioLogin, LoginResponse, LogoutResponse, MeResponse

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


@router.post("/login", response_model=LoginResponse)
def login(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Login de usuario
    - Verifica credenciales
    - Crea sesión activa
    - Retorna token y datos del usuario
    """
    # Buscar usuario por correo
    usuario = db.query(Usuario).options(joinedload(Usuario.cliente)).filter(Usuario.correo == credenciales.correo).first()
    
    if not usuario or not verify_password(credenciales.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )
    
    if usuario.estado == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario dado de baja"
        )
    
    # Validar que el nivel coincida
    if usuario.nivel != credenciales.nivel:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol incorrecto para este usuario"
        )
    
    # Crear nueva sesión
    nueva_sesion = SesionLog(
        fecha_inicio=date.today(),
        estado=1
    )
    db.add(nueva_sesion)
    db.flush()
    
    # Registrar detalle de sesión (acción de login)
    detalle = DetalleSesion(
        tabla="usuario",
        accion=0,  # Consulta (login)
        cod_usuario=usuario.cod_usuario,
        num_sesion=nueva_sesion.num_sesion
    )
    db.add(detalle)
    db.commit()
    
    # En producción, aquí generarías un JWT real
    token = f"token_{usuario.cod_usuario}_{nueva_sesion.num_sesion}"
    
    return {
        "message": "Login exitoso",
        "access_token": token,
        "token_type": "bearer",
        "usuario": MeResponse.model_validate(usuario),
        "num_sesion": nueva_sesion.num_sesion
    }


@router.post("/logout", response_model=LogoutResponse)
def logout(num_sesion: int = Query(..., description="Número de sesión a cerrar"), db: Session = Depends(get_db)):
    """
    Cierra la sesión activa del usuario
    """
    sesion = db.query(SesionLog).filter(SesionLog.num_sesion == num_sesion).first()
    
    if not sesion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    sesion.fecha_fin = date.today()
    sesion.estado = 0
    db.commit()
    
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me", response_model=MeResponse)
def get_current_user(cod_usuario: int = Query(..., description="Código del usuario autenticado"), db: Session = Depends(get_db)):
    """
    Obtiene los datos del usuario autenticado
    """
    usuario = db.query(Usuario).options(joinedload(Usuario.cliente)).filter(Usuario.cod_usuario == cod_usuario).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario
