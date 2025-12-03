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
from app.models.email_verification import EmailVerificationToken
from app.schemas.auth import UsuarioLogin, LoginResponse, LogoutResponse, MeResponse, VerifyEmailRequest, VerifyEmailResponse
from app.core.security import create_access_token, get_token
from app.email.email_service import email_service

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
def get_current_user_info(
    current_user: Usuario = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Obtiene los datos del usuario autenticado usando el token
    """
    from app.core.security import registrar_auditoria
    
    # Registrar auditoría de consulta de perfil
    registrar_auditoria(db, token, "usuario", 0)
    
    return current_user


@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """
    Verifica el email del usuario usando el token enviado por correo
    """
    from datetime import datetime
    
    # Buscar el token en la base de datos
    token_record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == request.token
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación inválido"
        )
    
    # Verificar si el token ya fue usado
    if token_record.used == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token ya ha sido utilizado"
        )
    
    # Verificar si el token ha expirado
    if datetime.utcnow() > token_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de verificación ha expirado"
        )
    
    # Buscar el usuario
    usuario = db.query(Usuario).filter(
        Usuario.cod_usuario == token_record.cod_usuario
    ).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar el email del usuario
    usuario.email_verificado = 1
    token_record.used = 1
    
    db.commit()
    
    # Enviar email de bienvenida
    email_service.send_welcome_email(
        recipient_email=usuario.correo,
        username=f"{usuario.nombres} {usuario.apellidos}"
    )
    
    return {
        "message": "Email verificado exitosamente",
        "email_verified": True
    }


@router.post("/resend-verification")
def resend_verification_email(correo: str, db: Session = Depends(get_db)):
    """
    Reenvía el email de verificación al usuario
    """
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if usuario.email_verificado == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está verificado"
        )
    
    # Generar nuevo token
    token = email_service.generate_verification_token()
    
    # Guardar token en la base de datos
    nuevo_token = EmailVerificationToken(
        cod_usuario=usuario.cod_usuario,
        token=token
    )
    db.add(nuevo_token)
    db.commit()
    
    # Enviar email
    email_sent = email_service.send_verification_email(
        recipient_email=usuario.correo,
        username=f"{usuario.nombres} {usuario.apellidos}",
        token=token
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el email de verificación"
        )
    
    return {
        "message": "Email de verificación reenviado exitosamente"
    }
