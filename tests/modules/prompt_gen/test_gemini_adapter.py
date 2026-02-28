import pytest
from unittest.mock import MagicMock
from google.genai import types
from src.core.config import ConfigManager
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput
from src.modules.prompt_gen.gemini_adapter import GeminiAdapter

def test_initialization():
    config = ConfigManager(runtime_config={"api_key": "test_key", "model": "gemini-2.5-flash"})
    adapter = GeminiAdapter(config)
    
    assert adapter.model_name == "gemini-2.5-flash"
    assert adapter.client is not None
    assert adapter.api_key == "test_key"

def test_construct_request():
    config = ConfigManager(runtime_config={"api_key": "test_key", "model": "gemini-2.5-flash"})
    adapter = GeminiAdapter(config)
    
    prompt_input = PromptInput(text_prompt="A majestic lion")
    
    contents, generation_config = adapter._construct_request(prompt_input)
    
    # Assert contents format
    assert isinstance(contents, list)
    assert contents[0] == "A majestic lion"
    
    # Assert config
    assert isinstance(generation_config, types.GenerateContentConfig)
    assert generation_config.response_mime_type == "application/json"
    assert generation_config.response_schema == PromptOutput
    assert generation_config.system_instruction is not None
    assert "You are an expert prompt engineer" in generation_config.system_instruction
