"""Tests for palette_preset support in PostProcessingPipeline."""

import os
from unittest.mock import MagicMock, patch, call

import pytest
from PIL import Image

from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


class TestPipelinePalettePresetUnit:
    """Unit tests for pipeline palette_preset resolution (mocked components)."""

    @pytest.fixture
    def output_dir(self, tmp_path):
        return str(tmp_path / "output")

    def test_resolves_palette_preset_via_get_preset(self, output_dir):
        """Pipeline calls PaletteLoader.get_preset with the preset name and passes
        result palette to ColorQuantizer.quantize."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")
        fake_palette = [(0x1A, 0x1C, 0x2C), (0x5D, 0x27, 0x5D)]

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.PaletteLoader") as MockPL,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockPL.get_preset.return_value = fake_palette

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                palette_preset="sweetie-16",
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            # PaletteLoader.get_preset called with the preset name
            MockPL.get_preset.assert_called_once_with("sweetie-16")

            # ColorQuantizer.quantize receives the palette from get_preset
            MockCQ.return_value.quantize.assert_called_once()
            call_kwargs = MockCQ.return_value.quantize.call_args
            assert call_kwargs[1].get("palette") is fake_palette or call_kwargs[0][0] is downscaled_img

    def test_palette_name_equals_preset_name(self, output_dir):
        """PostProcessingOutput.palette_name equals the preset name when palette_preset is used."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")
        fake_palette = [(0x1A, 0x1C, 0x2C), (0x5D, 0x27, 0x5D)]

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.PaletteLoader") as MockPL,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockPL.get_preset.return_value = fake_palette

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                palette_preset="sweetie-16",
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            assert result.palette_name == "sweetie-16"

    def test_palette_path_still_works_unchanged(self, output_dir):
        """Pipeline still loads palette from file when palette_path is used (no regression)."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")
        fake_palette = [(255, 0, 0), (0, 255, 0)]

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.PaletteLoader") as MockPL,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockPL.load_from_hex_file.return_value = fake_palette

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                palette_path="/palettes/retro.hex",
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            MockPL.load_from_hex_file.assert_called_once_with("/palettes/retro.hex")
            MockPL.get_preset.assert_not_called()
            assert result.palette_name == "retro"

    def test_skip_quantization_when_no_preset_no_path_no_count(self, output_dir):
        """Pipeline skips quantization when palette_preset, palette_path, and color_count are all None."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.PaletteLoader") as MockPL,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.return_value = downscaled_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            MockCQ.return_value.quantize.assert_not_called()
            MockPL.get_preset.assert_not_called()
            MockPL.load_from_hex_file.assert_not_called()
