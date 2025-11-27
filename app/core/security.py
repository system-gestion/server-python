from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models.detalle_sesion import DetalleSesion

# Esquema de seguridad Bearer para Swagger UI
security = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extrae el token del header Authorization: Bearer <token>
    """
    return credentials.credentials

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token de acceso JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica un token JWT y retorna el payload
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

import json

def registrar_auditoria(db: Session, token: str, tabla: str, accion: int, old_data: Optional[dict] = None, new_data: Optional[dict] = None):
    """
    Registra una acción de auditoría en la base de datos.
    
    Args:
        db (Session): Sesión de base de datos
        token (str): Token JWT del usuario
        tabla (str): Nombre de la tabla afectada
        accion (int): 0=Consulta, 1=Edición, 2=Inserción, 3=Eliminación
        old_data (dict, optional): Datos anteriores al cambio (para Update/Delete)
        new_data (dict, optional): Datos nuevos tras el cambio (para Insert/Update)
    """
    # Decodificar token para obtener usuario y sesión
    payload = decode_access_token(token)
    
    if not payload:
        # Si el token es inválido, no podemos registrar auditoría correctamente
        # Podríamos lanzar error o registrar como anónimo, pero por seguridad lanzamos error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido para auditoría"
        )
        
    cod_usuario = payload.get("sub")
    num_sesion = payload.get("sesion")
    
    if not cod_usuario or not num_sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token incompleto para auditoría"
        )
        
    # Estructurar datos para snapshot
    datos_snapshot = {
        "old_data": old_data,
        "new_data": new_data
    }
    
    # Serializar datos a JSON si existen
    datos_json_str = None
    if old_data or new_data:
        try:
            # Convertir objetos date/datetime a string para serialización
            def json_serial(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                raise TypeError (f"Type {type(obj)} not serializable")
                
            datos_json_str = json.dumps(datos_snapshot, default=json_serial)
        except Exception as e:
            print(f"Error serializando datos para auditoría: {e}")
            
    # Crear registro de detalle de sesión
    nuevo_detalle = DetalleSesion(
        tabla=tabla,
        accion=accion,
        cod_usuario=int(cod_usuario),
        num_sesion=int(num_sesion),
        hora=datetime.now().time(),
        datos_json=datos_json_str
    )
    
    db.add(nuevo_detalle)
    # No hacemos commit aquí para permitir que la transacción principal maneje el commit/rollback
    # Pero si es una consulta (GET), necesitamos hacer commit o flush para que quede registrado
    if accion == 0: 
        db.commit()
    else:
        db.flush()
