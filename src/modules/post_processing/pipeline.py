"""Post-processing pipeline orchestrating downscaling, color quantization, and asset export."""

import logging
import os

from PIL import Image

from src.modules.post_processing.color_quantizer import ColorQuantizer
from src.modules.post_processing.downscaler import Downscaler
from src.modules.post_processing.interface import BasePostProcessor
from src.modules.post_processing.palette_loader import PaletteLoader
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput

logger = logging.getLogger(__name__)


class PostProcessingPipeline(BasePostProcessor):
    """Orchestrates the full post-processing chain: downscale, quantize colors, and export assets."""

    def __init__(self) -> None:
        self._color_quantizer = ColorQuantizer()
        self._downscaler = Downscaler()

    def process(self, input_data: PostProcessingInput) -> PostProcessingOutput:
        """Process an image through the post-processing pipeline.

        Steps executed for each target size:
        1. Load source image
        2. Log deprecation warning if remove_background is True
        3. Downscale to target size
        4. Quantize colors at target resolution (if color_count, palette_path, or palette_preset is provided)
        5. Save

        Args:
            input_data: Configuration specifying image path, options, and output settings.

        Returns:
            PostProcessingOutput with paths to all generated asset files.
        """
        # Load input image
        image = Image.open(input_data.image_path)

        # Deprecation warning for remove_background
        if input_data.remove_background:
            logger.warning(
                "remove_background is deprecated in PostProcessingPipeline and will be "
                "removed in a future version. Background removal is now handled in the "
                "pre-processing stage."
            )

        # Resolve palette once (shared across all sizes)
        palette = None
        needs_quantization = (
            input_data.color_count is not None
            or input_data.palette_path is not None
            or input_data.palette_preset is not None
        )
        if needs_quantization:
            if input_data.palette_preset is not None:
                palette = PaletteLoader.get_preset(input_data.palette_preset)
            elif input_data.palette_path is not None:
                palette = PaletteLoader.load_from_hex_file(input_data.palette_path)

        # Determine output directory
        output_dir = input_data.output_dir or "output"
        os.makedirs(output_dir, exist_ok=True)

        # For each target size: downscale first, then quantize at target resolution
        output_paths: list[str] = []
        for size in input_data.target_sizes:
            # Step 1: Downscale to target size
            resized = self._downscaler.downscale(image, size)

            # Step 2: Quantize at target resolution
            if needs_quantization:
                resized = self._color_quantizer.quantize(
                    resized, color_count=input_data.color_count, palette=palette
                )

            filename = f"{input_data.asset_name}_{size}x{size}.png"
            filepath = os.path.join(output_dir, filename)
            resized.save(filepath)
            output_paths.append(filepath)

        # Derive palette name from preset name or filename
        palette_name = None
        if input_data.palette_preset is not None:
            palette_name = input_data.palette_preset
        elif input_data.palette_path is not None:
            palette_name = os.path.splitext(
                os.path.basename(input_data.palette_path)
            )[0]

        return PostProcessingOutput(
            output_paths=output_paths,
            target_sizes=input_data.target_sizes,
            color_count=input_data.color_count,
            palette_name=palette_name,
        )
