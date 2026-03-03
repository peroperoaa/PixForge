import pytest
from src.modules.full_pipeline.schemas import FullPipelineConfig, PipelineStage


class TestFullPipelineConfigDebugField:
    """Tests for the debug boolean field on FullPipelineConfig."""

    def test_debug_defaults_to_false(self):
        """When debug is not provided, it defaults to False."""
        config = FullPipelineConfig(user_prompt="a pixel art knight")
        assert config.debug is False

    def test_debug_explicit_true(self):
        """When debug=True is passed, the field stores True."""
        config = FullPipelineConfig(user_prompt="a pixel art knight", debug=True)
        assert config.debug is True

    def test_debug_explicit_false(self):
        """When debug=False is passed explicitly, the field stores False."""
        config = FullPipelineConfig(user_prompt="a pixel art knight", debug=False)
        assert config.debug is False
