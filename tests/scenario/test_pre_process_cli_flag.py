"""Tests for --pre-process CLI flag parsing (FR-1)."""

import pytest
from main import build_parser


class TestPreProcessCLIFlag:
    """Test that --pre-process flag is parsed correctly."""

    def setup_method(self):
        self.parser = build_parser()

    # Case 1: --pre-process flag sets pre_process to True
    def test_pre_process_flag_present(self):
        args = self.parser.parse_args(["--prompt", "test", "--pre-process"])
        assert args.pre_process is True

    # Case 2: Default (no --pre-process) sets pre_process to False
    def test_pre_process_flag_default(self):
        args = self.parser.parse_args(["--prompt", "test"])
        assert args.pre_process is False
