from typing import Optional
from src.core.config import ConfigManager
from src.modules.prompt_gen.schemas import PromptInput
from src.modules.prompt_gen.gemini_adapter import GeminiAdapter
from src.modules.image_gen.schemas import ImageGenInput
from src.modules.image_gen.gemini_adapter import GeminiImageAdapter
from src.modules.prompt_gen.exceptions import APIConnectionError
from src.modules.image_gen.exceptions import ImageGenerationError

class ImageGenerationPipeline:
    """
    A pipeline that orchestrates the generation of an image from a user prompt.
    It first uses Module 1 (Prompt Gen) to enhance the prompt, and then uses
    Module 2 (Image Gen) to generate the image.
    """
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.prompt_adapter = GeminiAdapter(config_manager)
        self.image_adapter = GeminiImageAdapter(config_manager)

    def generate_image(self, user_prompt: str, aspect_ratio: str = "1:1") -> Optional[str]:
        """
        Generates an image based on the user prompt.

        Args:
            user_prompt (str): The initial user prompt.
            aspect_ratio (str): The desired aspect ratio for the image.

        Returns:
            Optional[str]: The path to the generated image, or None if failed.
        """
        print(f"Pipeline started with prompt: '{user_prompt}'")

        # Step 1: Generate Enhanced Prompt
        print("Step 1: Enhancing prompt with Module 1...")
        prompt_input = PromptInput(text_prompt=user_prompt)
        try:
            prompt_output = self.prompt_adapter.generate(prompt_input)
            positive_prompt = prompt_output.positive_prompt
            negative_prompt = prompt_output.negative_prompt
            print(f"Enhanced Positive Prompt: {positive_prompt[:100]}...")
            print(f"Enhanced Negative Prompt: {negative_prompt[:100]}...")
        except APIConnectionError as e:
            print(f"Prompt Generation Failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in prompt generation: {e}")
            return None

        # Step 2: Generate Image
        print("Step 2: Generating image with Module 2...")
        # Note: Currently ImageGenInput does not support negative_prompt directly in the schema,
        # but we pass the enhanced positive prompt.
        image_input = ImageGenInput(
            prompt=positive_prompt,
            aspect_ratio=aspect_ratio
        )
        
        try:
            image_output = self.image_adapter.generate(image_input)
            print(f"Image generation successful: {image_output.image_path}")
            return image_output.image_path
        except ImageGenerationError as e:
            print(f"Image Generation Failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in image generation: {e}")
            return None
