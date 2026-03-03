"""Tests for conditional PreProcessor creation in pipeline factory (FR-2)."""

import pytest
from unittest.mock import patch, MagicMock

from main import create_pipeline, build_parser, args_to_config, run_pipeline


class TestConditionalPreProcessorCreation:
    """Test that PreProcessor is only created when --pre-process is passed."""

    # Case 1: Default - no pre_process flag, pre_processor is None
    @patch("src.modules.post_processing.pipeline.PostProcessingPipeline")
    @patch("src.modules.pixelization.comfyui_adapter.ComfyUIAdapter")
    @patch("src.modules.image_gen.gemini_adapter.GeminiImageAdapter")
    @patch("src.modules.prompt_gen.gemini_adapter.GeminiAdapter")
    @patch("src.core.config.ConfigManager")
    def test_default_no_preprocessor(
        self, mock_cm, mock_prompt, mock_img, mock_comfy, mock_pp
    ):
        pipeline = create_pipeline(pre_process=False)
        assert pipeline._pre_processor is None

    # Case 2: pre_process=True, PreProcessor is created
    @patch("src.modules.pre_processing.pipeline.PreProcessor")
    @patch("src.modules.post_processing.pipeline.PostProcessingPipeline")
    @patch("src.modules.pixelization.comfyui_adapter.ComfyUIAdapter")
    @patch("src.modules.image_gen.gemini_adapter.GeminiImageAdapter")
    @patch("src.modules.prompt_gen.gemini_adapter.GeminiAdapter")
    @patch("src.core.config.ConfigManager")
    def test_with_preprocessor(
        self, mock_cm, mock_prompt, mock_img, mock_comfy, mock_pp, mock_pre
    ):
        pipeline = create_pipeline(pre_process=True)
        assert pipeline._pre_processor is not None
        mock_pre.assert_called_once()

    # Case 3: run_pipeline threads pre_process from config
    @patch("main.create_pipeline")
    def test_run_pipeline_threads_flag(self, mock_create_pipeline):
        mock_pipeline = MagicMock()
        mock_result = MagicMock()
        mock_result.stage_results = []
        mock_result.final_asset_paths = []
        mock_result.total_duration_seconds = 0.0
        mock_pipeline.run.return_value = mock_result
        mock_create_pipeline.return_value = mock_pipeline

        parser = build_parser()
        args = parser.parse_args(["--prompt", "test", "--pre-process"])
        config = args_to_config(args)
        run_pipeline(config, pre_process=True)

        mock_create_pipeline.assert_called_once_with(pre_process=True)
