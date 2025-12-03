"""
Modelo para almacenar tokens de verificación de email
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from app.database import Base


class EmailVerificationToken(Base):
    """
    Tabla para almacenar tokens de verificación de email
    
    Atributos:
        id (int): ID único del token [PK]
        cod_usuario (int): Código del usuario al que pertenece el token
        token (str): Token único de verificación
        created_at (datetime): Fecha y hora de creación del token
        expires_at (datetime): Fecha y hora de expiración del token
        used (int): Indica si el token ya fue usado (0 = no, 1 = sí)
    """
    __tablename__ = "email_verification_token"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cod_usuario = Column(Integer, nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=24))
    used = Column(Integer, nullable=False, default=0)  # 0 = no usado, 1 = usado
