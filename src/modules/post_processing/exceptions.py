class PostProcessingError(Exception):
    """Base exception for errors in the post-processing process."""
    pass


class BackgroundRemovalError(PostProcessingError):
    """Exception raised when background removal fails."""
    pass


class ColorQuantizationError(PostProcessingError):
    """Exception raised when color quantization fails."""
    pass


class DownscaleError(PostProcessingError):
    """Exception raised when image downscaling fails."""
    pass
