"""BOX (area-average) downscaler for pixel-art image resizing."""

from typing import List

from PIL import Image

from src.modules.post_processing.exceptions import DownscaleError


class Downscaler:
    """Resizes images to exact square pixel dimensions using BOX (area-average) resampling.

    BOX resampling averages all source pixels that map to each output pixel,
    preserving more detail than nearest-neighbor while keeping pixel-art crisp.
    """

    def downscale(self, image: Image.Image, target_size: int) -> Image.Image:
        """Resize an image to target_size × target_size using BOX resampling.

        Non-square source images are center-cropped to the largest inscribed
        square before resizing.

        Args:
            image: Source PIL Image (any mode).
            target_size: Desired width and height in pixels.  Must be > 0.

        Returns:
            A new PIL Image of exactly (target_size, target_size).

        Raises:
            DownscaleError: If target_size is zero or negative.
        """
        if target_size <= 0:
            raise DownscaleError(
                f"target_size must be a positive integer, got {target_size}"
            )

        cropped = self._center_crop_square(image)
        return cropped.resize((target_size, target_size), Image.BOX)

    def downscale_multi(
        self, image: Image.Image, target_sizes: List[int]
    ) -> List[Image.Image]:
        """Resize an image to multiple square sizes using BOX resampling.

        Args:
            image: Source PIL Image (any mode).
            target_sizes: List of desired sizes in pixels.

        Returns:
            List of PIL Images, one per requested size.
        """
        return [self.downscale(image, size) for size in target_sizes]

    @staticmethod
    def _center_crop_square(image: Image.Image) -> Image.Image:
        """Crop the largest centered square from a possibly non-square image."""
        width, height = image.size
        if width == height:
            return image
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        return image.crop((left, top, left + side, top + side))
