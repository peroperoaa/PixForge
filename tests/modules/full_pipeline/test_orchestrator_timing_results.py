"""Tests for FullPipeline orchestrator - timing and results."""

import pytest
from unittest.mock import MagicMock

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


class TestTimingAndResults:
    def test_all_stages_have_duration(self):
        """Each StageResult has duration_seconds >= 0."""
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

        for sr in result.stage_results:
            assert sr.duration_seconds >= 0

    def test_total_duration_gte_sum_of_stages(self):
        """total_duration_seconds >= sum of individual stage durations."""
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

        sum_of_stages = sum(sr.duration_seconds for sr in result.stage_results)
        assert result.total_duration_seconds >= sum_of_stages - 0.001  # small tolerance

    def test_final_asset_paths_on_success(self):
        """On success, final_asset_paths contains post_processing output_paths."""
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

        assert result.final_asset_paths == [
            "/output/assets/knight_32.png",
            "/output/assets/knight_64.png",
        ]
