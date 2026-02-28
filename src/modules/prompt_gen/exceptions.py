class PromptGenerationError(Exception):
    """Base exception for prompt generation errors."""
    pass

class APIConnectionError(PromptGenerationError):
    """Raised when the API call fails due to network or authentication issues."""
    pass

class PromptParsingError(PromptGenerationError):
    """Raised when the output from the model cannot be parsed into the expected format."""
    pass
