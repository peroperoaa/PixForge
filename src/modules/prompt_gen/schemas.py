from typing import Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, ConfigDict, WithJsonSchema

class PromptInput(BaseModel):
    model_config = ConfigDict(strict=True)
    text_prompt: str = Field(..., description="The main text prompt for generation")
    image_path: Optional[str] = Field(None, description="Optional path to an image for img2img")

class PromptOutput(BaseModel):
    model_config = ConfigDict(strict=True)
    positive_prompt: str = Field(..., description="The generated positive prompt")

    negative_prompt: str = Field(..., description="The generated negative prompt")
    style_parameters: Annotated[Dict[str, Any], WithJsonSchema({'type': 'object'})] = Field(
        ...,
        description=(
            "Style parameters for pixel-art generation. Expected keys include: "
            "view_angle (e.g. 'front', '3/4'), background_type (e.g. 'simple', 'transparent'), "
            "outline_style (e.g. 'clear', 'bold'), color_palette, and detail_level."
        )
    )
