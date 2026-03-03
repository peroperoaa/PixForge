"""Tests for pipeline skipping POST_PROCESSING when skip_post_processing is True."""

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


class TestPipelineSkipPostProcessing:
    """Test orchestrator respects skip_post_processing flag."""

    # Case 1: skip_post_processing=True stops after PIXELIZATION
    def test_skip_post_processing_stops_after_pixelization(self):
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            user_prompt="pixel knight",
            skip_post_processing=True,
        )
        result = pipeline.run(config)

        # POST_PROCESSING should not appear in stage_results
        stages_executed = [sr.stage for sr in result.stage_results]
        assert PipelineStage.POST_PROCESSING not in stages_executed

        # Should have PROMPT, IMAGE, PIXELIZATION
        assert PipelineStage.PROMPT in stages_executed
        assert PipelineStage.IMAGE in stages_executed
        assert PipelineStage.PIXELIZATION in stages_executed

        # final_asset_paths should contain the pixelized image path
        assert result.final_asset_paths == ["/output/images/knight_pixelized.png"]

        # post_processor should not have been called
        post_proc.process.assert_not_called()

    # Case 2: skip_post_processing=False runs all stages (default behavior)
    def test_default_runs_all_stages(self):
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )

        config = FullPipelineConfig(
            user_prompt="pixel knight",
            skip_post_processing=False,
        )
        result = pipeline.run(config)

        stages_executed = [sr.stage for sr in result.stage_results]
        assert PipelineStage.POST_PROCESSING in stages_executed
        assert len(stages_executed) == 4

        # final_asset_paths should come from post-processing
        assert result.final_asset_paths == [
            "/output/assets/knight_32.png",
            "/output/assets/knight_64.png",
        ]

        post_proc.process.assert_called_once()

    # Case 3: skip_post_processing=True with start_stage=PIXELIZATION
    def test_skip_post_processing_from_pixelization_stage(self):
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
            skip_post_processing=True,
        )
        result = pipeline.run(config)

        stages_executed = [sr.stage for sr in result.stage_results]
        assert stages_executed == [PipelineStage.PIXELIZATION]
        assert PipelineStage.POST_PROCESSING not in stages_executed
        assert result.final_asset_paths == ["/output/images/knight_pixelized.png"]

        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_not_called()
        post_proc.process.assert_not_called()
