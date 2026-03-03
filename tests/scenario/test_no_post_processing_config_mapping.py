"""Tests for --no-post-processing config mapping."""

import argparse
import pytest
from main import args_to_config


class TestNoPostProcessingConfigMapping:
    """Test that no_post_processing CLI arg maps to skip_post_processing config field."""

    def _make_args(self, **overrides) -> argparse.Namespace:
        """Create a minimal argparse.Namespace with defaults."""
        defaults = dict(
            prompt="test prompt",
            input=None,
            start_from=None,
            auto_detect=False,
            aspect_ratio="1:1",
            palette=None,
            colors=None,
            sizes="64,128",
            no_remove_bg=False,
            asset_name=None,
            output_dir=None,
            debug=False,
            pre_process=False,
            no_post_processing=False,
        )
        defaults.update(overrides)
        return argparse.Namespace(**defaults)

    # Case 1: no_post_processing=True maps to skip_post_processing=True
    def test_flag_true_maps_to_config(self):
        args = self._make_args(no_post_processing=True)
        config = args_to_config(args)
        assert config.skip_post_processing is True

    # Case 2: no_post_processing=False maps to skip_post_processing=False
    def test_flag_false_maps_to_config(self):
        args = self._make_args(no_post_processing=False)
        config = args_to_config(args)
        assert config.skip_post_processing is False
