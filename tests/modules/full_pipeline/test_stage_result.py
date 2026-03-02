import pytest
from pydantic import ValidationError
from src.modules.full_pipeline.schemas import StageResult, PipelineStage


class TestStageResult:
    def test_successful_stage_result(self):
        """Create a successful StageResult with output_path."""
        result = StageResult(
            stage=PipelineStage.IMAGE,
            success=True,
            output_path="output/image.png",
            duration_seconds=2.5,
        )
        assert result.stage == PipelineStage.IMAGE
        assert result.success is True
        assert result.output_path == "output/image.png"
        assert result.error_message is None
        assert result.duration_seconds == 2.5

    def test_failed_stage_result(self):
        """Create a failed StageResult with error_message."""
        result = StageResult(
            stage=PipelineStage.PIXELIZATION,
            success=False,
            error_message="Connection timeout",
            duration_seconds=10.0,
        )
        assert result.stage == PipelineStage.PIXELIZATION
        assert result.success is False
        assert result.output_path is None
        assert result.error_message == "Connection timeout"
        assert result.duration_seconds == 10.0

    def test_missing_stage_raises_error(self):
        """Missing stage raises ValidationError."""
        with pytest.raises(ValidationError):
            StageResult(success=True, duration_seconds=1.0)

    def test_missing_success_raises_error(self):
        """Missing success raises ValidationError."""
        with pytest.raises(ValidationError):
            StageResult(stage=PipelineStage.PROMPT, duration_seconds=1.0)

    def test_missing_duration_raises_error(self):
        """Missing duration_seconds raises ValidationError."""
        with pytest.raises(ValidationError):
            StageResult(stage=PipelineStage.PROMPT, success=True)
