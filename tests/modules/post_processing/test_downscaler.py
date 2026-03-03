"""Tests for Downscaler - BOX (area-average) image downscaling."""

import pytest
from PIL import Image

from src.modules.post_processing.downscaler import Downscaler
from src.modules.post_processing.exceptions import DownscaleError


class TestDownscaleSingle:
    """Tests for Downscaler.downscale (FR-1)."""

    def test_downscale_256_rgba_to_32(self):
        """256x256 RGBA image downscaled to 32 produces exactly 32x32."""
        img = Image.new("RGBA", (256, 256), (255, 0, 0, 255))
        ds = Downscaler()
        result = ds.downscale(img, 32)
        assert result.size == (32, 32)

    def test_downscale_512_rgb_to_64(self):
        """512x512 RGB image downscaled to 64 produces exactly 64x64."""
        img = Image.new("RGB", (512, 512), (0, 128, 255))
        ds = Downscaler()
        result = ds.downscale(img, 64)
        assert result.size == (64, 64)

    def test_downscale_preserves_rgba_mode(self):
        """Downscale preserves RGBA mode (alpha channel not dropped)."""
        img = Image.new("RGBA", (128, 128), (10, 20, 30, 128))
        ds = Downscaler()
        result = ds.downscale(img, 32)
        assert result.mode == "RGBA"

    def test_downscale_box_solid_blocks(self):
        """4x4 checkerboard (solid 2x2 blocks) scaled to 2x2 preserves block colors with BOX."""
        # Build a 4x4 checkerboard: top-left 2x2 = black, top-right 2x2 = white, etc.
        img = Image.new("RGB", (4, 4))
        black = (0, 0, 0)
        white = (255, 255, 255)
        pixels = img.load()
        for y in range(4):
            for x in range(4):
                # 2x2 block checkerboard
                if (x // 2 + y // 2) % 2 == 0:
                    pixels[x, y] = black
                else:
                    pixels[x, y] = white

        ds = Downscaler()
        result = ds.downscale(img, 2)
        rp = result.load()
        # With BOX from 4x4 to 2x2, each output pixel averages its 2x2 source block.
        # Since each block is solid, the average equals the block color.
        assert rp[0, 0] == black
        assert rp[1, 0] == white
        assert rp[0, 1] == white
        assert rp[1, 1] == black

    def test_downscale_raises_on_zero_target(self):
        """DownscaleError raised when target size is 0."""
        img = Image.new("RGB", (64, 64))
        ds = Downscaler()
        with pytest.raises(DownscaleError):
            ds.downscale(img, 0)

    def test_downscale_raises_on_negative_target(self):
        """DownscaleError raised when target size is negative."""
        img = Image.new("RGB", (64, 64))
        ds = Downscaler()
        with pytest.raises(DownscaleError):
            ds.downscale(img, -5)

    def test_downscale_non_square_source(self):
        """Non-square 256x128 image downscaled to 32 produces 32x32 output."""
        img = Image.new("RGB", (256, 128), (100, 150, 200))
        ds = Downscaler()
        result = ds.downscale(img, 32)
        assert result.size == (32, 32)


class TestDownscaleMulti:
    """Tests for Downscaler.downscale_multi (FR-2)."""

    def test_downscale_multi_returns_correct_count_and_sizes(self):
        """downscale_multi with [32, 64, 128] returns 3 images with matching dims."""
        img = Image.new("RGBA", (256, 256), (0, 255, 0, 255))
        ds = Downscaler()
        sizes = [32, 64, 128]
        results = ds.downscale_multi(img, sizes)
        assert len(results) == 3
        for result, size in zip(results, sizes):
            assert result.size == (size, size)
