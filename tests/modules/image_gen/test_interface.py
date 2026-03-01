import pytest
from src.modules.image_gen.interface import BaseImageGenerator
from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput

def test_base_image_generator_is_abstract():
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BaseImageGenerator()

def test_base_image_generator_requires_generate():
    class MissingGenerateGenerator(BaseImageGenerator):
        pass

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        MissingGenerateGenerator()

def test_concrete_image_generator():
    class ConcreteGenerator(BaseImageGenerator):
        def generate(self, input_data: ImageGenInput) -> ImageGenOutput:
            return ImageGenOutput(image_path="/path/to/image.png")

    generator = ConcreteGenerator()
    assert isinstance(generator, BaseImageGenerator)
    
    input_data = ImageGenInput(prompt="A test prompt")
    output = generator.generate(input_data)
    assert output.image_path == "/path/to/image.png"
