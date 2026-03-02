from abc import ABC, abstractmethod

from src.modules.pixelization.schemas import PixelizationInput, PixelizationOutput


class BasePixelization(ABC):
    """Abstract base class for all pixelization models."""

    @abstractmethod
    def generate(self, input_data: PixelizationInput) -> PixelizationOutput:
        """Generate a pixelized image from the provided input."""
        pass
