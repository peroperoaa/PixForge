import pytest
from pydantic import ValidationError
from src.modules.full_pipeline.schemas import FullPipelineConfig, PipelineStage


class TestFullPipelineConfigDefaults:
    def test_defaults_with_user_prompt(self):
        """Create config with user_prompt only; verify all defaults."""
        config = FullPipelineConfig(user_prompt="a pixel art knight")
        assert config.user_prompt == "a pixel art knight"
        assert config.input_image_path is None
        assert config.start_stage == PipelineStage.PROMPT
        assert config.aspect_ratio == "1:1"
        assert config.palette_preset is None
        assert config.color_count is None
        assert config.target_sizes == [64, 128]
        assert config.remove_background is True
        assert config.asset_name is None
        assert config.output_dir is None

    def test_all_fields_explicit(self):
        """All fields set explicitly are stored correctly."""
        config = FullPipelineConfig(
            user_prompt="a pixel art knight",
            input_image_path="input.png",
            start_stage=PipelineStage.PROMPT,
            aspect_ratio="16:9",
            palette_preset="endesga-32",
            color_count=32,
            target_sizes=[16, 32, 64],
            remove_background=False,
            asset_name="knight_sprite",
            output_dir="/output",
        )
        assert config.user_prompt == "a pixel art knight"
        assert config.input_image_path == "input.png"
        assert config.start_stage == PipelineStage.PROMPT
        assert config.aspect_ratio == "16:9"
        assert config.palette_preset == "endesga-32"
        assert config.color_count == 32
        assert config.target_sizes == [16, 32, 64]
        assert config.remove_background is False
        assert config.asset_name == "knight_sprite"
        assert config.output_dir == "/output"


class TestFullPipelineConfigCrossValidation:
    def test_prompt_stage_requires_user_prompt(self):
        """start_stage=PROMPT without user_prompt raises ValidationError."""
        with pytest.raises(ValidationError, match="user_prompt"):
            FullPipelineConfig(start_stage=PipelineStage.PROMPT)

    def test_image_stage_requires_input_image_path(self):
        """start_stage=IMAGE without input_image_path raises ValidationError."""
        with pytest.raises(ValidationError, match="input_image_path"):
            FullPipelineConfig(start_stage=PipelineStage.IMAGE)

    def test_pixelization_stage_requires_input_image_path(self):
        """start_stage=PIXELIZATION without input_image_path raises ValidationError."""
        with pytest.raises(ValidationError, match="input_image_path"):
            FullPipelineConfig(start_stage=PipelineStage.PIXELIZATION)

    def test_post_processing_stage_requires_input_image_path(self):
        """start_stage=POST_PROCESSING without input_image_path raises ValidationError."""
        with pytest.raises(ValidationError, match="input_image_path"):
            FullPipelineConfig(start_stage=PipelineStage.POST_PROCESSING)

    def test_image_stage_valid_with_input_image_path(self):
        """start_stage=IMAGE with input_image_path succeeds."""
        config = FullPipelineConfig(
            start_stage=PipelineStage.IMAGE,
            input_image_path="input.png",
        )
        assert config.input_image_path == "input.png"
        assert config.start_stage == PipelineStage.IMAGE

    def test_pixelization_stage_valid_with_input_image_path(self):
        """start_stage=PIXELIZATION with input_image_path succeeds."""
        config = FullPipelineConfig(
            start_stage=PipelineStage.PIXELIZATION,
            input_image_path="input.png",
        )
        assert config.input_image_path == "input.png"

    def test_post_processing_stage_valid_with_input_image_path(self):
        """start_stage=POST_PROCESSING with input_image_path succeeds."""
        config = FullPipelineConfig(
            start_stage=PipelineStage.POST_PROCESSING,
            input_image_path="input.png",
        )
        assert config.input_image_path == "input.png"

    def test_prompt_stage_does_not_require_input_image_path(self):
        """start_stage=PROMPT without input_image_path is valid."""
        config = FullPipelineConfig(
            user_prompt="a knight",
            start_stage=PipelineStage.PROMPT,
        )
        assert config.input_image_path is None
