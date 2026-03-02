import pytest
from src.modules.pixelization.exceptions import (
    PixelizationError,
    ComfyUIConnectionError,
    ComfyUITimeoutError,
    ComfyUIWorkflowError,
)


def test_pixelization_error():
    with pytest.raises(PixelizationError, match="base error"):
        raise PixelizationError("base error")


def test_comfyui_connection_error_is_pixelization_error():
    err = ComfyUIConnectionError("connection refused")
    assert isinstance(err, PixelizationError)


def test_comfyui_timeout_error_is_pixelization_error():
    err = ComfyUITimeoutError("request timed out")
    assert isinstance(err, PixelizationError)


def test_comfyui_workflow_error_is_pixelization_error():
    err = ComfyUIWorkflowError("invalid workflow")
    assert isinstance(err, PixelizationError)


def test_catch_all_comfyui_errors_via_base():
    """Catching PixelizationError should also catch all ComfyUI sub-exceptions."""
    for exc_class in (ComfyUIConnectionError, ComfyUITimeoutError, ComfyUIWorkflowError):
        with pytest.raises(PixelizationError):
            raise exc_class("caught via base")
