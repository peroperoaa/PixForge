from pydantic import BaseModel
from typing import Optional

class ImageGenInput(BaseModel):
    prompt: str
    image_path: Optional[str] = None

class ImageGenOutput(BaseModel):
    image_path: str
