from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional
import json

class PromptOutput(BaseModel):
    model_config = ConfigDict(strict=True)
    positive_prompt: str = Field(..., description="The generated positive prompt")
    negative_prompt: str = Field(..., description="The generated negative prompt")
    style_parameters: Dict[str, Any] = Field(..., description="Style parameters for generation")

print(json.dumps(PromptOutput.model_json_schema(), indent=2))
