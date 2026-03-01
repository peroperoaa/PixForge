from abc import ABC, abstractmethod

from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput

class BaseImageGenerator(ABC):
    """Abstract base class for all image generation models."""
    
    @abstractmethod
    def generate(self, input_data: ImageGenInput) -> ImageGenOutput:
        """Generate an image from the provided input."""
        pass
