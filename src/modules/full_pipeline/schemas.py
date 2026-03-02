from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, model_validator


class PipelineStage(IntEnum):
    PROMPT = 1
    IMAGE = 2
    PIXELIZATION = 3
    POST_PROCESSING = 4


class FullPipelineConfig(BaseModel):
    user_prompt: Optional[str] = None
    input_image_path: Optional[str] = None
    start_stage: PipelineStage = PipelineStage.PROMPT
    aspect_ratio: str = "1:1"
    palette_preset: str = "sweetie-16"
    color_count: Optional[int] = None
    target_sizes: list[int] = [32, 64]
    remove_background: bool = True
    asset_name: Optional[str] = None
    output_dir: Optional[str] = None

    @model_validator(mode="after")
    def validate_stage_requirements(self) -> "FullPipelineConfig":
        if self.start_stage == PipelineStage.PROMPT and not self.user_prompt:
            raise ValueError(
                "user_prompt is required when start_stage is PROMPT"
            )
        if self.start_stage > PipelineStage.PROMPT and not self.input_image_path:
            raise ValueError(
                "input_image_path is required when start_stage is IMAGE, PIXELIZATION, or POST_PROCESSING"
            )
        return self


class StageResult(BaseModel):
    stage: PipelineStage
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: float


class FullPipelineResult(BaseModel):
    stage_results: list[StageResult]
    final_asset_paths: list[str]
    total_duration_seconds: float
