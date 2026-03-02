import pytest
from src.modules.prompt_gen.schemas import PromptOutput


class TestPixelArtStyleParameters:
    """FR-2: style_parameters field description includes pixel-art constraint guidance."""

    def test_style_parameters_description_contains_pixel_art_guidance(self):
        """The style_parameters field description should mention pixel-art guidance."""
        field_info = PromptOutput.model_fields["style_parameters"]
        description = field_info.description.lower()
        assert "pixel" in description or "pixel art" in description or "pixel-art" in description, (
            f"Expected pixel-art guidance in style_parameters description, got: {field_info.description}"
        )

    def test_style_parameters_description_mentions_expected_keys(self):
        """The style_parameters field description should mention expected keys like view_angle, background_type, outline_style."""
        field_info = PromptOutput.model_fields["style_parameters"]
        description = field_info.description.lower()
        has_view = "view_angle" in description or "view angle" in description
        has_bg = "background_type" in description or "background" in description
        has_outline = "outline" in description
        assert has_view and has_bg and has_outline, (
            f"Expected view_angle, background, outline mentions in description, got: {field_info.description}"
        )

    def test_schema_export_includes_updated_description(self):
        """JSON schema export should include the updated description."""
        schema = PromptOutput.model_json_schema()
        style_props = schema["properties"]["style_parameters"]
        description = style_props.get("description", "").lower()
        assert "pixel" in description or "pixel art" in description or "pixel-art" in description, (
            f"Expected pixel-art reference in schema description, got: {style_props}"
        )
