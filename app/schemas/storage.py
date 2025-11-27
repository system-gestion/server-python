from pydantic import BaseModel
from typing import Optional, Any

class ImageSuccess(BaseModel):
    message: str
    code: int

class ImageFileDetails(BaseModel):
    filename: str
    name: str
    mime: str
    extension: str
    url: str
    size: int

class ImageThumbDetails(BaseModel):
    filename: str
    name: str
    mime: str
    extension: str
    url: str

class ImageMediumDetails(BaseModel):
    filename: str
    name: str
    mime: str
    extension: str
    url: str

class ImageData(BaseModel):
    name: str
    extension: str
    width: int
    height: int
    size: int
    time: int
    expiration: int
    likes: int
    description: Optional[str] = None
    original_filename: str
    is_animated: int
    id_encoded: str
    size_formatted: str
    filename: str
    url: str
    url_short: str
    url_seo: str
    url_viewer: str
    url_viewer_preview: str
    url_viewer_thumb: str
    image: ImageFileDetails
    thumb: ImageThumbDetails
    medium: Optional[ImageMediumDetails] = None
    display_url: str
    display_width: int
    display_height: int
    views_label: str
    likes_label: str
    how_long_ago: str
    date_fixed_peer: str
    title: str
    title_truncated: str
    title_truncated_html: str
    is_use_loader: bool

class ImageRequest(BaseModel):
    type: str
    action: str
    timestamp: str
    auth_token: str

class UploadResponse(BaseModel):
    status_code: int
    success: ImageSuccess
    image: ImageData
    request: ImageRequest
    status_txt: str
