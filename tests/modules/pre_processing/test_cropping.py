"""Tests for subject-aware cropping in pre-processing module."""

import pytest
from PIL import Image


def _make_rgba_with_subject(size=(400, 300), subject_box=(50, 50, 150, 150)):
    """Create an RGBA image with a colored subject inside a transparent background.

    Args:
        size: Image dimensions (width, height).
        subject_box: (left, top, right, bottom) of the opaque subject area.
    """
    img = Image.new("RGBA", size, (0, 0, 0, 0))  # fully transparent
    left, top, right, bottom = subject_box
    for y in range(top, bottom):
        for x in range(left, right):
            img.putpixel((x, y), (255, 0, 0, 255))  # opaque red subject
    return img


def _make_rgb_image(size=(400, 300)):
    """Create a plain RGB image (no alpha channel)."""
    return Image.new("RGB", size, (128, 128, 128))


class TestSubjectAwareCropping:
    """Tests for subject-aware cropping logic."""

    def test_alpha_bounding_box_centers_subject(self):
        """RGBA image with subject in top-left: crop centers on subject's alpha bounding box."""
        from src.modules.pre_processing.pipeline import PreProcessor

        # Subject is in top-left quadrant (50,50)-(150,150) of 400x300 image
        img = _make_rgba_with_subject(size=(400, 300), subject_box=(50, 50, 150, 150))
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="auto")

        # Result should be square
        assert cropped.size[0] == cropped.size[1], "Cropped image must be square"

        # Subject should be contained within the crop
        # The alpha bounding box center is at (100, 100), crop should include it
        alpha = cropped.getchannel("A")
        bbox = alpha.getbbox()
        assert bbox is not None, "Subject should be present in cropped image"

    def test_center_crop_fallback_for_rgb(self):
        """RGB image without alpha falls back to center crop."""
        from src.modules.pre_processing.pipeline import PreProcessor

        img = _make_rgb_image(size=(400, 300))
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="auto")

        # Center crop of 400x300 -> 300x300 square
        assert cropped.size == (300, 300)

    def test_crop_mode_center_forces_center_crop(self):
        """RGBA image with alpha but crop_mode='center' forces center crop."""
        from src.modules.pre_processing.pipeline import PreProcessor

        img = _make_rgba_with_subject(size=(400, 300), subject_box=(10, 10, 50, 50))
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="center")

        # Center crop of 400x300 -> 300x300 square
        assert cropped.size == (300, 300)

    def test_full_alpha_coverage_equivalent_to_center_crop(self):
        """RGBA image with entire image opaque: bounding box covers full image."""
        from src.modules.pre_processing.pipeline import PreProcessor

        img = Image.new("RGBA", (400, 300), (255, 0, 0, 255))  # fully opaque
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="auto")

        # Full coverage bounding box: center of bbox = center of image
        # Result should be 300x300 square (min dimension)
        assert cropped.size[0] == cropped.size[1]
        assert cropped.size[0] == 300

    def test_small_subject_in_corner(self):
        """RGBA image with tiny subject in corner: crop pads square around subject."""
        from src.modules.pre_processing.pipeline import PreProcessor

        # Small 20x20 subject in bottom-right corner of 400x400 image
        img = _make_rgba_with_subject(size=(400, 400), subject_box=(370, 370, 390, 390))
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="auto")

        # Result must be square
        assert cropped.size[0] == cropped.size[1]

        # Subject should still be in the cropped image
        alpha = cropped.getchannel("A")
        bbox = alpha.getbbox()
        assert bbox is not None, "Subject should be present in cropped image"

    def test_already_square_image_center_crop(self):
        """Already square image: center crop returns same dimensions."""
        from src.modules.pre_processing.pipeline import PreProcessor

        img = _make_rgb_image(size=(300, 300))
        processor = PreProcessor()
        cropped = processor._crop_square(img, crop_mode="center")

        assert cropped.size == (300, 300)
