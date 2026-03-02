"""Tests for ColorQuantizer class."""

import numpy as np
import pytest
from PIL import Image

from src.modules.post_processing.color_quantizer import ColorQuantizer
from src.modules.post_processing.exceptions import ColorQuantizationError
from src.modules.post_processing.palette_loader import PaletteLoader


class TestQuantizeKmeans:
    """Tests for quantize_kmeans method."""

    def test_kmeans_reduces_to_n_colors(self):
        """quantize_kmeans with N=4 on a 10x10 image with 100 random colors produces at most 4 unique RGB values."""
        np.random.seed(42)
        data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize_kmeans(image, n_colors=4)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert len(unique_colors) <= 4

    def test_kmeans_preserves_exact_colors(self):
        """quantize_kmeans with N=2 on a pure red/blue checkerboard returns exactly red and blue."""
        data = np.zeros((10, 10, 3), dtype=np.uint8)
        for i in range(10):
            for j in range(10):
                if (i + j) % 2 == 0:
                    data[i, j] = [255, 0, 0]  # red
                else:
                    data[i, j] = [0, 0, 255]  # blue
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize_kmeans(image, n_colors=2)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert unique_colors == {(255, 0, 0), (0, 0, 255)}

    def test_kmeans_raises_error_when_n_less_than_2(self):
        """quantize_kmeans raises ColorQuantizationError when N < 2."""
        image = Image.new("RGB", (10, 10), (128, 128, 128))

        quantizer = ColorQuantizer()
        with pytest.raises(ColorQuantizationError):
            quantizer.quantize_kmeans(image, n_colors=1)

    def test_kmeans_preserves_alpha_channel(self):
        """RGBA image with alpha=128 region retains alpha=128 after quantize_kmeans."""
        data = np.zeros((10, 10, 4), dtype=np.uint8)
        data[:, :, 0] = np.random.randint(0, 256, (10, 10))
        data[:, :, 1] = np.random.randint(0, 256, (10, 10))
        data[:, :, 2] = np.random.randint(0, 256, (10, 10))
        data[:, :, 3] = 128  # all alpha = 128
        image = Image.fromarray(data, "RGBA")

        quantizer = ColorQuantizer()
        result = quantizer.quantize_kmeans(image, n_colors=4)

        result_array = np.array(result)
        assert np.all(result_array[:, :, 3] == 128)


class TestQuantizePalette:
    """Tests for quantize_palette method."""

    def test_palette_maps_to_nearest_color(self):
        """Pure red pixel (255,0,0) maps to nearest palette color (200,0,0)."""
        image = Image.new("RGB", (1, 1), (255, 0, 0))
        palette = [(200, 0, 0), (0, 200, 0), (0, 0, 200)]

        quantizer = ColorQuantizer()
        result = quantizer.quantize_palette(image, palette)

        result_array = np.array(result)
        assert tuple(result_array[0, 0]) == (200, 0, 0)

    def test_palette_gb_four_colors(self):
        """GB 4-color palette produces output containing only those 4 colors."""
        gb_palette = PaletteLoader.get_preset("gb")
        np.random.seed(42)
        data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize_palette(image, gb_palette)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert unique_colors.issubset(set(gb_palette))

    def test_palette_output_only_contains_palette_colors(self):
        """Output contains zero colors not present in the input palette."""
        palette = [(0, 0, 0), (255, 255, 255), (128, 0, 0), (0, 128, 0)]
        np.random.seed(42)
        data = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize_palette(image, palette)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        palette_set = set(palette)
        off_palette = unique_colors - palette_set
        assert len(off_palette) == 0, f"Off-palette colors found: {off_palette}"

    def test_palette_preserves_alpha_channel(self):
        """RGBA image with alpha=0 region retains alpha=0 after quantize_palette."""
        data = np.zeros((10, 10, 4), dtype=np.uint8)
        data[:, :, 0] = 100
        data[:, :, 1] = 150
        data[:, :, 2] = 200
        data[:, :, 3] = 0  # fully transparent
        image = Image.fromarray(data, "RGBA")

        palette = [(0, 0, 0), (255, 255, 255)]
        quantizer = ColorQuantizer()
        result = quantizer.quantize_palette(image, palette)

        result_array = np.array(result)
        assert np.all(result_array[:, :, 3] == 0)


class TestQuantizeDispatch:
    """Tests for the quantize dispatch method."""

    def test_dispatch_to_palette_when_palette_provided(self):
        """quantize dispatches to quantize_palette when palette is provided."""
        palette = [(0, 0, 0), (255, 255, 255)]
        image = Image.new("RGB", (5, 5), (128, 128, 128))

        quantizer = ColorQuantizer()
        result = quantizer.quantize(image, palette=palette)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert unique_colors.issubset(set(palette))

    def test_dispatch_to_kmeans_when_only_color_count_given(self):
        """quantize dispatches to quantize_kmeans when only color_count is given."""
        np.random.seed(42)
        data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize(image, color_count=3)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert len(unique_colors) <= 3


class TestIntegration:
    """Integration test with PaletteLoader."""

    def test_quantizer_with_palette_loader_gb_preset(self):
        """ColorQuantizer with palette from PaletteLoader.get_preset('gb') produces exactly 4 unique colors."""
        gb_palette = PaletteLoader.get_preset("gb")
        np.random.seed(42)
        data = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)
        image = Image.fromarray(data, "RGB")

        quantizer = ColorQuantizer()
        result = quantizer.quantize(image, palette=gb_palette)

        result_array = np.array(result)
        unique_colors = set(map(tuple, result_array.reshape(-1, 3)))
        assert len(unique_colors) == 4
        assert unique_colors == set(gb_palette)
