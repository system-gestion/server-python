"""
Rutas CRUD para Usuarios
Gestión completa de usuarios del sistema
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List
import bcrypt
from datetime import date

from app.database import get_db
from app.models.usuario import Usuario
from app.models.sesion_log import SesionLog
from app.models.detalle_sesion import DetalleSesion
from app.models.email_verification import EmailVerificationToken
from app.schemas.usuario import (
    UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioOnline
)
from app.core.security import registrar_auditoria, get_token
from app.email.email_service import email_service

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Crear nuevo usuario"""
    
    if db.query(Usuario).filter(Usuario.correo == usuario.correo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Correo {usuario.correo} ya registrado"
        )
    
    usuario_data = usuario.model_dump()
    # Guardar contraseña en texto plano para el email antes de hashear
    plain_password = usuario_data.get('password')
    usuario_data['password'] = hash_password(usuario_data['password'])
    # Determinar nombre de rol según el nivel
    nivel = usuario_data.get('nivel')
    role_map = {1: 'Supervisor', 2: 'Vendedor', 3: 'Cliente'}
    role_name = role_map.get(nivel, None)
    nuevo_usuario = Usuario(**usuario_data)
    
    db.add(nuevo_usuario)
    db.flush() # Flush para obtener el ID
    
    # Generar token de verificación
    verification_token = email_service.generate_verification_token()
    
    # Guardar token en la base de datos
    token_record = EmailVerificationToken(
        cod_usuario=nuevo_usuario.cod_usuario,
        token=verification_token
    )
    db.add(token_record)
    
    # Registrar auditoría (2 = Inserción)
    # El usuario pide explícitamente guardar todo, incluso el password encriptado
    audit_data = usuario_data.copy()
    audit_data["cod_usuario"] = nuevo_usuario.cod_usuario
    # Asegurar que fechas sean strings
    if "fecha_ingreso" in audit_data:
        audit_data["fecha_ingreso"] = str(audit_data["fecha_ingreso"])
    registrar_auditoria(db, token, "usuario", 2, new_data=audit_data)
    
    db.commit()
    db.refresh(nuevo_usuario)
    
    # Enviar email de verificación (no bloquear si falla)
    try:
        email_service.send_verification_email(
            recipient_email=nuevo_usuario.correo,
            username=f"{nuevo_usuario.nombres} {nuevo_usuario.apellidos}",
            token=verification_token,
            plain_password=plain_password,
            role_name=role_name
        )
    except Exception as e:
        print(f"⚠️ No se pudo enviar el email de verificación: {e}")
    
    return nuevo_usuario


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    skip: int = Query(0, description="Número de registros a omitir"),
    limit: int = Query(100, description="Número máximo de registros"),
    estado: int = Query(None, ge=0, le=1, description="Filtrar por estado (0=inactivo, 1=activo)"),
    nivel: int = Query(None, ge=1, le=3, description="Filtrar por nivel (1=Supervisor, 2=Vendedor, 3=Cliente)"),
    q: str = Query(None, description="Término de búsqueda (nombre, apellido o correo)"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Listar usuarios con filtros opcionales"""
    query = db.query(Usuario)
    
    if estado is not None:
        query = query.filter(Usuario.estado == estado)
    if nivel is not None:
        query = query.filter(Usuario.nivel == nivel)
    if q:
        query = query.filter(
            or_(
                Usuario.nombres.ilike(f"%{q}%"),
                Usuario.apellidos.ilike(f"%{q}%"),
                Usuario.correo.ilike(f"%{q}%")
            )
        )
    
    usuarios = query.offset(skip).limit(limit).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "usuario", 0)
    
    return usuarios


@router.get("/online", response_model=List[UsuarioOnline])
def usuarios_online(
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener lista de usuarios con sesiones activas"""
    usuarios = db.query(Usuario).filter(Usuario.estado == 1).all()
    
    resultado = []
    for usuario in usuarios:
        # Verificar si tiene sesión activa
        sesion_activa = db.query(SesionLog).filter(
            and_(
                SesionLog.estado == 1,
                SesionLog.detalles.any(cod_usuario=usuario.cod_usuario)
            )
        ).first()
        
        # Obtener última actividad
        ultima_sesion = db.query(SesionLog).join(
            SesionLog.detalles
        ).filter(
            DetalleSesion.cod_usuario == usuario.cod_usuario
        ).order_by(SesionLog.fecha_inicio.desc()).first()
        
        resultado.append({
            "cod_usuario": usuario.cod_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "correo": usuario.correo,
            "nivel": usuario.nivel,
            "sesion_activa": sesion_activa is not None,
            "ultima_actividad": ultima_sesion.fecha_inicio if ultima_sesion else None
        })
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "usuario", 0)
    
    return resultado


