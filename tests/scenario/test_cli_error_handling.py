"""Tests for CLI error handling and exit codes (FR-4)."""

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

from main import run_pipeline, main as cli_main, build_parser, args_to_config
from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
    StageResult,
)


def _success_result() -> FullPipelineResult:
    return FullPipelineResult(
        stage_results=[
            StageResult(stage=PipelineStage.PROMPT, success=True, output_path=None, duration_seconds=0.1),
            StageResult(stage=PipelineStage.IMAGE, success=True, output_path="/out/img.png", duration_seconds=0.5),
            StageResult(stage=PipelineStage.PIXELIZATION, success=True, output_path="/out/pix.png", duration_seconds=0.3),
            StageResult(stage=PipelineStage.POST_PROCESSING, success=True, output_path="/out/a.png", duration_seconds=0.2),
        ],
        final_asset_paths=["/out/a_32.png"],
        total_duration_seconds=1.1,
    )


def _error_result() -> FullPipelineResult:
    return FullPipelineResult(
        stage_results=[
            StageResult(stage=PipelineStage.PROMPT, success=True, output_path=None, duration_seconds=0.1),
            StageResult(stage=PipelineStage.IMAGE, success=False, error_message="API timeout", duration_seconds=0.5),
        ],
        final_asset_paths=[],
        total_duration_seconds=0.6,
    )


class TestExitCodes:
    """Test exit codes for various conditions."""

    # Case 1: Success -> exit code 0
    @patch("main.create_pipeline")
    def test_success_exit_code(self, mock_create):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _success_result()
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)
        assert exit_code == 0

    # Case 2: Pipeline error -> exit code 1
    @patch("main.create_pipeline")
    def test_pipeline_error_exit_code(self, mock_create):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _error_result()
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)
        assert exit_code == 1

    # Case 3: Argument error -> exit code 2
    def test_argument_error_exit_code(self):
        """Invalid --start-from value should exit with code 2."""
        parser = build_parser()
        args = parser.parse_args(["--prompt", "x", "--start-from", "bogus"])
        with pytest.raises(SystemExit) as exc_info:
            args_to_config(args)
        assert exc_info.value.code == 2

    # Case 4: KeyboardInterrupt handling
    @patch("main.create_pipeline")
    def test_keyboard_interrupt(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.side_effect = KeyboardInterrupt()
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        assert exit_code == 130
        assert "interrupt" in captured.lower() or "cancel" in captured.lower()

    # Case 5: Unexpected exception -> exit code 1
    @patch("main.create_pipeline")
    def test_unexpected_exception(self, mock_create, capsys):
        mock_pipeline = MagicMock()
        mock_pipeline.run.side_effect = RuntimeError("something broke")
        mock_create.return_value = mock_pipeline

        config = FullPipelineConfig(user_prompt="sword")
        exit_code = run_pipeline(config)

        captured = capsys.readouterr().out
        assert exit_code == 1
        assert "something broke" in captured.lower() or "error" in captured.lower()


class TestCLIMainIntegration:
    """Test the main() function end-to-end with mocked pipeline."""

    @patch("main.create_pipeline")
    def test_main_success(self, mock_create):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _success_result()
        mock_create.return_value = mock_pipeline

        with patch("sys.argv", ["main.py", "--prompt", "a pixel art sword"]):
            exit_code = cli_main()
        assert exit_code == 0

    @patch("main.create_pipeline")
    def test_main_with_input_start_from(self, mock_create):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _success_result()
        mock_create.return_value = mock_pipeline

        with patch("sys.argv", ["main.py", "--input", "img.png", "--start-from", "post_processing"]):
            exit_code = cli_main()
        assert exit_code == 0

    @patch("main.create_pipeline")
    def test_main_auto_detect(self, mock_create):
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = _success_result()
        mock_create.return_value = mock_pipeline

        with patch("sys.argv", ["main.py", "--auto-detect"]):
            exit_code = cli_main()
        assert exit_code == 0
        # Verify config passed to pipeline has start_stage=None
        call_args = mock_pipeline.run.call_args[0][0]
        assert call_args.start_stage is None
