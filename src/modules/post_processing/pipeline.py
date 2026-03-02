"""Post-processing pipeline orchestrating background removal, color quantization, downscaling, and asset export."""

import os

from PIL import Image

from src.modules.post_processing.background_remover import BackgroundRemover
from src.modules.post_processing.color_quantizer import ColorQuantizer
from src.modules.post_processing.downscaler import Downscaler
from src.modules.post_processing.interface import BasePostProcessor
from src.modules.post_processing.palette_loader import PaletteLoader
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


class PostProcessingPipeline(BasePostProcessor):
    """Orchestrates the full post-processing chain: remove background, quantize colors, downscale, and export assets."""

    def __init__(self) -> None:
        self._background_remover = BackgroundRemover()
        self._color_quantizer = ColorQuantizer()
        self._downscaler = Downscaler()

    def process(self, input_data: PostProcessingInput) -> PostProcessingOutput:
        """Process an image through the post-processing pipeline.

        Steps executed based on input configuration:
        1. Load source image
        2. Remove background (if remove_background=True)
        3. Quantize colors (if color_count, palette_path, or palette_preset is provided)
        4. Downscale to each target size and save

        Args:
            input_data: Configuration specifying image path, options, and output settings.

        Returns:
            PostProcessingOutput with paths to all generated asset files.
        """
        # Load input image
        image = Image.open(input_data.image_path)

        # Step 1: Background removal
        if input_data.remove_background:
            image = self._background_remover.remove(image)

        # Step 2: Color quantization
        if input_data.color_count is not None or input_data.palette_path is not None or input_data.palette_preset is not None:
            palette = None
            if input_data.palette_preset is not None:
                palette = PaletteLoader.get_preset(input_data.palette_preset)
            elif input_data.palette_path is not None:
                palette = PaletteLoader.load_from_hex_file(input_data.palette_path)
            image = self._color_quantizer.quantize(
                image, color_count=input_data.color_count, palette=palette
            )

        # Determine output directory
        output_dir = input_data.output_dir or "output"
        os.makedirs(output_dir, exist_ok=True)

        # Step 3: Downscale and save for each target size
        output_paths: list[str] = []
        for size in input_data.target_sizes:
            resized = self._downscaler.downscale(image, size)
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
