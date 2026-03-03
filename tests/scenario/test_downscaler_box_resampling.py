"""Tests for Downscaler BOX resampling behavior."""

import pytest
from PIL import Image

from src.modules.post_processing.downscaler import Downscaler
from src.modules.post_processing.exceptions import DownscaleError


class TestDownscalerBoxResampling:
    """Tests verifying Downscaler uses BOX (area-average) resampling."""

    def test_mixed_block_area_averaging(self):
        """4x4 image with mixed pixels in each block, downscaled to 2x2,
        produces averaged colors — proving BOX area-averaging, not NEAREST sampling.

        Top-left 2x2 block pixels: (0,0,0), (200,0,0), (0,200,0), (0,0,200)
        BOX average: (50, 50, 50)
        NEAREST would pick a single pixel, e.g. (0,0,0).
        """
        img = Image.new("RGB", (4, 4), (0, 0, 0))
        pixels = img.load()
        # Top-left block
        pixels[0, 0] = (0, 0, 0)
        pixels[1, 0] = (200, 0, 0)
        pixels[0, 1] = (0, 200, 0)
        pixels[1, 1] = (0, 0, 200)
        # Top-right block — all white
        pixels[2, 0] = (255, 255, 255)
        pixels[3, 0] = (255, 255, 255)
        pixels[2, 1] = (255, 255, 255)
        pixels[3, 1] = (255, 255, 255)

        ds = Downscaler()
        result = ds.downscale(img, 2)
        rp = result.load()
        # BOX: average of (0,200,0,0)/4=50 per channel for top-left
        assert rp[0, 0] == (50, 50, 50), f"Expected area-averaged (50,50,50), got {rp[0, 0]}"
        # Top-right block is solid white
        assert rp[1, 0] == (255, 255, 255)

    def test_solid_color_preserved(self):
        """100x100 solid-color image downscaled to 10x10 preserves exact color.

        BOX averaging of identical pixels must produce the same color.
        """
        color = (42, 137, 200)
        img = Image.new("RGB", (100, 100), color)
        ds = Downscaler()
        result = ds.downscale(img, 10)
        assert result.size == (10, 10)
        # Every pixel should be the original color
        for y in range(10):
            for x in range(10):
                assert result.getpixel((x, y)) == color

    def test_error_on_non_positive_target(self):
        """target_size <= 0 still raises DownscaleError after BOX switch."""
        img = Image.new("RGB", (64, 64))
        ds = Downscaler()
        with pytest.raises(DownscaleError):
            ds.downscale(img, 0)
        with pytest.raises(DownscaleError):
            ds.downscale(img, -5)
