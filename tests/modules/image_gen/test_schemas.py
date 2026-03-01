import pytest
from pydantic import ValidationError
from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput

def test_image_gen_input_valid():
    input_data = ImageGenInput(prompt="A test prompt", image_path="input.png")
    assert input_data.prompt == "A test prompt"
    assert input_data.image_path == "input.png"

def test_image_gen_input_optional_image_path():
    input_data = ImageGenInput(prompt="A test prompt")
    assert input_data.prompt == "A test prompt"
    assert input_data.image_path is None

def test_image_gen_input_missing_prompt():
    with pytest.raises(ValidationError):
        ImageGenInput()

def test_image_gen_output_valid():
    output = ImageGenOutput(image_path="output.png")
    assert output.image_path == "output.png"

def test_image_gen_output_missing_image_path():
    with pytest.raises(ValidationError):
        ImageGenOutput()
