"""Tests for FullPipeline orchestrator - auto-detect mode."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

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


class TestAutoDetectMode:
    def test_auto_detect_no_artifacts_runs_full_pipeline(self):
        """When auto-detect finds no artifacts, pipeline starts from PROMPT."""
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
            start_stage=None,
        )

        mock_detector = MagicMock()
        mock_detector.detect_start_stage.return_value = (PipelineStage.PROMPT, None)

        with patch(
            "src.modules.full_pipeline.orchestrator.ArtifactDetector",
            return_value=mock_detector,
        ):
            result = pipeline.run(config)

        assert len(result.stage_results) == 4
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        prompt_gen.generate.assert_called_once()

    def test_auto_detect_image_artifacts_skips_to_pixelization(self):
        """When auto-detect finds image artifacts, pipeline starts from PIXELIZATION."""
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
            start_stage=None,
        )

        detected_path = Path("/output/images/knight.png")
        mock_detector = MagicMock()
        mock_detector.detect_start_stage.return_value = (PipelineStage.PIXELIZATION, detected_path)

        with patch(
            "src.modules.full_pipeline.orchestrator.ArtifactDetector",
            return_value=mock_detector,
        ):
            result = pipeline.run(config)

        assert len(result.stage_results) == 2
        assert result.stage_results[0].stage == PipelineStage.PIXELIZATION
        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_not_called()
        pixelizer.generate.assert_called_once()

        # Verify the detected path was used
        pix_call_args = pixelizer.generate.call_args
        pix_input = pix_call_args[0][0] if pix_call_args[0] else pix_call_args[1].get("input_data")
        assert pix_input.image_path == str(detected_path)

    def test_auto_detect_pixelized_artifacts_skips_to_post_processing(self):
        """When auto-detect finds pixelized artifacts, pipeline starts from POST_PROCESSING."""
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
            start_stage=None,
        )

        detected_path = Path("/output/images/knight_pixelized.png")
        mock_detector = MagicMock()
        mock_detector.detect_start_stage.return_value = (PipelineStage.POST_PROCESSING, detected_path)

        with patch(
            "src.modules.full_pipeline.orchestrator.ArtifactDetector",
            return_value=mock_detector,
        ):
            result = pipeline.run(config)

        assert len(result.stage_results) == 1
        assert result.stage_results[0].stage == PipelineStage.POST_PROCESSING
        prompt_gen.generate.assert_not_called()
        image_gen.generate.assert_not_called()
        pixelizer.generate.assert_not_called()
        post_proc.process.assert_called_once()
