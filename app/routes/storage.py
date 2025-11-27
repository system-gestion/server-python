from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
import requests
import time
from app.schemas.storage import UploadResponse
from app.database import get_db
from app.core.security import registrar_auditoria, get_token

router = APIRouter(
    prefix="/storage",
    tags=["Storage"],
)

FREEIMAGE_API_URL = "https://freeimage.host/json"
AUTH_TOKEN = "acb3d08751cf59286697ee382500304c588ba131"

@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(get_token)
):
    """
    Sube una imagen a freeimage.host
    """
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        
        # Preparar los datos para la petición
        timestamp = str(int(time.time() * 1000))
        
        payload = {
            "type": "file",
            "action": "upload",
            "timestamp": timestamp,
            "auth_token": AUTH_TOKEN
        }
        
        files = {
            "source": (file.filename, file_content, file.content_type)
        }
        
        # Headers simulando un navegador real (como en el curl)
        headers = {
            "origin": "https://freeimage.host",
            "referer": "https://freeimage.host/api",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36"
        }
        
        response = requests.post(
            FREEIMAGE_API_URL,
            data=payload,
            files=files,
            headers=headers
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error en freeimage.host: {response.text}"
            )
            
        data = response.json()
        
        if data.get("status_code") != 200:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al subir imagen: {data.get('error', {}).get('message', 'Unknown error')}"
            )
        
        # Registrar auditoría (2 = Inserción)
        registrar_auditoria(db, token, "storage", 2)
            
        return data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
