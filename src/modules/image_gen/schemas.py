from pydantic import BaseModel
from typing import Optional

class ImageGenInput(BaseModel):
    prompt: str
    image_path: Optional[str] = None
    aspect_ratio: str = "1:1"
    person_generation: Optional[str] = None
    safety_filter_level: Optional[str] = None

class ImageGenOutput(BaseModel):
    image_path: str
