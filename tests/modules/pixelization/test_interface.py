import pytest
from src.modules.pixelization.interface import BasePixelization
from src.modules.pixelization.schemas import PixelizationInput, PixelizationOutput


def test_base_pixelization_is_abstract():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePixelization()


def test_base_pixelization_requires_generate():
    class MissingGeneratePixelization(BasePixelization):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        MissingGeneratePixelization()


def test_concrete_pixelization():
    class ConcretePixelization(BasePixelization):
        def generate(self, input_data: PixelizationInput) -> PixelizationOutput:
            return PixelizationOutput(image_path="/path/to/pixel.png", width=32, height=32)

    pixelizer = ConcretePixelization()
    assert isinstance(pixelizer, BasePixelization)

    input_data = PixelizationInput(image_path="input.png")
    output = pixelizer.generate(input_data)
    assert output.image_path == "/path/to/pixel.png"
    assert output.width == 32
    assert output.height == 32
