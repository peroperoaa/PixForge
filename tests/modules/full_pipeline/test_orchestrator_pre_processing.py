"""Tests for FullPipeline orchestrator - pre-processing integration.

Verifies that pre-processing (background removal, crop, downscale) runs
between IMAGE and PIXELIZATION stages, and that POST_PROCESSING receives
remove_background=False since it was already handled.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
)
from src.modules.full_pipeline.orchestrator import FullPipeline
from src.modules.prompt_gen.schemas import PromptOutput
from src.modules.image_gen.schemas import ImageGenOutput
from src.modules.pixelization.schemas import PixelizationOutput
from src.modules.post_processing.schemas import PostProcessingOutput
from src.modules.pre_processing.schemas import PreProcessingInput, PreProcessingOutput


def _make_mocks():
    """Create mock adapters for all five modules (including pre_processor)."""
    prompt_gen = MagicMock()
    prompt_gen.generate.return_value = PromptOutput(
        positive_prompt="pixel art knight, 16-bit",
        negative_prompt="blurry, low quality",
        style_parameters={"style": "pixel_art"},
    )

    image_gen = MagicMock()
    image_gen.generate.return_value = ImageGenOutput(image_path="/output/images/knight.png")

    pixelizer = MagicMock()
    pixelizer.generate.return_value = PixelizationOutput(
        image_path="/output/images/knight_pixelized.png", width=64, height=64
    )

    post_proc = MagicMock()
    post_proc.process.return_value = PostProcessingOutput(
        output_paths=["/output/assets/knight_32.png", "/output/assets/knight_64.png"],
        target_sizes=[32, 64],
        color_count=16,
        palette_name="sweetie-16",
    )

    pre_proc = MagicMock()
    pre_proc.process.return_value = PreProcessingOutput(
        image_path="/output/knight_pre_256x256.png",
        original_size=(1024, 1024),
        intermediate_size=256,
    )

    config_mgr = MagicMock()
    config_mgr.get_post_processing_output_dir.return_value = "./output/assets"

    return prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr


class TestPreProcessingIntegration:
    """Tests for pre-processing integration between IMAGE and PIXELIZATION stages."""

    def test_pre_processor_called_after_image_stage(self):
        """Pre-processor.process is called after IMAGE stage produces output."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        pipeline.run(config)

        pre_proc.process.assert_called_once()

    def test_pre_processor_receives_image_stage_output(self):
        """Pre-processor input image_path comes from IMAGE stage output."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        pipeline.run(config)

        pre_call_args = pre_proc.process.call_args
        pre_input = pre_call_args[0][0]
        assert pre_input.image_path == "/output/images/knight.png"

    def test_pre_processor_removes_background(self):
        """Pre-processor input has remove_background=True."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
            remove_background=True,
        )
        pipeline.run(config)

        pre_call_args = pre_proc.process.call_args
        pre_input = pre_call_args[0][0]
        assert pre_input.remove_background is True

    def test_pre_processor_uses_intermediate_size(self):
        """Pre-processor input uses intermediate_size from config (default 256)."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        pipeline.run(config)

        pre_call_args = pre_proc.process.call_args
        pre_input = pre_call_args[0][0]
        assert pre_input.intermediate_size == 256

    def test_pre_processor_uses_custom_intermediate_size(self):
        """Pre-processor input uses custom intermediate_size when specified."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()

        pre_proc.process.return_value = PreProcessingOutput(
            image_path="/output/knight_pre_128x128.png",
            original_size=(1024, 1024),
            intermediate_size=128,
        )

        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
            intermediate_size=128,
        )
        pipeline.run(config)

        pre_call_args = pre_proc.process.call_args
        pre_input = pre_call_args[0][0]
        assert pre_input.intermediate_size == 128

    def test_pixelization_receives_pre_processed_image(self):
        """PIXELIZATION stage receives the 256px pre-processed image, not the original 1024px."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        pipeline.run(config)

        pix_call_args = pixelizer.generate.call_args
        pix_input = pix_call_args[0][0]
        assert pix_input.image_path == "/output/knight_pre_256x256.png"

    def test_post_processing_receives_remove_background_false(self):
        """POST_PROCESSING receives remove_background=False since pre-processing already did it."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
            remove_background=True,
        )
        pipeline.run(config)

        pp_call_args = post_proc.process.call_args
        pp_input = pp_call_args[0][0]
        assert pp_input.remove_background is False

    def test_pre_processing_not_called_when_starting_from_pixelization(self):
        """When start_stage=PIXELIZATION, pre-processing is skipped."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            start_stage=PipelineStage.PIXELIZATION,
            input_image_path="/input/knight.png",
        )
        pipeline.run(config)

        pre_proc.process.assert_not_called()

    def test_pre_processing_not_called_when_starting_from_post_processing(self):
        """When start_stage=POST_PROCESSING, pre-processing is skipped."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            start_stage=PipelineStage.POST_PROCESSING,
            input_image_path="/input/knight_pixelized.png",
        )
        pipeline.run(config)

        pre_proc.process.assert_not_called()

    def test_full_pipeline_stage_count_with_pre_processing(self):
        """Full pipeline still reports 4 stage results (pre-processing is inline, not a separate stage)."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        result = pipeline.run(config)

        assert len(result.stage_results) == 4
        stages = [sr.stage for sr in result.stage_results]
        assert stages == [
            PipelineStage.PROMPT,
            PipelineStage.IMAGE,
            PipelineStage.PIXELIZATION,
            PipelineStage.POST_PROCESSING,
        ]

    def test_intermediate_size_default_is_256(self):
        """FullPipelineConfig.intermediate_size defaults to 256."""
        config = FullPipelineConfig(
            user_prompt="test",
            start_stage=PipelineStage.PROMPT,
        )
        assert config.intermediate_size == 256

    def test_pre_processing_error_aborts_pipeline(self):
        """If pre-processing fails, the pipeline should abort at IMAGE stage."""
        prompt_gen, image_gen, pixelizer, post_proc, pre_proc, config_mgr = _make_mocks()
        pre_proc.process.side_effect = RuntimeError("Background removal failed")

        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
            pre_processor=pre_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        result = pipeline.run(config)

        # PROMPT succeeds, IMAGE fails (because pre-processing within IMAGE stage fails)
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        assert result.stage_results[0].success is True
        assert result.stage_results[1].stage == PipelineStage.IMAGE
        assert result.stage_results[1].success is False
        assert "Background removal failed" in result.stage_results[1].error_message

        pixelizer.generate.assert_not_called()
        post_proc.process.assert_not_called()
