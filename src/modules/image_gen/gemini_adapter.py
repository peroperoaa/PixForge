import os
import io
import uuid
from PIL import Image

from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

from src.core.config import ConfigManager
from src.modules.image_gen.interface import BaseImageGenerator
from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput
from src.modules.image_gen.exceptions import ImageGenerationError

class GeminiImageAdapter(BaseImageGenerator):
    """Adapter for generating images using Google GenAI SDK's Imagen models."""

    def __init__(self, config_manager: ConfigManager):
        """Initialize the adapter with a configured client."""
        self.api_key = config_manager.get_api_key()
        self.model_name = config_manager.get_image_model() or "gemini-3.1-flash-image-preview"
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, input_data: ImageGenInput) -> ImageGenOutput:
        """
        Generate an image using the Gemini API.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[input_data.prompt]
            )

            generated_image = None
            
            # Navigate response structure based on user's working example and SDK common patterns
            parts = None
            if hasattr(response, 'parts'):
                parts = response.parts
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                    parts = response.candidates[0].content.parts
            
            if not parts:
                 raise ImageGenerationError("No content parts found in the API response.")

            for part in parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Attempt to get PIL image directly if method exists (as per user script)
                    if hasattr(part, 'as_image'):
                        generated_image = part.as_image()
                    # Fallback to reading bytes if available
                    elif hasattr(part.inline_data, 'data'):
                        img_bytes = part.inline_data.data
                        generated_image = Image.open(io.BytesIO(img_bytes))
                    
                    if generated_image:
                        break
            
            if not generated_image:
                raise ImageGenerationError("No image inline data found in the response.")

            # Generate unique path and save
            output_dir = getattr(self, 'output_dir', os.path.join(os.getcwd(), 'output', 'images'))
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(output_dir, filename)
            
            generated_image.save(filepath, format="PNG")
            
            return ImageGenOutput(image_path=filepath)

        except (APIError, ClientError) as e:
            raise ImageGenerationError(f"API Error during image generation: {e}")
        except Exception as e:
            raise ImageGenerationError(f"Unexpected error during image generation: {e}")