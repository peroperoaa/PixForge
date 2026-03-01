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
        self.model_name = config_manager.get_image_model() or "imagen-3.0-generate-002"
        self.client = genai.Client(api_key=self.api_key)

    def generate(self, input_data: ImageGenInput) -> ImageGenOutput:
        """
        Generate an image using the Gemini API.
        This simply returns the first iteration stub, proper image byte processing will be added next.
        """
        config = types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            output_mime_type="image/png",
            person_generation="allow_adult"
        )
        
        try:
            # We don't save bytes to disk in this task yet, per tasks.json the next task handles bytes.
            # But the google-genai generation interface needs to compile:
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=input_data.prompt,
                config=config
            )
            # Dummy output for now; the next task will implement byte-to-PIL conversion and saving.
            return ImageGenOutput(image_path="dummy/path/to/image.png")
            
        except (APIError, ClientError) as e:
            raise ImageGenerationError(f"API Error during image generation: {e}")
        except Exception as e:
            raise ImageGenerationError(f"Unexpected error during image generation: {e}")