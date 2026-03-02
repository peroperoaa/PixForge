from abc import ABC, abstractmethod

from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


class BasePostProcessor(ABC):
    """Abstract base class for all post-processing implementations."""

    @abstractmethod
    def process(self, input_data: PostProcessingInput) -> PostProcessingOutput:
        """Process an image through the post-processing pipeline."""
        pass
