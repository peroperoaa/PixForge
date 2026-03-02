"""Tests for PostProcessingPipeline."""

import logging
import os
import sys
from unittest.mock import MagicMock, call, patch

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

    def test_downscale_then_quantize_order(self, output_dir):
        """Pipeline downscales first, then quantizes each downscaled image
        at target resolution (mocked components)."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")
        quantized_img = MagicMock(name="quantized")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockCQ.return_value.quantize.return_value = quantized_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32],
                color_count=16,
                output_dir=output_dir,
            )

            result = pipeline.process(input_data)

            # Downscaler receives the original image (downscale first)
            MockDS.return_value.downscale.assert_called_once()
            assert MockDS.return_value.downscale.call_args[0][0] is original_img

            # ColorQuantizer receives the downscaled image (quantize second)
            MockCQ.return_value.quantize.assert_called_once()
            assert MockCQ.return_value.quantize.call_args[0][0] is downscaled_img

            # The quantized image is what gets saved
            quantized_img.save.assert_called_once()

    def test_remove_background_logs_deprecation_warning(self, output_dir, caplog):
        """Pipeline logs deprecation warning when remove_background=True and
        does NOT actually remove background."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
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
                remove_background=True,
                output_dir=output_dir,
            )

            with caplog.at_level(logging.WARNING, logger="src.modules.post_processing.pipeline"):
                pipeline.process(input_data)

            assert any("deprecated" in r.message.lower() for r in caplog.records)
            assert any("remove_background" in r.message for r in caplog.records)

    def test_no_deprecation_warning_when_remove_background_false(self, output_dir, caplog):
        """Pipeline does NOT log deprecation warning when remove_background=False."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
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
                output_dir=output_dir,
            )

            with caplog.at_level(logging.WARNING, logger="src.modules.post_processing.pipeline"):
                pipeline.process(input_data)

            assert not any("deprecated" in r.message.lower() for r in caplog.records)

    def test_skip_quantization_when_both_none(self, output_dir):
        """Pipeline with color_count=None and palette_path=None skips ColorQuantizer
        (mocked, verify not called)."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
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
            # Downscaled image is saved directly (no quantization)
            downscaled_img.save.assert_called_once()

    def test_file_naming_convention(self, output_dir):
        """Pipeline generates files named '{asset_name}_{size}x{size}.png'
        for each target_size (mocked filesystem)."""
        original_img = MagicMock(name="original")
        mock_downscaled_32 = MagicMock(name="downscaled_32")
        mock_downscaled_64 = MagicMock(name="downscaled_64")
        mock_quantized_32 = MagicMock(name="quantized_32")
        mock_quantized_64 = MagicMock(name="quantized_64")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.side_effect = [mock_downscaled_32, mock_downscaled_64]
            MockCQ.return_value.quantize.side_effect = [mock_quantized_32, mock_quantized_64]

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

            mock_quantized_32.save.assert_called_once_with(expected_32)
            mock_quantized_64.save.assert_called_once_with(expected_64)
            assert result.output_paths == [expected_32, expected_64]

    def test_creates_output_dir_if_missing(self, output_dir):
        """Pipeline creates output_dir if it does not exist (mocked os.makedirs)."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")
        quantized_img = MagicMock(name="quantized")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs") as mock_makedirs,
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockCQ.return_value.quantize.return_value = quantized_img

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
        downscaled_img = MagicMock(name="downscaled")
        quantized_img = MagicMock(name="quantized")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.return_value = downscaled_img
            MockCQ.return_value.quantize.return_value = quantized_img

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

    def test_quantize_called_per_target_size(self, output_dir):
        """Pipeline calls quantize once per target size, each on the downscaled image."""
        original_img = MagicMock(name="original")
        downscaled_32 = MagicMock(name="downscaled_32")
        downscaled_64 = MagicMock(name="downscaled_64")
        quantized_32 = MagicMock(name="quantized_32")
        quantized_64 = MagicMock(name="quantized_64")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.ColorQuantizer") as MockCQ,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.side_effect = [downscaled_32, downscaled_64]
            MockCQ.return_value.quantize.side_effect = [quantized_32, quantized_64]

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()
            input_data = PostProcessingInput(
                image_path="input.png",
                asset_name="hero",
                target_sizes=[32, 64],
                color_count=8,
                output_dir=output_dir,
            )

            pipeline.process(input_data)

            # Quantize called twice - once per target size
            assert MockCQ.return_value.quantize.call_count == 2
            # Each call receives the corresponding downscaled image
            assert MockCQ.return_value.quantize.call_args_list[0][0][0] is downscaled_32
            assert MockCQ.return_value.quantize.call_args_list[1][0][0] is downscaled_64

    def test_no_background_remover_usage(self, output_dir):
        """Pipeline does not use BackgroundRemover even when remove_background=True."""
        original_img = MagicMock(name="original")
        downscaled_img = MagicMock(name="downscaled")

        with (
            patch("src.modules.post_processing.pipeline.Image") as MockImage,
            patch("src.modules.post_processing.pipeline.Downscaler") as MockDS,
            patch("src.modules.post_processing.pipeline.os.makedirs"),
        ):
            MockImage.open.return_value = original_img
            MockDS.return_value.downscale.return_value = downscaled_img

            from src.modules.post_processing.pipeline import PostProcessingPipeline

            pipeline = PostProcessingPipeline()

            # Verify pipeline has no _background_remover attribute
            assert not hasattr(pipeline, "_background_remover")


# ---------------------------------------------------------------------------
# Integration Tests (real components)
# ---------------------------------------------------------------------------
class TestPipelineIntegration:
    """Integration tests with real ColorQuantizer and Downscaler."""

    def test_full_chain_downscale_then_quantize(self, tmp_path):
        """Pipeline with real ColorQuantizer and real Downscaler produces
        correct-dimension output files; downscale happens before quantize."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(256, 256), mode="RGBA")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="test_sprite",
            target_sizes=[32, 64],
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

    def test_full_chain_real_256_image(self, tmp_path):
        """Pipeline processes a real 256x256 RGBA test image through full chain
        and saves to temp directory with correct filenames."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(256, 256), mode="RGBA")
        input_path = str(tmp_path / "test_input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="pixel_art",
            target_sizes=[16, 32, 64],
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
        palette mode via PaletteLoader and ColorQuantizer at target resolution."""
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

    def test_deprecation_warning_integration(self, tmp_path, caplog):
        """Integration test: remove_background=True logs deprecation warning
        but pipeline still completes successfully."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(64, 64), mode="RGB")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="warn_test",
            target_sizes=[32],
            remove_background=True,
            color_count=4,
            output_dir=output_dir,
        )

        with caplog.at_level(logging.WARNING, logger="src.modules.post_processing.pipeline"):
            result = pipeline.process(input_data)

        assert any("deprecated" in r.message.lower() for r in caplog.records)
        assert len(result.output_paths) == 1
        assert os.path.exists(result.output_paths[0])

    def test_quantization_at_target_resolution_no_mixed_colors(self, tmp_path):
        """Verify quantization happens at target resolution: downscaling first means
        quantization sees the small image, guaranteeing no sub-pixel color mixing."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        # Create image with clear color boundaries
        img = _make_test_image(size=(256, 256), mode="RGB")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="color_test",
            target_sizes=[16],
            color_count=4,
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        out_img = Image.open(result.output_paths[0])
        assert out_img.size == (16, 16)

        # Count unique colors - should be at most 4 (the quantized palette)
        import numpy as np
        arr = np.array(out_img.convert("RGB"))
        pixels = arr.reshape(-1, 3)
        unique_colors = np.unique(pixels, axis=0)
        assert len(unique_colors) <= 4
