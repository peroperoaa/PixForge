from abc import ABC, abstractmethod

from src.modules.pre_processing.schemas import PreProcessingInput, PreProcessingOutput


class BasePreProcessor(ABC):
    """Abstract base class for all pre-processing implementations."""

    @abstractmethod
    def process(self, input_data: PreProcessingInput) -> PreProcessingOutput:
        """Process an image through the pre-processing pipeline."""
        pass
