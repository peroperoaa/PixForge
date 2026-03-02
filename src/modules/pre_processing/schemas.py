from pydantic import BaseModel, field_validator
from typing import Optional, Tuple, Literal


class PreProcessingInput(BaseModel):
    image_path: str
    remove_background: bool = False
    intermediate_size: int = 256
    crop_mode: Literal["auto", "center"] = "auto"
    output_dir: Optional[str] = None

    @field_validator("intermediate_size")
    @classmethod
    def validate_intermediate_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"intermediate_size must be a positive integer, got {v}")
        return v


class PreProcessingOutput(BaseModel):
    image_path: str
    original_size: Tuple[int, int]
    intermediate_size: int
