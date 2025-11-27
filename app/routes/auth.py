"""
Rutas de Autenticación
Login, Logout, Gestión de Sesiones
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from jose import JWTError, jwt
import bcrypt
from datetime import date, timedelta

from app.database import get_db
from app.config import settings
from app.models.usuario import Usuario
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.schemas.auth import UsuarioLogin, LoginResponse, LogoutResponse, MeResponse
from app.core.security import create_access_token, get_token

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash bcrypt"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def get_current_user_from_token(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """
    Dependencia para obtener el usuario actual desde el token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        cod_usuario: str = payload.get("sub")
        if cod_usuario is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).options(joinedload(Usuario.cliente)).filter(Usuario.cod_usuario == int(cod_usuario)).first()
    if user is None:
        raise credentials_exception
        
    if user.estado == 0:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
        
    return user


@router.post("/login", response_model=LoginResponse)
def login(credenciales: UsuarioLogin, db: Session = Depends(get_db)):
    """
    Login de usuario
    - Verifica credenciales
    - Crea sesión activa
    - Retorna token JWT y datos del usuario
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
    
    # Generar Token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(usuario.cod_usuario), "sesion": nueva_sesion.num_sesion},
        expires_delta=access_token_expires
    )
    
    return {
        "message": "Login exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": MeResponse.model_validate(usuario),
        "num_sesion": nueva_sesion.num_sesion
    }


@router.post("/logout", response_model=LogoutResponse)
def logout(
    num_sesion: int = Query(..., description="Número de sesión a cerrar"), 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_token)
):
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
def get_current_user_info(current_user: Usuario = Depends(get_current_user_from_token)):
    """
    Obtiene los datos del usuario autenticado usando el token
    """
    return current_user
