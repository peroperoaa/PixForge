import pytest
from unittest.mock import MagicMock
from google.genai import types
from src.core.config import ConfigManager
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput
from src.modules.prompt_gen.gemini_adapter import GeminiAdapter


@pytest.fixture
def adapter(mocker):
    mocker.patch("src.modules.prompt_gen.gemini_adapter.genai.Client")
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    return GeminiAdapter(config)


class TestPixelArtTestVerification:
    """FR-3: Updated unit tests verify pixel-art system instruction content."""

    def test_construct_request_system_instruction_has_pixel_art_keywords(self, adapter):
        """The existing test_construct_request scenario should verify pixel-art keywords."""
        prompt_input = PromptInput(text_prompt="A majestic lion")
        _, config = adapter._construct_request(prompt_input)

        instruction = config.system_instruction.lower()
        # All these keywords must be present
        assert "centered" in instruction
        assert "clear outlines" in instruction
        assert ("simple background" in instruction or "transparent background" in instruction)
        assert ("front view" in instruction or "3/4 view" in instruction)
        assert ("pixel" in instruction)

    def test_generate_still_works_with_updated_instruction(self, adapter, mocker):
        """Existing generate flow must still work after system instruction update."""
        mock_client = mocker.patch("src.modules.prompt_gen.gemini_adapter.genai.Client").return_value
        # Re-create adapter with fresh mock
        config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
        adapter2 = GeminiAdapter(config)

        mock_response = MagicMock()
        expected_output = PromptOutput(
            positive_prompt="pixel art warrior, centered, clear outlines",
            negative_prompt="blurry, photorealistic",
            style_parameters={"view_angle": "front", "background_type": "transparent"}
        )
        mock_response.parsed = expected_output
        mock_client.models.generate_content.return_value = mock_response

        prompt_input = PromptInput(text_prompt="A warrior character")
        output = adapter2.generate(prompt_input)

        assert output == expected_output
        mock_client.models.generate_content.assert_called_once()
