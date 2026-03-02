"""Tests for PostProcessingPipeline."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


def _make_test_image(size=(256, 256), mode="RGBA"):
    """Create a test PIL Image with 4 distinct color quadrants."""
    if mode == "RGBA":
        img = Image.new("RGBA", size, (0, 0, 0, 255))
        hw, hh = size[0] // 2, size[1] // 2
        img.paste(Image.new("RGBA", (hw, hh), (255, 0, 0, 255)), (0, 0))
        img.paste(Image.new("RGBA", (hw, hh), (0, 255, 0, 255)), (hw, 0))
        img.paste(Image.new("RGBA", (hw, hh), (0, 0, 255, 255)), (0, hh))
        img.paste(Image.new("RGBA", (hw, hh), (255, 255, 255, 255)), (hw, hh))
        return img
    else:
        img = Image.new("RGB", size, (0, 0, 0))
        hw, hh = size[0] // 2, size[1] // 2
        img.paste(Image.new("RGB", (hw, hh), (255, 0, 0)), (0, 0))
        img.paste(Image.new("RGB", (hw, hh), (0, 255, 0)), (hw, 0))
        img.paste(Image.new("RGB", (hw, hh), (0, 0, 255)), (0, hh))
        img.paste(Image.new("RGB", (hw, hh), (255, 255, 255)), (hw, hh))
        return img


# ---------------------------------------------------------------------------
# Unit Tests (mocked components)
# ---------------------------------------------------------------------------
class TestPipelineUnit:
    """Unit tests with fully mocked components."""

    @pytest.fixture
    def output_dir(self, tmp_path):
        return str(tmp_path / "output")

    def test_all_steps_calls_components_in_order(self, output_dir):
        """Pipeline with all steps enabled calls BackgroundRemover, ColorQuantizer,
        and Downscaler in correct order (mocked components)."""
        original_img = MagicMock(name="original")
        bg_removed_img = MagicMock(name="bg_removed")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover") as MockBR,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockBR.return_value.remove.return_value = bg_removed_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                remove_background=True,
                color_count=16,
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            # BackgroundRemover receives the original image
            MockBR.return_value.remove.assert_called_once()
            assert MockBR.return_value.remove.call_args[0][0] is original_img

            # ColorQuantizer receives the bg-removed image
            MockCQ.return_value.quantize.assert_called_once()
            assert MockCQ.return_value.quantize.call_args[0][0] is bg_removed_img

            # Downscaler receives the quantized image
            MockDS.return_value.downscale.assert_called_once()
            assert MockDS.return_value.downscale.call_args[0][0] is quantized_img

    def test_skip_bg_removal_when_false(self, output_dir):
        """Pipeline with remove_background=False skips BackgroundRemover
        (mocked, verify not called)."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover") as MockBR,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                remove_background=False,
                color_count=16,
                output_dir=output_dir,
            )

            pipeline.process(input_data)

            MockBR.return_value.remove.assert_not_called()
            # Quantizer receives the original image directly
            assert MockCQ.return_value.quantize.call_args[0][0] is original_img

    def test_skip_quantization_when_both_none(self, output_dir):
        """Pipeline with color_count=None and palette_path=None skips ColorQuantizer
        (mocked, verify not called)."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover") as MockBR,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
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
                remove_background=False,
                color_count=None,
                palette_path=None,
                output_dir=output_dir,
            )

            pipeline.process(input_data)

            MockCQ.return_value.quantize.assert_not_called()
            # Downscaler receives the original image directly
            assert MockDS.return_value.downscale.call_args[0][0] is original_img

    def test_file_naming_convention(self, output_dir):
        """Pipeline generates files named '{asset_name}_{size}x{size}.png'
        for each target_size (mocked filesystem)."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        mock_resized_32 = MagicMock(name="resized_32")
        mock_resized_64 = MagicMock(name="resized_64")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover"),
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.side_effect = [mock_resized_32, mock_resized_64]

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[32, 64],
                color_count=16,
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            expected_32 = os.path.join(output_dir, "hero_sprite_32x32.png")
            expected_64 = os.path.join(output_dir, "hero_sprite_64x64.png")

            mock_resized_32.save.assert_called_once_with(expected_32)
            mock_resized_64.save.assert_called_once_with(expected_64)
            assert result.output_paths == [expected_32, expected_64]

    def test_creates_output_dir_if_missing(self, output_dir):
        """Pipeline creates output_dir if it does not exist (mocked os.makedirs)."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover"),
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs") as mock_makedirs,
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = downscaled_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                color_count=16,
                output_dir=output_dir,
            )

            pipeline.process(input_data)

            mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)

    def test_output_paths_match_target_sizes_count(self, output_dir):
        """Pipeline returns PostProcessingOutput with output_paths matching
        number of target_sizes."""
        original_img = MagicMock(name="original")
        quantized_img = MagicMock(name="quantized")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.BackgroundRemover"),
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockCQ.return_value.quantize.return_value = quantized_img
            MockDS.return_value.downscale.return_value = MagicMock()

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            sizes = [16, 32, 64, 128]
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=sizes,
                color_count=16,
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            assert isinstance(result, PostProcessingOutput)
            assert len(result.output_paths) == len(sizes)
            assert result.target_sizes == sizes
            assert result.color_count == 16


# ---------------------------------------------------------------------------
# Integration Tests (real components, mocked rembg)
# ---------------------------------------------------------------------------
class TestPipelineIntegration:
    """Integration tests with real BackgroundRemover/ColorQuantizer/Downscaler."""

    @pytest.fixture
    def mock_rembg(self):
        """Mock the rembg module to avoid requiring it as a real dependency."""
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"rembg": mock_module}):
            yield mock_module

    def test_full_chain_with_real_components(self, tmp_path, mock_rembg):
        """Pipeline with real BackgroundRemover (mocked rembg), real ColorQuantizer,
        and real Downscaler produces correct-dimension output files on temp filesystem."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(256, 256), mode="RGBA")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        # rembg.remove returns the same image (RGBA)
        mock_rembg.remove.return_value = img

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="test_sprite",
            target_sizes=[32, 64],
            remove_background=True,
            color_count=4,
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        assert len(result.output_paths) == 2
        for path in result.output_paths:
            assert os.path.exists(path)

        img_32 = Image.open(result.output_paths[0])
        assert img_32.size == (32, 32)
        img_64 = Image.open(result.output_paths[1])
        assert img_64.size == (64, 64)

    def test_full_chain_real_256_image(self, tmp_path, mock_rembg):
        """Pipeline processes a real 256x256 RGBA test image through full chain
        and saves to temp directory with correct filenames."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(256, 256), mode="RGBA")
        input_path = str(tmp_path / "test_input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        mock_rembg.remove.return_value = img

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="pixel_art",
            target_sizes=[16, 32, 64],
            remove_background=True,
            color_count=4,
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        assert os.path.exists(os.path.join(output_dir, "pixel_art_16x16.png"))
        assert os.path.exists(os.path.join(output_dir, "pixel_art_32x32.png"))
        assert os.path.exists(os.path.join(output_dir, "pixel_art_64x64.png"))
        assert len(result.output_paths) == 3

    def test_palette_mode_with_hex_file(self, tmp_path):
        """Pipeline with palette_path pointing to a real .hex file quantizes using
        palette mode via PaletteLoader and ColorQuantizer."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        # Create a .hex palette file
        palette_path = str(tmp_path / "test_palette.hex")
        with open(palette_path, "w") as f:
            f.write("FF0000\n")
            f.write("00FF00\n")
            f.write("0000FF\n")
            f.write("FFFFFF\n")

        img = _make_test_image(size=(64, 64), mode="RGB")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="palette_test",
            target_sizes=[32],
            palette_path=palette_path,
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        assert len(result.output_paths) == 1
        assert os.path.exists(result.output_paths[0])
        assert result.palette_name == "test_palette"

        out_img = Image.open(result.output_paths[0])
        assert out_img.size == (32, 32)
