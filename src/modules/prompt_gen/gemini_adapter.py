from typing import Tuple, List, Union
from pydantic import BaseModel
from google import genai
from google.genai import types

from src.core.config import ConfigManager
from src.modules.prompt_gen.interface import BasePromptGenerator
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput

class GeminiAdapter(BasePromptGenerator):
    """Adapter for generating prompts using Google GenAI SDK."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the adapter with a configured client."""
        self.api_key = config_manager.get_api_key()
        self.model_name = config_manager.get_model() or "gemini-2.5-flash"
        self.client = genai.Client(api_key=self.api_key)
        
    def _construct_request(self, input_data: PromptInput) -> Tuple[List[Union[str, types.Part]], types.GenerateContentConfig]:
        """Construct the contents and configuration for the API request."""
        
        system_instruction = (
            "You are an expert prompt engineer. Given a basic idea or prompt, "
            "generate a detailed positive prompt, a negative prompt, and relevant "
            "style parameters for an image generation model. Respond strictly in JSON format matching the schema."
        )
        
        contents = [input_data.text_prompt]
        
        # If there's an image path, we'd add image part here. 
        # But per current requirements and schema, sticking to text for now.
        if input_data.image_path:
            # Note: The actual file upload or Part creation from local path depends on GenAI SDK capabilities.
            pass
            
        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=PromptOutput,
        )
        
        return contents, generation_config
        
    def generate(self, input_data: PromptInput) -> PromptOutput:
        """Generate prompt implementation."""
        contents, config = self._construct_request(input_data)
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )
        
        # Parse output - The SDK should handle Pydantic objects directly if we use generate_content with response_schema
        # But actually standard client returns `response.parsed` which is the instance
        if hasattr(response, "parsed") and isinstance(response.parsed, PromptOutput):
            return response.parsed
            
        # Fallback parsing just in case
        return PromptOutput.model_validate_json(response.text)
