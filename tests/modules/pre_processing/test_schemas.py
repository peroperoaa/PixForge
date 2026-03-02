import pytest
from pydantic import ValidationError


class TestPreProcessingInput:
    def test_accepts_all_defaults(self):
        """PreProcessingInput with only image_path uses defaults: intermediate_size=256, remove_background=False, crop_mode='auto'."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        input_data = PreProcessingInput(image_path="test.png")
        assert input_data.image_path == "test.png"
        assert input_data.remove_background is False
        assert input_data.intermediate_size == 256
        assert input_data.crop_mode == "auto"

    def test_accepts_custom_values(self):
        """PreProcessingInput accepts custom intermediate_size=128, remove_background=True, crop_mode='center'."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        input_data = PreProcessingInput(
            image_path="input.png",
            remove_background=True,
            intermediate_size=128,
            crop_mode="center",
        )
        assert input_data.remove_background is True
        assert input_data.intermediate_size == 128
        assert input_data.crop_mode == "center"

    def test_rejects_non_positive_intermediate_size(self):
        """PreProcessingInput rejects intermediate_size <= 0."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        with pytest.raises(ValidationError):
            PreProcessingInput(image_path="test.png", intermediate_size=0)
        with pytest.raises(ValidationError):
            PreProcessingInput(image_path="test.png", intermediate_size=-10)

    def test_rejects_invalid_crop_mode(self):
        """PreProcessingInput rejects invalid crop_mode values (not 'auto' or 'center')."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        with pytest.raises(ValidationError):
            PreProcessingInput(image_path="test.png", crop_mode="invalid")

    def test_accepts_output_dir(self):
        """PreProcessingInput accepts optional output_dir."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        input_data = PreProcessingInput(image_path="test.png", output_dir="/tmp/out")
        assert input_data.output_dir == "/tmp/out"

    def test_output_dir_defaults_to_none(self):
        """PreProcessingInput output_dir defaults to None."""
        from src.modules.pre_processing.schemas import PreProcessingInput

        input_data = PreProcessingInput(image_path="test.png")
        assert input_data.output_dir is None


class TestPreProcessingOutput:
    def test_accepts_valid_fields(self):
        """PreProcessingOutput accepts image_path, original_size, intermediate_size."""
        from src.modules.pre_processing.schemas import PreProcessingOutput

        output = PreProcessingOutput(
            image_path="output.png",
            original_size=(512, 512),
            intermediate_size=256,
        )
        assert output.image_path == "output.png"
        assert output.original_size == (512, 512)
        assert output.intermediate_size == 256

    def test_original_size_is_tuple(self):
        """PreProcessingOutput original_size is a tuple of two ints."""
        from src.modules.pre_processing.schemas import PreProcessingOutput

        output = PreProcessingOutput(
            image_path="output.png",
            original_size=(1920, 1080),
            intermediate_size=256,
        )
        assert len(output.original_size) == 2
        assert all(isinstance(x, int) for x in output.original_size)
