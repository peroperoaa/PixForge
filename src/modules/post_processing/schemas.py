from pydantic import BaseModel, field_validator, model_validator
from typing import Optional


class PostProcessingInput(BaseModel):
    image_path: str
    asset_name: str
    target_sizes: list[int]
    remove_background: bool = False
    color_count: Optional[int] = None
    palette_path: Optional[str] = None
    palette_preset: Optional[str] = None
    output_dir: Optional[str] = None

    @field_validator("target_sizes")
    @classmethod
    def validate_target_sizes(cls, v: list[int]) -> list[int]:
        if len(v) == 0:
            raise ValueError("target_sizes must be a non-empty list")
        for size in v:
            if size <= 0:
                raise ValueError(f"All target_sizes must be positive integers, got {size}")
        return v

    @model_validator(mode="after")
    def validate_palette_sources(self) -> "PostProcessingInput":
        if self.palette_preset is not None and self.palette_path is not None:
            raise ValueError(
                "Cannot specify both 'palette_preset' and 'palette_path'. Use one or the other."
            )
        return self


class PostProcessingOutput(BaseModel):
    output_paths: list[str]
    target_sizes: list[int]
    color_count: Optional[int] = None
    palette_name: Optional[str] = None
