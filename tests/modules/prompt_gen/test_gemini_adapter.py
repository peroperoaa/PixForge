import pytest
from unittest.mock import MagicMock
from google.genai import types
from src.core.config import ConfigManager
from src.modules.prompt_gen.schemas import PromptInput, PromptOutput
from src.modules.prompt_gen.gemini_adapter import GeminiAdapter
from src.modules.prompt_gen.exceptions import APIConnectionError, PromptParsingError
from google.genai.errors import APIError

@pytest.fixture
def mock_genai_client(mocker):
    # Mock the genai.Client class used in gemini_adapter
    mock_client_class = mocker.patch("src.modules.prompt_gen.gemini_adapter.genai.Client")
    return mock_client_class.return_value

def test_initialization(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    adapter = GeminiAdapter(config)

    assert adapter.model_name == "gemini-3.1-pro-preview"
    assert adapter.client is mock_genai_client
    assert adapter.api_key == "test_key"

def test_construct_request(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
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

def test_generate_success_with_parsed(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    adapter = GeminiAdapter(config)

    # Mock the client
    mock_response = MagicMock()
    expected_output = PromptOutput(
        positive_prompt="A majestic lion standing proudly",
        negative_prompt="blurry, bad anatomy",
        style_parameters={"style": "realistic"}
    )
    mock_response.parsed = expected_output

    mock_genai_client.models.generate_content.return_value = mock_response

    prompt_input = PromptInput(text_prompt="A majestic lion")
    output = adapter.generate(prompt_input)

    assert output == expected_output
    mock_genai_client.models.generate_content.assert_called_once()

def test_generate_success_fallback(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    adapter = GeminiAdapter(config)

    # Mock the client where parsed is not PromptOutput but text is valid JSON
    mock_response = MagicMock()
    mock_response.parsed = None
    mock_response.text = '{"positive_prompt": "A majestic lion standing proudly", "negative_prompt": "blurry, bad anatomy", "style_parameters": {"style": "realistic"}}'

    mock_genai_client.models.generate_content.return_value = mock_response

    prompt_input = PromptInput(text_prompt="A majestic lion")
    output = adapter.generate(prompt_input)

    assert output.positive_prompt == "A majestic lion standing proudly"
    assert output.negative_prompt == "blurry, bad anatomy"

def test_generate_api_error(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    adapter = GeminiAdapter(config)

    # Mock the client to raise an API error
    mock_genai_client.models.generate_content.side_effect = Exception("Mocked API Error")

    prompt_input = PromptInput(text_prompt="A majestic lion")

    with pytest.raises(APIConnectionError) as exc_info:
        adapter.generate(prompt_input)
    assert "Mocked API Error" in str(exc_info.value)

def test_generate_invalid_json(mock_genai_client):
    config = ConfigManager(runtime_config={"api_key": "test_key", "gemini_model": "gemini-3.1-pro-preview"})
    adapter = GeminiAdapter(config)

    mock_response = MagicMock()
    mock_response.parsed = None
    mock_response.text = '{"invalid_json": "A majestic lion standing proudly"'  # Missing closing brace

    mock_genai_client.models.generate_content.return_value = mock_response

    prompt_input = PromptInput(text_prompt="A majestic lion")

