class PreProcessingError(Exception):
    """Base exception for errors in the pre-processing process."""
    pass


class BackgroundRemovalError(PreProcessingError):
    """Exception raised when background removal fails."""
    pass


class CropError(PreProcessingError):
    """Exception raised when image cropping fails."""
    pass


class DownscaleError(PreProcessingError):
    """Exception raised when image downscaling fails."""
    pass
