"""Tests for FR-1: Default palette_preset is None."""

import pytest
from main import build_parser, args_to_config
from src.modules.full_pipeline.schemas import FullPipelineConfig


class TestDisableDefaultPalette:
    """Verify that palette_preset defaults to None everywhere."""

    # Case 1: FullPipelineConfig default is None
    def test_config_palette_preset_default_is_none(self):
        config = FullPipelineConfig(user_prompt="test prompt")
        assert config.palette_preset is None

    # Case 2: Explicit palette_preset still works
    def test_config_explicit_palette_preset(self):
        config = FullPipelineConfig(user_prompt="test", palette_preset="sweetie-16")
        assert config.palette_preset == "sweetie-16"

    # Case 3: CLI --palette defaults to None
    def test_cli_palette_default_is_none(self):
        parser = build_parser()
        args = parser.parse_args(["--prompt", "x"])
        assert args.palette is None

    # Case 4: CLI explicit --palette works
    def test_cli_explicit_palette(self):
        parser = build_parser()
        args = parser.parse_args(["--prompt", "x", "--palette", "gb"])
        assert args.palette == "gb"

    # Case 5: args_to_config with no palette -> config.palette_preset is None
    def test_args_to_config_default_palette_none(self):
        parser = build_parser()
        args = parser.parse_args(["--prompt", "sword"])
        config = args_to_config(args)
        assert config.palette_preset is None

    # Case 6: args_to_config with explicit palette
    def test_args_to_config_explicit_palette(self):
        parser = build_parser()
        args = parser.parse_args(["--prompt", "sword", "--palette", "sweetie-16"])
        config = args_to_config(args)
        assert config.palette_preset == "sweetie-16"
