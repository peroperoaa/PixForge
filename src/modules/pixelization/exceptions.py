class PixelizationError(Exception):
    """Base exception for errors in the pixelization process."""
    pass


class ComfyUIConnectionError(PixelizationError):
    """Exception raised when a connection to ComfyUI fails."""
    pass


class ComfyUITimeoutError(PixelizationError):
    """Exception raised when a ComfyUI request times out."""
    pass


class ComfyUIWorkflowError(PixelizationError):
    """Exception raised when a ComfyUI workflow encounters an error."""
    pass
