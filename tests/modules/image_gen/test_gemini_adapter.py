import pytest
from unittest.mock import Mock, patch
from google.genai.errors import APIError

from src.core.config import ConfigManager
from src.modules.image_gen.gemini_adapter import GeminiImageAdapter
from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput
from src.modules.image_gen.exceptions import ImageGenerationError

@pytest.fixture
def mock_config_manager():
    config = Mock(spec=ConfigManager)
    config.get_api_key.return_value = "test_api_key"
    config.get_image_model.return_value = "imagen-3.0-generate-002"
    return config

def test_adapter_initialization(mock_config_manager):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client:
        adapter = GeminiImageAdapter(mock_config_manager)
        assert adapter.api_key == "test_api_key"
        assert adapter.model_name == "imagen-3.0-generate-002"
        mock_client.assert_called_once_with(api_key="test_api_key")

def test_generate_success(mock_config_manager):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client_class:
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance
        
        adapter = GeminiImageAdapter(mock_config_manager)
        input_data = ImageGenInput(prompt="An epic fantasy hero")
        
        output = adapter.generate(input_data)
        
        mock_client_instance.models.generate_images.assert_called_once()
        call_kwargs = mock_client_instance.models.generate_images.call_args.kwargs
        assert call_kwargs['model'] == "imagen-3.0-generate-002"
        assert call_kwargs['prompt'] == "An epic fantasy hero"
        assert call_kwargs['config'].aspect_ratio == "1:1"
        # The SDK might convert 'allow_adult' to 'ALLOW_ADULT' or a PersonGeneration enum
        assert "ALLOW_ADULT" in str(call_kwargs['config'].person_generation).upper()
        
        assert isinstance(output, ImageGenOutput)
        assert output.image_path == "dummy/path/to/image.png"

def test_generate_api_error(mock_config_manager):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client_class:
        mock_client_instance = Mock()
        mock_client_instance.models.generate_images.side_effect = Exception("Test API error")
        mock_client_class.return_value = mock_client_instance
        
        adapter = GeminiImageAdapter(mock_config_manager)
        input_data = ImageGenInput(prompt="An epic fantasy hero")
        
        with pytest.raises(ImageGenerationError, match="Unexpected error during image generation"):
            adapter.generate(input_data)