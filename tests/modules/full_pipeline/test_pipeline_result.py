import pytest
from pydantic import ValidationError
from src.modules.full_pipeline.schemas import (
    FullPipelineResult,
    StageResult,
    PipelineStage,
)


class TestFullPipelineResult:
    def test_full_result_with_stages(self):
        """Create result with multiple stage results and final asset paths."""
        stage_results = [
            StageResult(
                stage=PipelineStage.PROMPT,
                success=True,
                output_path="prompt.txt",
                duration_seconds=1.0,
            ),
            StageResult(
                stage=PipelineStage.IMAGE,
                success=True,
                output_path="image.png",
                duration_seconds=5.0,
            ),
        ]
        result = FullPipelineResult(
            stage_results=stage_results,
            final_asset_paths=["output/sprite_32.png", "output/sprite_64.png"],
            total_duration_seconds=6.0,
        )
        assert len(result.stage_results) == 2
        assert result.stage_results[0].stage == PipelineStage.PROMPT
        assert result.stage_results[1].stage == PipelineStage.IMAGE
        assert result.final_asset_paths == [
            "output/sprite_32.png",
            "output/sprite_64.png",
        ]
        assert result.total_duration_seconds == 6.0

    def test_empty_result(self):
        """Create result with empty lists and zero duration."""
        result = FullPipelineResult(
            stage_results=[],
            final_asset_paths=[],
            total_duration_seconds=0.0,
        )
        assert result.stage_results == []
        assert result.final_asset_paths == []
        assert result.total_duration_seconds == 0.0

    def test_missing_stage_results_raises_error(self):
        """Missing stage_results raises ValidationError."""
        with pytest.raises(ValidationError):
            FullPipelineResult(
                final_asset_paths=[],
                total_duration_seconds=0.0,
            )

    def test_missing_final_asset_paths_raises_error(self):
        """Missing final_asset_paths raises ValidationError."""
        with pytest.raises(ValidationError):
            FullPipelineResult(
                stage_results=[],
                total_duration_seconds=0.0,
            )

    def test_missing_total_duration_raises_error(self):
        """Missing total_duration_seconds raises ValidationError."""
        with pytest.raises(ValidationError):
            FullPipelineResult(
                stage_results=[],
                final_asset_paths=[],
            )
