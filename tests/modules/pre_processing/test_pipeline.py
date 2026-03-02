"""Tests for PreProcessor process pipeline."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


def _make_test_image(size=(512, 512), mode="RGB"):
    """Create a test PIL Image."""
    img = Image.new(mode, size, (255, 0, 0))
    return img


def _save_test_image(path, size=(512, 512), mode="RGB"):
    """Save a test image to disk and return the path."""
    img = _make_test_image(size, mode)
    img.save(path)
    return path


class TestPreProcessorUnit:
    """Unit tests for PreProcessor with mocked dependencies."""

    @pytest.fixture
    def output_dir(self, tmp_path):
        return str(tmp_path / "output")

    @pytest.fixture
    def input_image_path(self, tmp_path):
        path = str(tmp_path / "input.png")
        _save_test_image(path, size=(512, 512), mode="RGB")
        return path

    @pytest.fixture
    def input_image_path_nonsquare(self, tmp_path):
        path = str(tmp_path / "input_nonsquare.png")
        _save_test_image(path, size=(640, 480), mode="RGB")
        return path

    def test_process_default_produces_256_square(self, input_image_path, output_dir):
        """Process a 512x512 RGB image with defaults produces a 256x256 PNG."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor

        input_data = PreProcessingInput(
            image_path=input_image_path,
            output_dir=output_dir,
        )
        result = PreProcessor().process(input_data)

        assert os.path.exists(result.image_path)
        output_img = Image.open(result.image_path)
        assert output_img.size == (256, 256)
        assert result.intermediate_size == 256
        assert result.original_size == (512, 512)

    def test_process_custom_size_128(self, input_image_path, output_dir):
        """Process with intermediate_size=128 produces 128x128 output."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor

        input_data = PreProcessingInput(
            image_path=input_image_path,
            intermediate_size=128,
            output_dir=output_dir,
        )
        result = PreProcessor().process(input_data)

        output_img = Image.open(result.image_path)
        assert output_img.size == (128, 128)
        assert result.intermediate_size == 128

    def test_process_nonsquare_input_crops_to_square(self, input_image_path_nonsquare, output_dir):
        """Process a 640x480 image crops to square first, then downscales to 256x256."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor

        input_data = PreProcessingInput(
            image_path=input_image_path_nonsquare,
            output_dir=output_dir,
        )
        result = PreProcessor().process(input_data)

        output_img = Image.open(result.image_path)
        assert output_img.size == (256, 256)
        assert result.original_size == (640, 480)

    def test_process_with_background_removal(self, input_image_path, output_dir):
        """Process with remove_background=True calls background removal before cropping."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor

        rgba_img = Image.new("RGBA", (512, 512), (255, 0, 0, 128))

        with patch("src.modules.pre_processing.pipeline.BackgroundRemover") as MockBR:
            MockBR.return_value.remove.return_value = rgba_img

            input_data = PreProcessingInput(
                image_path=input_image_path,
                remove_background=True,
                output_dir=output_dir,
            )
            result = PreProcessor().process(input_data)

            MockBR.return_value.remove.assert_called_once()
            assert os.path.exists(result.image_path)

    def test_process_uses_lanczos_resampling(self, input_image_path, output_dir):
        """Process uses LANCZOS resampling (not NEAREST) for smooth intermediate output."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor

        input_data = PreProcessingInput(
            image_path=input_image_path,
            output_dir=output_dir,
        )

        with patch("src.modules.pre_processing.pipeline.Image") as MockImage:
            real_img = Image.open(input_image_path)
            MockImage.open.return_value = real_img
            MockImage.LANCZOS = Image.LANCZOS

            mock_cropped = MagicMock()
            mock_resized = MagicMock()
            mock_cropped.resize.return_value = mock_resized
            mock_resized.save = MagicMock()

            with patch.object(PreProcessor, '_crop_square', return_value=mock_cropped):
                result = PreProcessor().process(input_data)
                mock_cropped.resize.assert_called_once_with(
                    (256, 256), Image.LANCZOS
                )

    def test_process_nonexistent_image_raises_error(self, output_dir):
        """Process with nonexistent image_path raises PreProcessingError."""
        from src.modules.pre_processing.schemas import PreProcessingInput
        from src.modules.pre_processing.pipeline import PreProcessor
        from src.modules.pre_processing.exceptions import PreProcessingError

        input_data = PreProcessingInput(
            image_path="/nonexistent/path/image.png",
            output_dir=output_dir,
        )
        with pytest.raises(PreProcessingError):
            PreProcessor().process(input_data)

    def test_process_returns_correct_output_schema(self, input_image_path, output_dir):
        """Process returns PreProcessingOutput with correct fields."""
        from src.modules.pre_processing.schemas import PreProcessingInput, PreProcessingOutput
        from src.modules.pre_processing.pipeline import PreProcessor

        input_data = PreProcessingInput(
            image_path=input_image_path,
            output_dir=output_dir,
        )
        result = PreProcessor().process(input_data)

        assert isinstance(result, PreProcessingOutput)
        assert isinstance(result.image_path, str)
        assert isinstance(result.original_size, tuple)
        assert isinstance(result.intermediate_size, int)
