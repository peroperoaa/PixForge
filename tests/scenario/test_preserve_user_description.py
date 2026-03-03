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


class TestPreserveUserDescription:
    """FR-1 & FR-2: SYSTEM_INSTRUCTION treats user input as scene description and preserves it as core of positive_prompt."""

    def test_system_instruction_states_user_input_is_scene_description(self, adapter):
        """SYSTEM_INSTRUCTION must explicitly say user input is a scene description."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        assert "scene description" in instruction, (
            f"Expected 'scene description' in SYSTEM_INSTRUCTION, got: {config.system_instruction}"
        )

    def test_system_instruction_states_user_input_not_a_command(self, adapter):
        """SYSTEM_INSTRUCTION must clarify that user input is NOT a command/instruction."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        assert "not a command" in instruction or "not an instruction" in instruction, (
            f"Expected 'not a command' or 'not an instruction' in SYSTEM_INSTRUCTION, got: {config.system_instruction}"
        )

    def test_system_instruction_requires_user_description_as_core_of_positive_prompt(self, adapter):
        """SYSTEM_INSTRUCTION must require user's description to be the core subject of positive_prompt."""
        prompt_input = PromptInput(text_prompt="A warrior character")
        _, config = adapter._construct_request(prompt_input)
        instruction = config.system_instruction.lower()
        # Must contain language about preserving/incorporating the user description as core/subject
        has_core = "core" in instruction and "positive_prompt" in instruction
        has_subject = "subject" in instruction and "positive_prompt" in instruction
        assert has_core or has_subject, (
            f"Expected directive about user description being core/subject of positive_prompt, got: {config.system_instruction}"
        )

    def test_construct_request_passes_text_prompt_unchanged(self, adapter):
        """_construct_request must pass user text_prompt in contents without modification."""
        original_prompt = "请给出一组像素风的素材"
        prompt_input = PromptInput(text_prompt=original_prompt)
        contents, _ = adapter._construct_request(prompt_input)
        assert contents[0] == original_prompt, (
            f"Expected text_prompt '{original_prompt}' to be passed unchanged, got: {contents[0]}"
        )
