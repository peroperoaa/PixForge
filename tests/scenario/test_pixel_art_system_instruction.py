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


class TestPixelArtSystemInstruction:
    """FR-1: system_instruction contains pixel-art-specific constraints."""

    def test_system_instruction_contains_centered(self, adapter):
        """System instruction must mention centered subject."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        assert "centered" in instruction, f"Expected 'centered' in system instruction, got: {config.system_instruction}"

    def test_system_instruction_contains_simple_or_transparent_background(self, adapter):
        """System instruction must mention simple or transparent background."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        has_simple = "simple background" in instruction
        has_transparent = "transparent background" in instruction
        assert has_simple or has_transparent, (
            f"Expected 'simple background' or 'transparent background' in system instruction, got: {config.system_instruction}"
        )

    def test_system_instruction_contains_clear_outlines(self, adapter):
        """System instruction must mention clear outlines."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        assert "clear outlines" in instruction, f"Expected 'clear outlines' in system instruction, got: {config.system_instruction}"

    def test_system_instruction_contains_view_angle(self, adapter):
        """System instruction must mention front view or 3/4 view."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        has_front = "front view" in instruction
        has_three_quarter = "3/4 view" in instruction
        assert has_front or has_three_quarter, (
            f"Expected 'front view' or '3/4 view' in system instruction, got: {config.system_instruction}"
        )

    def test_system_instruction_includes_positive_prompt_pixel_art_directives(self, adapter):
        """System instruction must instruct the model to include pixel-art-friendly directives in positive_prompt."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        # The instruction should tell the model to embed pixel-art directives in positive_prompt
        assert "pixel" in instruction or "pixel art" in instruction or "pixel-art" in instruction, (
            f"Expected pixel-art reference in system instruction, got: {config.system_instruction}"
        )

    def test_system_instruction_includes_negative_prompt_guidance(self, adapter):
        """System instruction should guide the model to include anti-patterns in negative_prompt."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        assert "negative" in instruction, (
            f"Expected 'negative' prompt guidance in system instruction, got: {config.system_instruction}"
        )
