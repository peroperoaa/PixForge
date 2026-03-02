import pytest
from src.modules.post_processing.exceptions import (
    PostProcessingError,
    BackgroundRemovalError,
    ColorQuantizationError,
    DownscaleError,
)


def test_post_processing_error_is_base():
    """PostProcessingError is an Exception."""
    error = PostProcessingError("base error")
    assert isinstance(error, Exception)
    assert str(error) == "base error"


def test_background_removal_error_inherits():
    """BackgroundRemovalError inherits from PostProcessingError."""
    error = BackgroundRemovalError("bg removal failed")
    assert isinstance(error, PostProcessingError)
    assert isinstance(error, Exception)


def test_color_quantization_error_inherits():
    """ColorQuantizationError inherits from PostProcessingError."""
    error = ColorQuantizationError("quantization failed")
    assert isinstance(error, PostProcessingError)
    assert isinstance(error, Exception)


def test_downscale_error_inherits():
    """DownscaleError inherits from PostProcessingError."""
    error = DownscaleError("downscale failed")
    assert isinstance(error, PostProcessingError)
    assert isinstance(error, Exception)
