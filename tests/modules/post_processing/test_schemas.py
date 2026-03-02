import pytest
from pydantic import ValidationError
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


class TestPostProcessingInput:
    def test_accepts_valid_fields(self):
        """PostProcessingInput accepts valid image_path, asset_name, target_sizes=[32,64], remove_background=True, color_count=16."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32, 64],
            remove_background=True,
            color_count=16,
        )
        assert input_data.image_path == "input.png"
        assert input_data.asset_name == "hero_sprite"
        assert input_data.target_sizes == [32, 64]
        assert input_data.remove_background is True
        assert input_data.color_count == 16

    def test_rejects_empty_target_sizes(self):
        """PostProcessingInput rejects empty target_sizes list."""
        with pytest.raises(ValidationError):
            PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[],
                color_count=16,
            )

    def test_rejects_non_positive_target_sizes(self):
        """PostProcessingInput rejects target_sizes containing non-positive integers."""
        with pytest.raises(ValidationError):
            PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[32, 0, 64],
                color_count=16,
            )
        with pytest.raises(ValidationError):
            PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[-1, 32],
                color_count=16,
            )

    def test_accepts_palette_path_without_color_count(self):
        """PostProcessingInput accepts palette_path without color_count (palette mode)."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            palette_path="/palettes/retro.hex",
        )
        assert input_data.palette_path == "/palettes/retro.hex"
        assert input_data.color_count is None

    def test_accepts_color_count_without_palette_path(self):
        """PostProcessingInput accepts color_count without palette_path (K-Means mode)."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[64],
            color_count=8,
        )
        assert input_data.color_count == 8
        assert input_data.palette_path is None

    def test_rejects_neither_palette_path_nor_color_count(self):
        """PostProcessingInput rejects when both palette_path and color_count are None."""
        with pytest.raises(ValidationError):
            PostProcessingInput(
                image_path="input.png",
                asset_name="hero_sprite",
                target_sizes=[32],
            )

    def test_remove_background_defaults_false(self):
        """PostProcessingInput defaults remove_background to False."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            color_count=16,
        )
        assert input_data.remove_background is False

    def test_output_dir_is_optional(self):
        """PostProcessingInput allows output_dir to be None."""
        input_data = PostProcessingInput(
            image_path="input.png",
            asset_name="hero_sprite",
            target_sizes=[32],
            color_count=16,
        )
        assert input_data.output_dir is None


class TestPostProcessingOutput:
    def test_serializes_output_paths_as_list_of_strings(self):
        """PostProcessingOutput serializes output_paths as list of file path strings."""
        output = PostProcessingOutput(
            output_paths=["/out/hero_32.png", "/out/hero_64.png"],
            target_sizes=[32, 64],
            color_count=16,
            palette_name=None,
        )
        assert output.output_paths == ["/out/hero_32.png", "/out/hero_64.png"]
        assert isinstance(output.output_paths, list)
        assert all(isinstance(p, str) for p in output.output_paths)

    def test_output_optional_fields(self):
        """PostProcessingOutput allows optional fields to be None."""
        output = PostProcessingOutput(
            output_paths=["/out/hero_32.png"],
            target_sizes=[32],
        )
        assert output.color_count is None
        assert output.palette_name is None
