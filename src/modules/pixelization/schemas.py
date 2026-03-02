from pydantic import BaseModel
from typing import Optional


class PixelizationInput(BaseModel):
    image_path: str
    image_bytes: Optional[bytes] = None
    prompt: Optional[str] = None
    denoising_strength: Optional[float] = None


class PixelizationOutput(BaseModel):
    image_path: str
    width: Optional[int] = None
    height: Optional[int] = None
