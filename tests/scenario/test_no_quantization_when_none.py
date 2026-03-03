"""Tests for FR-2: No quantization when palette and colors are both None."""

import os
from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from PIL import Image

from src.modules.post_processing.pipeline import PostProcessingPipeline
from src.modules.post_processing.schemas import PostProcessingInput


@pytest.fixture
def sample_image(tmp_path):
    """Create a small test image and return its path."""
    img = Image.new("RGBA", (64, 64), (255, 0, 0, 255))
    path = str(tmp_path / "test.png")
    img.save(path)
    return path


class TestNoQuantizationWhenNone:
    """Verify that PostProcessingPipeline skips quantization when palette and colors are both None."""

    # Case 1: No quantization when all palette/color fields are None
    def test_no_quantization_when_all_none(self, sample_image, tmp_path):
        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=sample_image,
            asset_name="test_asset",
            target_sizes=[32],
            palette_preset=None,
            palette_path=None,
            color_count=None,
            output_dir=str(tmp_path / "out"),
        )
        with patch.object(pipeline._color_quantizer, "quantize") as mock_quantize:
            result = pipeline.process(input_data)
            mock_quantize.assert_not_called()
        assert len(result.output_paths) == 1
        assert os.path.exists(result.output_paths[0])

    # Case 2: Quantization occurs with explicit palette_preset
    def test_quantization_with_explicit_palette(self, sample_image, tmp_path):
        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=sample_image,
            asset_name="test_asset",
            target_sizes=[32],
            palette_preset="sweetie-16",
            color_count=None,
            output_dir=str(tmp_path / "out"),
        )
        with patch.object(pipeline._color_quantizer, "quantize", wraps=pipeline._color_quantizer.quantize) as mock_quantize:
            result = pipeline.process(input_data)
            mock_quantize.assert_called_once()

    # Case 3: Quantization occurs with explicit color_count
    def test_quantization_with_explicit_color_count(self, sample_image, tmp_path):
        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=sample_image,
            asset_name="test_asset",
            target_sizes=[32],
            palette_preset=None,
            color_count=8,
            output_dir=str(tmp_path / "out"),
        )
        with patch.object(pipeline._color_quantizer, "quantize", wraps=pipeline._color_quantizer.quantize) as mock_quantize:
            result = pipeline.process(input_data)
            mock_quantize.assert_called_once()

    # Case 4: Output metadata when no quantization
    def test_output_metadata_no_quantization(self, sample_image, tmp_path):
        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=sample_image,
            asset_name="test_asset",
            target_sizes=[32],
            palette_preset=None,
            palette_path=None,
            color_count=None,
            output_dir=str(tmp_path / "out"),
        )
        result = pipeline.process(input_data)
        assert result.palette_name is None
        assert result.color_count is None
