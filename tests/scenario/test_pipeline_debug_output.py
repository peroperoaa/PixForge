"""Tests for pipeline debug output in FullPipeline orchestrator."""

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
from src.modules.pre_processing.schemas import PreProcessingOutput


def _make_mocks():
    """Create mock adapters for all four modules."""
    prompt_gen = MagicMock()
    prompt_gen.generate.return_value = PromptOutput(
        positive_prompt="pixel art knight, 16-bit",
        negative_prompt="blurry, low quality",
        style_parameters={"style": "pixel_art", "view_angle": "front"},
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


class TestDebugOutputEnabled:
    """Tests that [DEBUG] lines appear in stdout when config.debug=True."""

    def test_prompt_stage_debug_output(self, capsys):
        """After PROMPT stage success, prints positive_prompt, negative_prompt, style_parameters."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "[DEBUG]" in captured
        assert "pixel art knight, 16-bit" in captured
        assert "blurry, low quality" in captured
        assert "pixel_art" in captured

    def test_image_stage_debug_output(self, capsys):
        """After IMAGE stage success, prints generated image path."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "/output/images/knight.png" in captured

    def test_pixelization_stage_debug_output(self, capsys):
        """After PIXELIZATION stage success, prints pixelized image path."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "/output/images/knight_pixelized.png" in captured

    def test_post_processing_stage_debug_output(self, capsys):
        """After POST_PROCESSING stage success, prints all output asset paths."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "/output/assets/knight_32.png" in captured
        assert "/output/assets/knight_64.png" in captured

    def test_pre_processing_debug_output(self, capsys):
        """After PRE_PROCESSING success, prints pre-processed image path."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pre_proc = MagicMock()
        pre_proc.process.return_value = PreProcessingOutput(
            image_path="/output/images/knight_preprocessed.png",
            original_size=(512, 512),
            intermediate_size=256,
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
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "/output/images/knight_preprocessed.png" in captured


class TestDebugOutputDisabled:
    """Tests that no [DEBUG] lines appear in stdout when config.debug=False."""

    def test_no_debug_output_when_disabled(self, capsys):
        """When debug=False, no [DEBUG] lines appear in stdout."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=False
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "[DEBUG]" not in captured

    def test_no_debug_output_default(self, capsys):
        """When debug is not set (default=False), no [DEBUG] lines appear."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight",
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        assert "[DEBUG]" not in captured


class TestDebugOutputOnFailure:
    """Tests debug output behavior when a stage fails."""

    def test_debug_only_for_completed_stages(self, capsys):
        """Debug lines appear for completed stages, not for failed/skipped ones."""
        prompt_gen, image_gen, pixelizer, post_proc, config_mgr = _make_mocks()
        # Make pixelization fail
        pixelizer.generate.side_effect = RuntimeError("pixelization failed")
        pipeline = FullPipeline(
            config_manager=config_mgr,
            prompt_generator=prompt_gen,
            image_generator=image_gen,
            pixelizer=pixelizer,
            post_processor=post_proc,
        )
        config = FullPipelineConfig(
            user_prompt="a pixel knight", debug=True
        )
        pipeline.run(config)
        captured = capsys.readouterr().out

        # PROMPT and IMAGE debug should appear
        assert "pixel art knight, 16-bit" in captured
        assert "/output/images/knight.png" in captured
        # PIXELIZATION and POST_PROCESSING should NOT appear
        assert "knight_pixelized.png" not in captured
        assert "knight_32.png" not in captured
