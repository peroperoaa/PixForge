"""Tests for pipeline execution with progress output (FR-3)."""

import io
from unittest.mock import MagicMock, patch

import pytest

from main import run_pipeline, build_parser, args_to_config
from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
    StageResult,
)


def _make_result(
    stages: list[PipelineStage],
    success: bool = True,
    error_stage: PipelineStage | None = None,
    asset_paths: list[str] | None = None,
) -> FullPipelineResult:
    """Helper to build a FullPipelineResult."""
    results = []
    for s in stages:
        if s == error_stage:
            results.append(StageResult(stage=s, success=False, error_message="boom", duration_seconds=0.1))
            break
        results.append(StageResult(stage=s, success=True, output_path=f"/out/{s.name.lower()}.png", duration_seconds=0.5))
    return FullPipelineResult(
        stage_results=results,
        final_asset_paths=asset_paths or ["/out/asset_32.png", "/out/asset_64.png"],
        total_duration_seconds=2.0,
    )


class TestPipelineProgress:
    """Test progress output during pipeline execution."""

    # Case 1: Full pipeline prints progress for all 4 stages
    @patch("main.create_pipeline")
    def test_full_pipeline_progress(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _make_result(
            [PipelineStage.PROMPT, PipelineStage.IMAGE, PipelineStage.PIXELIZATION, PipelineStage.POST_PROCESSING],
            asset_paths=["/out/sword_32.png", "/out/sword_64.png"],
        )
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="a pixel art sword")
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        assert "PROMPT" in captured
        assert "IMAGE" in captured
        assert "PIXELIZATION" in captured
        assert "POST_PROCESSING" in captured
        assert "/out/sword_32.png" in captured
        assert exit_code == 0

    # Case 2: Partial run only shows executed stages
    @patch("main.create_pipeline")
    def test_partial_pipeline_progress(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _make_result(
            [PipelineStage.PIXELIZATION, PipelineStage.POST_PROCESSING],
            asset_paths=["/out/asset_32.png"],
        )
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(
            input_image_path="img.png",
            start_stage=PipelineStage.PIXELIZATION,
        )
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        assert "PIXELIZATION" in captured
        assert "POST_PROCESSING" in captured
        assert exit_code == 0

    # Case 3: Error in stage
    @patch("main.create_pipeline")
    def test_error_stage_progress(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _make_result(
            [PipelineStage.PROMPT, PipelineStage.IMAGE],
            error_stage=PipelineStage.IMAGE,
        )
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        assert "PROMPT" in captured
        assert "IMAGE" in captured
        assert "boom" in captured.lower() or "error" in captured.lower()
        assert exit_code == 1

    # Case 4: Summary includes asset paths and total time
    @patch("main.create_pipeline")
    def test_summary_format(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _make_result(
            [PipelineStage.PROMPT, PipelineStage.IMAGE, PipelineStage.PIXELIZATION, PipelineStage.POST_PROCESSING],
            asset_paths=["/out/sword_32.png", "/out/sword_64.png"],
        )
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        # Check summary has paths and time
        assert "/out/sword_32.png" in captured
        assert "/out/sword_64.png" in captured
        assert "2.0" in captured or "2.00" in captured
        assert exit_code == 0