@router.get("/search", response_model=List[UsuarioResponse])
def buscar_usuarios(
    q: str = Query(..., min_length=1, description="Término de búsqueda (nombre, apellido o correo)"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Buscar usuarios por nombre, apellido o correo"""
    usuarios = db.query(Usuario).filter(
        or_(
            Usuario.nombres.ilike(f"%{q}%"),
            Usuario.apellidos.ilike(f"%{q}%"),
            Usuario.correo.ilike(f"%{q}%")
        )
    ).all()
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "usuario", 0)
    
    return usuarios


@router.get("/{cod_usuario}", response_model=UsuarioResponse)
def obtener_usuario(
    cod_usuario: int = Path(..., description="Código único del usuario"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Obtener un usuario específico"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    # Registrar auditoría (0 = Consulta)
    registrar_auditoria(db, token, "usuario", 0)
    
    return usuario


@router.put("/{cod_usuario}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_update: UsuarioUpdate,
    cod_usuario: int = Path(..., description="Código único del usuario a actualizar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Actualizar datos de usuario"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    update_data = usuario_update.model_dump(exclude_unset=True)
    
    # Verificar si el correo ya existe en otro usuario
    if 'correo' in update_data:
        correo_existente = db.query(Usuario).filter(
            Usuario.correo == update_data['correo'],
            Usuario.cod_usuario != cod_usuario
        ).first()
        if correo_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El correo {update_data['correo']} ya está registrado por otro usuario"
            )
    
    # Hash password si se está actualizando
    if 'password' in update_data:
        update_data['password'] = hash_password(update_data['password'])
    
    # Snapshot de datos originales antes de actualizar
    datos_originales = {
        "cod_usuario": usuario.cod_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "nivel": usuario.nivel,
        "celular": usuario.celular,
        "fecha_ingreso": str(usuario.fecha_ingreso),
        "estado": usuario.estado,
        "fecha_baja": str(usuario.fecha_baja) if usuario.fecha_baja else None,
        "password": usuario.password
    }

    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    # Registrar auditoría (1 = Edición)
    # Registrar auditoría (1 = Edición)
    datos_nuevos = {
        "cod_usuario": usuario.cod_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "nivel": usuario.nivel,
        "celular": usuario.celular,
        "fecha_ingreso": str(usuario.fecha_ingreso),
        "estado": usuario.estado,
        "fecha_baja": str(usuario.fecha_baja) if usuario.fecha_baja else None,
        "password": usuario.password
    }
    registrar_auditoria(db, token, "usuario", 1, old_data=datos_originales, new_data=datos_nuevos)
    
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{cod_usuario}/deactivate")
def desactivar_usuario(
    cod_usuario: int = Path(..., description="Código único del usuario a desactivar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Dar de baja a un usuario"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    # Snapshot estado original
    # Snapshot estado original completo
    datos_originales = {
        "cod_usuario": usuario.cod_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "nivel": usuario.nivel,
        "celular": usuario.celular,
        "fecha_ingreso": str(usuario.fecha_ingreso),
        "estado": usuario.estado,
        "fecha_baja": str(usuario.fecha_baja) if usuario.fecha_baja else None,
        "password": usuario.password
    }

    usuario.estado = 0
    usuario.fecha_baja = date.today()
    
    # Registrar auditoría (1 = Edición)
    datos_nuevos = datos_originales.copy()
    datos_nuevos["estado"] = usuario.estado
    datos_nuevos["fecha_baja"] = str(usuario.fecha_baja) if usuario.fecha_baja else None
    registrar_auditoria(db, token, "usuario", 1, old_data=datos_originales, new_data=datos_nuevos)
    
    db.commit()
    
    return {"message": f"Usuario {cod_usuario} desactivado exitosamente"}


@router.patch("/{cod_usuario}/activate")
def activar_usuario(
    cod_usuario: int = Path(..., description="Código único del usuario a activar"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Reactivar un usuario dado de baja"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    # Snapshot estado original
    # Snapshot estado original completo
    datos_originales = {
        "cod_usuario": usuario.cod_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "nivel": usuario.nivel,
        "celular": usuario.celular,
        "fecha_ingreso": str(usuario.fecha_ingreso),
        "estado": usuario.estado,
        "fecha_baja": str(usuario.fecha_baja) if usuario.fecha_baja else None,
        "password": usuario.password
    }

    usuario.estado = 1
    usuario.fecha_baja = None
    
    # Registrar auditoría (1 = Edición)
    datos_nuevos = datos_originales.copy()
    datos_nuevos["estado"] = usuario.estado
    datos_nuevos["fecha_baja"] = None
    registrar_auditoria(db, token, "usuario", 1, old_data=datos_originales, new_data=datos_nuevos)
    
    db.commit()
    
    return {"message": f"Usuario {cod_usuario} activado exitosamente"}


@router.delete("/{cod_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    cod_usuario: int = Path(..., description="Código único del usuario a eliminar permanentemente"),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """Eliminar usuario permanentemente"""
    usuario = db.query(Usuario).filter(Usuario.cod_usuario == cod_usuario).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario {cod_usuario} no encontrado"
        )
    
    # Snapshot completo antes de eliminar
    datos_originales = {
        "cod_usuario": usuario.cod_usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "nivel": usuario.nivel,
        "celular": usuario.celular,
        "fecha_ingreso": str(usuario.fecha_ingreso),
        "estado": usuario.estado,
        "fecha_baja": str(usuario.fecha_baja) if usuario.fecha_baja else None,
        "password": usuario.password
    }

    db.delete(usuario)
    
    # Registrar auditoría (3 = Eliminación)
    registrar_auditoria(db, token, "usuario", 3, old_data=datos_originales)
    
    db.commit()
    return None
