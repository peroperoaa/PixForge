"""Pre-processing pipeline: background removal, subject-aware cropping, and LANCZOS downscale."""

import os

from PIL import Image

from src.modules.post_processing.background_remover import BackgroundRemover
from src.modules.pre_processing.exceptions import PreProcessingError
from src.modules.pre_processing.interface import BasePreProcessor
from src.modules.pre_processing.schemas import PreProcessingInput, PreProcessingOutput


class PreProcessor(BasePreProcessor):
    """Pre-processes a high-res image to an intermediate-resolution square suitable for pixelization.

    Steps:
    1. Load image from disk
    2. Optionally remove background (producing RGBA with alpha channel)
    3. Crop to square (subject-aware via alpha bounding box, or center crop)
    4. Downscale to intermediate_size using LANCZOS resampling
    5. Save and return output path
    """

    def __init__(self) -> None:
        self._background_remover = BackgroundRemover()

    def process(self, input_data: PreProcessingInput) -> PreProcessingOutput:
        """Process an image through the pre-processing pipeline.

        Args:
            input_data: Configuration specifying image path and processing options.

        Returns:
            PreProcessingOutput with path to the intermediate-resolution image.

        Raises:
            PreProcessingError: If the image cannot be loaded or processing fails.
        """
        # Load image
        try:
            image = Image.open(input_data.image_path)
        except Exception as e:
            raise PreProcessingError(
                f"Failed to load image: {input_data.image_path}: {e}"
            ) from e

        original_size = image.size

        # Step 1: Background removal
        if input_data.remove_background:
            image = self._background_remover.remove(image)

        # Step 2: Crop to square
        image = self._crop_square(image, crop_mode=input_data.crop_mode)

        # Step 3: Downscale using LANCZOS
        target = input_data.intermediate_size
        image = image.resize((target, target), Image.LANCZOS)

        # Save output
        output_dir = input_data.output_dir or "output"
        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(input_data.image_path))[0]
        filename = f"{base_name}_pre_{target}x{target}.png"
        output_path = os.path.join(output_dir, filename)
        image.save(output_path)

        return PreProcessingOutput(
            image_path=output_path,
            original_size=original_size,
            intermediate_size=target,
        )

    def _crop_square(self, image: Image.Image, crop_mode: str = "auto") -> Image.Image:
        """Crop the image to a square.

        When crop_mode is "auto" and the image has an alpha channel, uses the alpha
        bounding box to center the subject. Otherwise, falls back to center crop.

        Args:
            image: Source PIL Image.
            crop_mode: "auto" (subject-aware) or "center" (always center crop).

        Returns:
            A square-cropped PIL Image.
        """
        if crop_mode == "auto" and image.mode == "RGBA":
            return self._subject_aware_crop(image)
        return self._center_crop(image)

    @staticmethod
    def _center_crop(image: Image.Image) -> Image.Image:
        """Crop the largest centered square from a possibly non-square image."""
        width, height = image.size
        if width == height:
            return image
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        return image.crop((left, top, left + side, top + side))

    @staticmethod
    def _subject_aware_crop(image: Image.Image) -> Image.Image:
        """Crop a square centered on the subject using the alpha channel bounding box.

        The crop is the largest square that:
        1. Contains the entire alpha bounding box
        2. Fits within the image bounds
        3. Is centered on the bounding box center

        Args:
            image: RGBA PIL Image with alpha channel.

        Returns:
            A square-cropped PIL Image centered on the subject.
        """
        width, height = image.size
        alpha = image.getchannel("A")
        bbox = alpha.getbbox()

        if bbox is None:
            # Fully transparent image, fall back to center crop
            return PreProcessor._center_crop(image)

        # Bounding box of non-transparent pixels
        bb_left, bb_top, bb_right, bb_bottom = bbox
        bb_width = bb_right - bb_left
        bb_height = bb_bottom - bb_top

        # Center of the bounding box
        cx = (bb_left + bb_right) // 2
        cy = (bb_top + bb_bottom) // 2

        # Side length: must contain the bounding box, but at most the image's min dimension
        side = max(bb_width, bb_height)
        side = min(side, min(width, height))

        # Compute crop centered on the bounding box center
        half = side // 2
        left = cx - half
        top = cy - half

        # Clamp to image bounds
        if left < 0:
            left = 0
        if top < 0:
            top = 0
        if left + side > width:
            left = width - side
        if top + side > height:
            top = height - side

        return image.crop((left, top, left + side, top + side))
