"""Tests for CLI argument-to-config mapping (FR-2)."""

import pytest
from main import build_parser, args_to_config
from src.modules.full_pipeline.schemas import FullPipelineConfig, PipelineStage


class TestArgsToConfigMapping:
    """Test mapping from argparse Namespace to FullPipelineConfig."""

    def setup_method(self):
        self.parser = build_parser()

    # Case 1: Palette preset name
    def test_palette_preset(self):
        args = self.parser.parse_args(["--prompt", "sword", "--palette", "sweetie-16"])
        config = args_to_config(args)
        assert config.palette_preset == "sweetie-16"
        assert config.user_prompt == "sword"

    # Case 2: Hex file palette
    def test_palette_hex_file(self):
        args = self.parser.parse_args([
            "--input", "img.png",
            "--start-from", "pixelization",
            "--palette", "custom.hex",
        ])
        config = args_to_config(args)
        assert config.palette_preset == "custom.hex"

    def test_palette_hex_file_detection(self):
        """A .hex extension should be treated as a file path."""
        args = self.parser.parse_args([
            "--input", "img.png",
            "--start-from", "post_processing",
            "--palette", "/path/to/palette.hex",
        ])
        config = args_to_config(args)
        assert config.palette_preset == "/path/to/palette.hex"

    # Case 3: K-Means mode
    def test_kmeans_mode(self):
        args = self.parser.parse_args(["--prompt", "sword", "--colors", "8"])
        config = args_to_config(args)
        assert config.color_count == 8

    # Case 4: Auto-detect mode
    def test_auto_detect(self):
        args = self.parser.parse_args(["--auto-detect", "--input", "img.png"])
        config = args_to_config(args)
        assert config.start_stage is None

    # Case 5: Start-from mapping
    def test_start_from_prompt(self):
        args = self.parser.parse_args(["--prompt", "sword", "--start-from", "prompt"])
        config = args_to_config(args)
        assert config.start_stage == PipelineStage.PROMPT

    def test_start_from_image(self):
        args = self.parser.parse_args(["--prompt", "sword", "--input", "img.png", "--start-from", "image"])
        config = args_to_config(args)
        assert config.start_stage == PipelineStage.IMAGE

    def test_start_from_pixelization(self):
        args = self.parser.parse_args(["--input", "img.png", "--start-from", "pixelization"])
        config = args_to_config(args)
        assert config.start_stage == PipelineStage.PIXELIZATION

    def test_start_from_post_processing(self):
        args = self.parser.parse_args(["--input", "img.png", "--start-from", "post_processing"])
        config = args_to_config(args)
        assert config.start_stage == PipelineStage.POST_PROCESSING

    def test_start_from_case_insensitive(self):
        args = self.parser.parse_args(["--input", "img.png", "--start-from", "Post_Processing"])
        config = args_to_config(args)
        assert config.start_stage == PipelineStage.POST_PROCESSING

    def test_invalid_start_from(self):
        args = self.parser.parse_args(["--prompt", "sword", "--start-from", "invalid_stage"])
        with pytest.raises(SystemExit) as exc_info:
            args_to_config(args)
        assert exc_info.value.code == 2

    # Case 6: no-remove-bg
    def test_no_remove_bg(self):
        args = self.parser.parse_args(["--prompt", "sword", "--no-remove-bg"])
        config = args_to_config(args)
        assert config.remove_background is False

    def test_remove_bg_default(self):
        args = self.parser.parse_args(["--prompt", "sword"])
        config = args_to_config(args)
        assert config.remove_background is True

    # Case 7: Output dir and asset name
    def test_output_dir_and_asset_name(self):
        args = self.parser.parse_args([
            "--prompt", "sword",
            "--output-dir", "/tmp/out",
            "--asset-name", "my_sword",
        ])
        config = args_to_config(args)
        assert config.output_dir == "/tmp/out"
        assert config.asset_name == "my_sword"

    # Sizes parsing
    def test_sizes_parsing(self):
        args = self.parser.parse_args(["--prompt", "sword", "--sizes", "16,32,64"])
        config = args_to_config(args)
        assert config.target_sizes == [16, 32, 64]

    def test_sizes_default(self):
        args = self.parser.parse_args(["--prompt", "sword"])
        config = args_to_config(args)
        assert config.target_sizes == [32, 64]

    # Aspect ratio
    def test_aspect_ratio(self):
        args = self.parser.parse_args(["--prompt", "sword", "--aspect-ratio", "16:9"])
        config = args_to_config(args)
        assert config.aspect_ratio == "16:9"

    # Validation: no prompt or input without auto-detect
    def test_no_prompt_no_input_no_autodetect_raises(self):
        args = self.parser.parse_args([])
        with pytest.raises(SystemExit) as exc_info:
            args_to_config(args)
        assert exc_info.value.code == 2

    # Debug flag mapping
    def test_debug_default_false_in_config(self):
        args = self.parser.parse_args(["--prompt", "sword"])
        config = args_to_config(args)
        assert config.debug is False

    def test_debug_true_when_flag_passed(self):
        args = self.parser.parse_args(["--prompt", "sword", "--debug"])
        config = args_to_config(args)
        assert config.debug is True
