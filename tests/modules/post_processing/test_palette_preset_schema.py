"""Tests for palette_preset support in PostProcessingInput schema."""

import pytest
from pydantic import ValidationError

from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


class TestPalettePresetSchema:
    """Tests for palette_preset field on PostProcessingInput."""

    def test_accepts_palette_preset_sweetie16(self):
        """PostProcessingInput accepts palette_preset='sweetie-16' without palette_path."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            palette_preset="sweetie-16",
        )
        assert input_data.palette_preset == "sweetie-16"
        assert input_data.palette_path is None

    def test_palette_preset_defaults_to_none(self):
        """PostProcessingInput defaults palette_preset to None."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
        )
        assert input_data.palette_preset is None

    def test_rejects_both_palette_preset_and_palette_path(self):
        """PostProcessingInput raises ValidationError when both palette_preset and palette_path are set."""
        with pytest.raises(ValidationError, match="Cannot specify both"):
            PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[32],
                palette_preset="sweetie-16",
                palette_path="/palettes/retro.hex",
            )

    def test_accepts_palette_preset_without_color_count(self):
        """PostProcessingInput accepts palette_preset with color_count=None."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            palette_preset="gb",
        )
        assert input_data.palette_preset == "gb"
        assert input_data.color_count is None

    def test_accepts_palette_preset_with_color_count(self):
        """PostProcessingInput accepts palette_preset alongside color_count (preset takes priority in pipeline)."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            palette_preset="sweetie-16",
            color_count=8,
        )
        assert input_data.palette_preset == "sweetie-16"
        assert input_data.color_count == 8
