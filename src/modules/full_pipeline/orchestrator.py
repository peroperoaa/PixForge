"""Full pipeline orchestrator that chains all four modules sequentially."""

import time
from pathlib import Path
from typing import Optional

from src.core.config import ConfigManager
from src.modules.full_pipeline.artifact_detector import ArtifactDetector
from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
    StageResult,
)
from src.modules.prompt_gen.interface import BasePromptGenerator
from src.modules.prompt_gen.schemas import PromptInput
from src.modules.image_gen.interface import BaseImageGenerator
from src.modules.image_gen.schemas import ImageGenInput
from src.modules.pixelization.interface import BasePixelization
from src.modules.pixelization.schemas import PixelizationInput
from src.modules.post_processing.interface import BasePostProcessor
from src.modules.post_processing.schemas import PostProcessingInput
from src.modules.pre_processing.interface import BasePreProcessor
from src.modules.pre_processing.schemas import PreProcessingInput


def _debug_print(config: "FullPipelineConfig", message: str) -> None:
    """Print a debug message to stdout if config.debug is True."""
    if config.debug:
        print(f"[DEBUG] {message}")


class FullPipeline:
    """Orchestrates the full pixel-art generation pipeline.

    Chains four stages sequentially:
    PROMPT -> IMAGE -> PIXELIZATION -> POST_PROCESSING

    Supports stage-skipping and auto-detection of existing artifacts.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        prompt_generator: BasePromptGenerator,
        image_generator: BaseImageGenerator,
        pixelizer: BasePixelization,
        post_processor: BasePostProcessor,
        pre_processor: Optional[BasePreProcessor] = None,
    ) -> None:
        self._config_manager = config_manager
        self._prompt_generator = prompt_generator
        self._image_generator = image_generator
        self._pixelizer = pixelizer
        self._post_processor = post_processor
        self._pre_processor = pre_processor

    def run(self, config: FullPipelineConfig) -> FullPipelineResult:
        """Execute the pipeline according to configuration.

        Args:
            config: Pipeline configuration specifying start stage, parameters, etc.

        Returns:
            FullPipelineResult with stage results, asset paths, and timing.
        """
        total_start = time.monotonic()
        stage_results: list[StageResult] = []
        final_asset_paths: list[str] = []

        # Resolve start stage and input image path
        start_stage, current_image_path = self._resolve_start(config)

        # Track the current prompt (set during PROMPT stage)
        current_prompt: Optional[str] = None

        # Define stage execution order
        all_stages = [
            PipelineStage.PROMPT,
            PipelineStage.IMAGE,
            PipelineStage.PIXELIZATION,
            PipelineStage.POST_PROCESSING,
        ]

        for stage in all_stages:
            if stage < start_stage:
                continue

            stage_start = time.monotonic()
            try:
                if stage == PipelineStage.PROMPT:
                    result_output = self._run_prompt(config)
                    current_prompt = result_output.positive_prompt
                    output_path = None

                elif stage == PipelineStage.IMAGE:
                    prompt_text = current_prompt or config.user_prompt or ""
                    result_output = self._run_image(prompt_text, config)
                    current_image_path = result_output.image_path
                    output_path = result_output.image_path

                    # Run pre-processing between IMAGE and PIXELIZATION
                    if self._pre_processor is not None:
                        pre_output = self._run_pre_processing(
                            current_image_path, config
                        )
                        current_image_path = pre_output.image_path

                elif stage == PipelineStage.PIXELIZATION:
                    assert current_image_path is not None
                    result_output = self._run_pixelization(current_image_path, current_prompt)
                    current_image_path = result_output.image_path
                    output_path = result_output.image_path

                elif stage == PipelineStage.POST_PROCESSING:
                    assert current_image_path is not None
                    result_output = self._run_post_processing(current_image_path, config)
                    final_asset_paths = result_output.output_paths
                    output_path = result_output.output_paths[0] if result_output.output_paths else None

                stage_duration = time.monotonic() - stage_start
                stage_results.append(
                    StageResult(
                        stage=stage,
                        success=True,
                        output_path=output_path,
                        duration_seconds=stage_duration,
                    )
                )

                # Debug output after successful stage completion
                if stage == PipelineStage.PROMPT:
                    _debug_print(config, f"positive_prompt: {result_output.positive_prompt}")
                    _debug_print(config, f"negative_prompt: {result_output.negative_prompt}")
                    _debug_print(config, f"style_parameters: {result_output.style_parameters}")
                elif stage == PipelineStage.IMAGE:
                    _debug_print(config, f"generated image path: {result_output.image_path}")
                    if self._pre_processor is not None:
                        _debug_print(config, f"pre-processed image path: {pre_output.image_path}")
                elif stage == PipelineStage.PIXELIZATION:
                    _debug_print(config, f"pixelized image path: {result_output.image_path}")
                elif stage == PipelineStage.POST_PROCESSING:
                    _debug_print(config, f"output asset paths: {result_output.output_paths}")

            except Exception as e:
                stage_duration = time.monotonic() - stage_start
                stage_results.append(
                    StageResult(
                        stage=stage,
                        success=False,
                        error_message=str(e),
                        duration_seconds=stage_duration,
                    )
                )
                # Abort remaining stages on failure
                break

        total_duration = time.monotonic() - total_start
        return FullPipelineResult(
            stage_results=stage_results,
            final_asset_paths=final_asset_paths,
            total_duration_seconds=total_duration,
        )

    def _resolve_start(
        self, config: FullPipelineConfig
    ) -> tuple[PipelineStage, Optional[str]]:
        """Resolve the actual start stage and input image path.

        When start_stage is None, uses ArtifactDetector for auto-detection.
        """
        if config.start_stage is not None:
            return config.start_stage, config.input_image_path

        # Auto-detect mode
        output_dir = config.output_dir or self._config_manager.get_post_processing_output_dir()
        # Use the parent of output_dir (e.g., ./output) as the base for artifact detection
        detector = ArtifactDetector(Path(output_dir).parent)
        detected_stage, detected_path = detector.detect_start_stage()

        image_path = str(detected_path) if detected_path else config.input_image_path
        return detected_stage, image_path

    def _run_prompt(self, config: FullPipelineConfig):
        """Execute the PROMPT stage."""
        prompt_input = PromptInput(
            text_prompt=config.user_prompt or "",
        )
        return self._prompt_generator.generate(prompt_input)

    def _run_image(self, prompt: str, config: FullPipelineConfig):
        """Execute the IMAGE stage."""
        image_input = ImageGenInput(
            prompt=prompt,
            image_path=config.input_image_path,
            aspect_ratio=config.aspect_ratio,
        )
        return self._image_generator.generate(image_input)

    def _run_pixelization(self, image_path: str, prompt: Optional[str] = None):
        """Execute the PIXELIZATION stage."""
        pix_input = PixelizationInput(
            image_path=image_path,
            prompt=prompt,
        )
        return self._pixelizer.generate(pix_input)

    def _run_pre_processing(self, image_path: str, config: FullPipelineConfig):
        """Execute pre-processing between IMAGE and PIXELIZATION stages."""
        pre_input = PreProcessingInput(
            image_path=image_path,
            remove_background=config.remove_background,
            intermediate_size=config.intermediate_size,
            output_dir=config.output_dir,
        )
        return self._pre_processor.process(pre_input)

    def _run_post_processing(self, image_path: str, config: FullPipelineConfig):
        """Execute the POST_PROCESSING stage."""
        output_dir = config.output_dir or self._config_manager.get_post_processing_output_dir()
        asset_name = config.asset_name or "output"

        # Disable remove_background in post-processing when pre-processor handled it
        remove_bg = False if self._pre_processor is not None else config.remove_background

        pp_input = PostProcessingInput(
            image_path=image_path,
            asset_name=asset_name,
            target_sizes=config.target_sizes,
            remove_background=remove_bg,
            color_count=config.color_count,
            palette_preset=config.palette_preset,
            output_dir=output_dir,
        )
        return self._post_processor.process(pp_input)
