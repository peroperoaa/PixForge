"""Tests for FullPipeline orchestrator - error handling and abort."""

import pytest
from unittest.mock import MagicMock

from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    PipelineStage,
)
from src.modules.full_pipeline.orchestrator import FullPipeline
from src.modules.prompt_gen.schemas import PromptOutput
from src.modules.image_gen.schemas import ImageGenOutput
from src.modules.pixelization.schemas import PixelizationOutput
from src.modules.post_processing.schemas import PostProcessingOutput


def _make_mocks():
    """Create mock adapters for all four modules."""
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

    config_mgr = MagicMock()
    config_mgr.get_post_processing_output_dir.return_value = "./output/assets"

    return prompt_gen, image_gen, pixelizer, post_proc, config_mgr


class TestErrorHandling:
    def test_prompt_stage_failure_aborts_pipeline(self):
        """Prompt generator failure is recorded and remaining stages are aborted."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        prompt_gen.generate.side_effect = RuntimeError("API connection failed")

        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        result = pipeline.run(config)

        assert len(result.stage_results) == 1
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        assert result.stage_results[0].success is False
        assert "API connection failed" in result.stage_results[0].error_message
        assert result.final_asset_paths == []

        image_gen.generate.assert_not_called()
        pixelizer.generate.assert_not_called()
        post_proc.process.assert_not_called()

    def test_mid_pipeline_failure_records_success_then_failure(self):
        """Image succeeds, pixelization fails: both are recorded, post_processing skipped."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pixelizer.generate.side_effect = ValueError("Invalid image format")

        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        result = pipeline.run(config)

        # PROMPT and IMAGE succeed, PIXELIZATION fails
        assert len(result.stage_results) == 3
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        assert result.stage_results[0].success is True
        assert result.stage_results[1].stage == PipelineStage.IMAGE
        assert result.stage_results[1].success is True
        assert result.stage_results[2].stage == PipelineStage.PIXELIZATION
        assert result.stage_results[2].success is False
        assert "Invalid image format" in result.stage_results[2].error_message

        post_proc.process.assert_not_called()

    def test_failed_stage_has_duration(self):
        """Even failed stages record duration_seconds."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        prompt_gen.generate.side_effect = RuntimeError("fail")

        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            start_stage=PipelineStage.PROMPT,
        )
        result = pipeline.run(config)

        assert result.stage_results[0].duration_seconds >= 0
