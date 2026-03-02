"""Integration tests for palette_preset support end-to-end."""

import os

import numpy as np
import pytest
from PIL import Image

from src.modules.post_processing.palette_loader import PaletteLoader
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


def _make_test_image(size=(64, 64), mode="RGB"):
    """Create a test PIL Image with 4 distinct color quadrants."""
    img = Image.new(mode, size, (0, 0, 0) if mode == "RGB" else (0, 0, 0, 255))
    hw, hh = size[0] // 2, size[1] // 2
    if mode == "RGB":
        img.paste(Image.new("RGB", (hw, hh), (255, 0, 0)), (0, 0))
        img.paste(Image.new("RGB", (hw, hh), (0, 255, 0)), (hw, 0))
        img.paste(Image.new("RGB", (hw, hh), (0, 0, 255)), (0, hh))
        img.paste(Image.new("RGB", (hw, hh), (255, 255, 255)), (hw, hh))
    else:
        img.paste(Image.new("RGBA", (hw, hh), (255, 0, 0, 255)), (0, 0))
        img.paste(Image.new("RGBA", (hw, hh), (0, 255, 0, 255)), (hw, 0))
        img.paste(Image.new("RGBA", (hw, hh), (0, 0, 255, 255)), (0, hh))
        img.paste(Image.new("RGBA", (hw, hh), (255, 255, 255, 255)), (hw, hh))
    return img


class TestPalettePresetIntegration:
    """Integration tests with real components for palette_preset."""

    def test_sweetie16_preset_end_to_end(self, tmp_path):
        """Pipeline with palette_preset='sweetie-16' processes image and output uses only sweetie-16 colors."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(64, 64), mode="RGB")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="preset_test",
            target_sizes=[32],
            palette_preset="sweetie-16",
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        assert len(result.output_paths) == 1
        assert os.path.exists(result.output_paths[0])
        assert result.palette_name == "sweetie-16"

        # Verify output image only uses sweetie-16 palette colors
        out_img = Image.open(result.output_paths[0])
        assert out_img.size == (32, 32)

        sweetie16_palette = set(tuple(c) for c in PaletteLoader.get_preset("sweetie-16"))
        pixels = np.array(out_img)
        unique_colors = set(tuple(c) for c in pixels.reshape(-1, 3))
        assert unique_colors.issubset(sweetie16_palette)

    def test_gb_preset_end_to_end(self, tmp_path):
        """Pipeline with palette_preset='gb' processes image and output uses only GB palette colors."""
        from src.modules.post_processing.pipeline import PostProcessingPipeline

        img = _make_test_image(size=(64, 64), mode="RGB")
        input_path = str(tmp_path / "input.png")
        img.save(input_path)
        output_dir = str(tmp_path / "output")

        pipeline = PostProcessingPipeline()
        input_data = PostProcessingInput(
            image_path=input_path,
            asset_name="gb_test",
            target_sizes=[16],
            palette_preset="gb",
            output_dir=output_dir,
        )

        result = pipeline.process(input_data)

        assert len(result.output_paths) == 1
        assert os.path.exists(result.output_paths[0])
        assert result.palette_name == "gb"

        gb_palette = set(tuple(c) for c in PaletteLoader.get_preset("gb"))
        out_img = Image.open(result.output_paths[0])
        pixels = np.array(out_img)
        unique_colors = set(tuple(c) for c in pixels.reshape(-1, 3))
        assert unique_colors.issubset(gb_palette)
