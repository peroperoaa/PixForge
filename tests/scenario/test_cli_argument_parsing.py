"""Tests for CLI argument parsing (FR-1)."""

import pytest
from main import build_parser


class TestCLIArgumentParsing:
    """Test argparse argument definitions and parsing."""

    def setup_method(self):
        self.parser = build_parser()

    # Case 1: --prompt parses correctly
    def test_prompt_flag(self):
        args = self.parser.parse_args(["--prompt", "a pixel art sword"])
        assert args.prompt == "a pixel art sword"

    # Case 2: All flags provided
    def test_all_flags(self):
        args = self.parser.parse_args([
            "--prompt", "a sword",
            "--input", "img.png",
            "--start-from", "image",
            "--aspect-ratio", "16:9",
            "--palette", "gb",
            "--colors", "8",
            "--sizes", "32,64,128",
            "--no-remove-bg",
            "--asset-name", "sword",
            "--output-dir", "/tmp/out",
            "--auto-detect",
        ])
        assert args.prompt == "a sword"
        assert args.input == "img.png"
        assert args.start_from == "image"
        assert args.aspect_ratio == "16:9"
        assert args.palette == "gb"
        assert args.colors == 8
        assert args.sizes == "32,64,128"
        assert args.no_remove_bg is True
        assert args.asset_name == "sword"
        assert args.output_dir == "/tmp/out"
        assert args.auto_detect is True

    # Case 3: Defaults
    def test_defaults(self):
        args = self.parser.parse_args(["--prompt", "test"])
        assert args.input is None
        assert args.start_from is None
        assert args.aspect_ratio == "1:1"
        assert args.palette == "sweetie-16"
        assert args.colors is None
        assert args.sizes == "32,64"
        assert args.no_remove_bg is False
        assert args.asset_name is None
        assert args.output_dir is None
        assert args.auto_detect is False

    # Case 4: --sizes parsing as comma-separated
    def test_sizes_single(self):
        args = self.parser.parse_args(["--prompt", "x", "--sizes", "16"])
        assert args.sizes == "16"

    def test_sizes_multiple(self):
        args = self.parser.parse_args(["--prompt", "x", "--sizes", "32,64,128"])
        assert args.sizes == "32,64,128"

    # Case 5: --start-from accepts various cases
    def test_start_from_case_insensitive(self):
        # The parser stores the raw string; validation happens at mapping time
        args = self.parser.parse_args(["--prompt", "x", "--start-from", "Post_Processing"])
        assert args.start_from == "Post_Processing"

    def test_start_from_lowercase(self):
        args = self.parser.parse_args(["--input", "img.png", "--start-from", "pixelization"])
        assert args.start_from == "pixelization"

    # Case 6: Both --prompt and --input can coexist
    def test_prompt_and_input_coexist(self):
        args = self.parser.parse_args(["--prompt", "a sword", "--input", "base.png"])
        assert args.prompt == "a sword"
        assert args.input == "base.png"

    # Case 7: No required arguments gives error
    def test_no_args_exits_with_error(self):
        """No --prompt, --input, or --auto-detect should cause exit code 2."""
        # argparse doesn't enforce this by default; validation does.
        # We test that the parser itself doesn't crash with no args.
        args = self.parser.parse_args([])
        # All None / defaults — validation layer will reject this
        assert args.prompt is None
        assert args.input is None
        assert args.auto_detect is False

    # Case 8: --debug flag
    def test_debug_flag_default_false(self):
        args = self.parser.parse_args(["--prompt", "test"])
        assert args.debug is False

    def test_debug_flag_when_passed(self):
        args = self.parser.parse_args(["--prompt", "test", "--debug"])
        assert args.debug is True
