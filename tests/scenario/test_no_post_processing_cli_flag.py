"""Tests for --no-post-processing CLI flag parsing."""

import pytest
from main import build_parser


class TestNoPostProcessingCLIFlag:
    """Test that --no-post-processing flag is parsed correctly."""

    def setup_method(self):
        self.parser = build_parser()

    # Case 1: --no-post-processing flag sets no_post_processing to True
    def test_no_post_processing_flag_present(self):
        args = self.parser.parse_args(["--prompt", "test", "--no-post-processing"])
        assert args.no_post_processing is True

    # Case 2: Default (no --no-post-processing) sets no_post_processing to False
    def test_no_post_processing_flag_default(self):
        args = self.parser.parse_args(["--prompt", "test"])
        assert args.no_post_processing is False
