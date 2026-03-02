"""Color quantizer for reducing image colors via K-Means or fixed-palette mapping."""

from typing import List, Optional, Tuple

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from src.modules.post_processing.exceptions import ColorQuantizationError

# Type alias matching palette_loader.py
Palette = List[Tuple[int, int, int]]


class ColorQuantizer:
    """Reduces image colors using K-Means clustering or nearest-palette mapping.

    Both methods preserve the alpha channel when processing RGBA images.
    """

    def quantize_kmeans(self, image: Image.Image, n_colors: int) -> Image.Image:
        """Reduce image to N colors using K-Means clustering.

        Args:
            image: PIL Image in RGB or RGBA mode.
            n_colors: Number of target colors. Must be >= 2.

        Returns:
            New PIL Image with at most n_colors unique RGB values.

        Raises:
            ColorQuantizationError: If n_colors < 2 or KMeans fails.
        """
        if n_colors < 2:
            raise ColorQuantizationError(
                f"n_colors must be >= 2, got {n_colors}"
            )

        arr = np.array(image)
        has_alpha = image.mode == "RGBA"

        if has_alpha:
            rgb = arr[:, :, :3]
            alpha = arr[:, :, 3]
        else:
            rgb = arr

        h, w, _ = rgb.shape
        pixels = rgb.reshape(-1, 3).astype(np.float64)

        try:
            kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
            kmeans.fit(pixels)
        except Exception as e:
            raise ColorQuantizationError(f"KMeans clustering failed: {e}") from e

        centers = np.round(kmeans.cluster_centers_).astype(np.uint8)
        quantized_pixels = centers[kmeans.labels_]
        quantized_rgb = quantized_pixels.reshape(h, w, 3)

        if has_alpha:
            result_arr = np.dstack([quantized_rgb, alpha])
            return Image.fromarray(result_arr, "RGBA")
        else:
            return Image.fromarray(quantized_rgb, "RGB")

    def quantize_palette(self, image: Image.Image, palette: Palette) -> Image.Image:
        """Map each pixel to the nearest color in the given palette.

        Uses Euclidean distance in RGB space.

        Args:
            image: PIL Image in RGB or RGBA mode.
            palette: List of (R, G, B) tuples. Must have >= 2 colors.

        Returns:
            New PIL Image where every pixel matches a palette color.

        Raises:
            ColorQuantizationError: If palette is empty or has fewer than 2 colors.
        """
        if not palette or len(palette) < 2:
            raise ColorQuantizationError(
                f"Palette must contain at least 2 colors, got {len(palette) if palette else 0}"
            )

        arr = np.array(image)
        has_alpha = image.mode == "RGBA"

        if has_alpha:
            rgb = arr[:, :, :3]
            alpha = arr[:, :, 3]
        else:
            rgb = arr

        h, w, _ = rgb.shape
        pixels = rgb.reshape(-1, 3).astype(np.float64)
        palette_arr = np.array(palette, dtype=np.float64)

        # Compute Euclidean distance from each pixel to each palette color
        # Using broadcasting: pixels (N, 1, 3) - palette (1, M, 3)
        diff = pixels[:, np.newaxis, :] - palette_arr[np.newaxis, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=2))
        nearest_indices = np.argmin(distances, axis=1)

        quantized_pixels = palette_arr[nearest_indices].astype(np.uint8)
        quantized_rgb = quantized_pixels.reshape(h, w, 3)

        if has_alpha:
            result_arr = np.dstack([quantized_rgb, alpha])
            return Image.fromarray(result_arr, "RGBA")
        else:
            return Image.fromarray(quantized_rgb, "RGB")

    def quantize(
        self,
        image: Image.Image,
        color_count: Optional[int] = None,
        palette: Optional[Palette] = None,
    ) -> Image.Image:
        """Dispatch to the appropriate quantization method.

        If palette is provided, uses palette-based quantization.
        Otherwise, uses K-Means with color_count.

        Args:
            image: PIL Image in RGB or RGBA mode.
            color_count: Number of target colors for K-Means mode.
            palette: Fixed palette for nearest-color mapping.

        Returns:
            Quantized PIL Image.

        Raises:
            ColorQuantizationError: If neither color_count nor palette is provided,
                or if the chosen method fails.
        """
        if palette is not None:
            return self.quantize_palette(image, palette)
        elif color_count is not None:
            return self.quantize_kmeans(image, color_count)
        else:
            raise ColorQuantizationError(
                "Either color_count or palette must be provided"
            )
