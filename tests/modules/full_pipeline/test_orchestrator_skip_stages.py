"""Tests for FullPipeline orchestrator - stage skipping."""

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


class TestStageSkipping:
    def test_skip_to_image_stage(self):
        """start_stage=IMAGE skips PROMPT, executes IMAGE/PIXELIZATION/POST_PROCESSING."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            start_stage=PipelineStage.IMAGE,
            input_image_path="/input/knight.png",
        )
        result = pipeline.run(config)

        assert len(result.stage_results) == 3
        assert result.stage_results[0].stage == PipelineStage.IMAGE
        assert result.stage_results[1].stage == PipelineStage.PIXELIZATION
        assert result.stage_results[2].stage == PipelineStage.POST_PROCESSING

        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_called_once()

    def test_skip_to_pixelization_stage(self):
        """start_stage=PIXELIZATION skips PROMPT and IMAGE."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            start_stage=PipelineStage.PIXELIZATION,
            input_image_path="/input/knight.png",
        )
        result = pipeline.run(config)

        assert len(result.stage_results) == 2
        assert result.stage_results[0].stage == PipelineStage.PIXELIZATION
        assert result.stage_results[1].stage == PipelineStage.POST_PROCESSING

        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_not_called()
        pixelizer.generate.assert_called_once()
        post_proc.process.assert_called_once()

    def test_skip_to_post_processing_stage(self):
        """start_stage=POST_PROCESSING, only POST_PROCESSING executes."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            start_stage=PipelineStage.POST_PROCESSING,
            input_image_path="/input/knight_pixelized.png",
        )
        result = pipeline.run(config)

        assert len(result.stage_results) == 1
        assert result.stage_results[0].stage == PipelineStage.POST_PROCESSING
        assert result.stage_results[0].success is True

        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_not_called()
        pixelizer.generate.assert_not_called()
        post_proc.process.assert_called_once()
