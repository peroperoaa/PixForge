import pytest
from pydantic import ValidationError
from src.modules.pixelization.schemas import PixelizationInput, PixelizationOutput


def test_pixelization_input_all_fields():
    input_data = PixelizationInput(
        image_path="input.png",
        image_bytes=b"fake_bytes",
        prompt="pixel art style",
        denoising_strength=0.75,
    )
    assert input_data.image_path == "input.png"
    assert input_data.image_bytes == b"fake_bytes"
    assert input_data.prompt == "pixel art style"
    assert input_data.denoising_strength == 0.75


def test_pixelization_input_only_required():
    input_data = PixelizationInput(image_path="input.png")
    assert input_data.image_path == "input.png"
    assert input_data.image_bytes is None
    assert input_data.prompt is None
    assert input_data.denoising_strength is None


def test_pixelization_input_missing_image_path():
    with pytest.raises(ValidationError):
        PixelizationInput()


def test_pixelization_output_all_fields():
    output = PixelizationOutput(image_path="output.png", width=64, height=64)
    assert output.image_path == "output.png"
    assert output.width == 64
    assert output.height == 64


def test_pixelization_output_only_required():
    output = PixelizationOutput(image_path="output.png")
    assert output.image_path == "output.png"
    assert output.width is None
    assert output.height is None


def test_pixelization_output_missing_image_path():
    with pytest.raises(ValidationError):
        PixelizationOutput()
