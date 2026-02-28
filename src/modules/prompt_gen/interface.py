from abc import ABC, abstractmethod
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput

class BasePromptGenerator(ABC):
    """Abstract base class for prompt generation providers."""
    
    @abstractmethod
    def generate(self, input: PromptInput) -> PromptOutput:
        """
        Generate a prompt output from a given input.

        Args:
            input (PromptInput): The input configuration.

        Returns:
            PromptOutput: The generated positive/negative prompts and style parameters.
        """
        pass
