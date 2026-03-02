"""Tests for FullPipeline orchestrator - sequential execution."""

import pytest
from unittest.mock import MagicMock, patch

from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
    StageResult,
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


class TestSequentialExecution:
    def test_full_pipeline_prompt_to_post_processing(self):
        """All four stages execute in order when start_stage=PROMPT."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
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

        assert isinstance(result, FullPipelineResult)
        assert len(result.stage_results) == 4
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        assert result.stage_results[1].stage == PipelineStage.IMAGE
        assert result.stage_results[2].stage == PipelineStage.PIXELIZATION
        assert result.stage_results[3].stage == PipelineStage.POST_PROCESSING
        for sr in result.stage_results:
            assert sr.success is True

        prompt_gen.generate.assert_called_once()
        image_gen.generate.assert_called_once()
        pixelizer.generate.assert_called_once()
        post_proc.process.assert_called_once()

    def test_output_chaining_prompt_to_image(self):
        """prompt_output.positive_prompt feeds into image_gen input."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
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
        pipeline.run(config)

        image_call_args = image_gen.generate.call_args
        image_input = image_call_args[0][0] if image_call_args[0] else image_call_args[1].get("input_data")
        assert image_input.prompt == "pixel art knight, 16-bit"

    def test_output_chaining_image_to_pixelization(self):
        """image_output.image_path feeds into pixelization input."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
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
        pipeline.run(config)

        pix_call_args = pixelizer.generate.call_args
        pix_input = pix_call_args[0][0] if pix_call_args[0] else pix_call_args[1].get("input_data")
        assert pix_input.image_path == "/output/images/knight.png"

    def test_output_chaining_pixelization_to_post_processing(self):
        """pixelization_output.image_path feeds into post_processing input."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
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
        pipeline.run(config)

        pp_call_args = post_proc.process.call_args
        pp_input = pp_call_args[0][0] if pp_call_args[0] else pp_call_args[1].get("input_data")
        assert pp_input.image_path == "/output/images/knight_pixelized.png"
