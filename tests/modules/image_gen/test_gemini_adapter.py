import pytest
from unittest.mock import Mock, patch, MagicMock
from google.genai.errors import APIError
import os

from src.core.config import ConfigManager
from src.modules.image_gen.gemini_adapter import GeminiImageAdapter
from src.modules.image_gen.schemas import ImageGenInput, ImageGenOutput
from src.modules.image_gen.exceptions import ImageGenerationError

@pytest.fixture
def mock_config_manager():
    config = Mock(spec=ConfigManager)
    config.get_api_key.return_value = "test_api_key"
    config.get_image_model.return_value = "gemini-3-pro-image-preview"
    return config

def test_adapter_initialization(mock_config_manager):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client:
        adapter = GeminiImageAdapter(mock_config_manager)
        assert adapter.api_key == "test_api_key"
        assert adapter.model_name == "gemini-3-pro-image-preview"
        mock_client.assert_called_once_with(api_key="test_api_key")

def test_generate_success(mock_config_manager, tmp_path):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client_class, \
         patch('src.modules.image_gen.gemini_adapter.Image.open') as mock_image_open, \
         patch('src.modules.image_gen.gemini_adapter.uuid.uuid4') as mock_uuid:
        
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance
        
        # Mock the generation response
        mock_part = MagicMock()
        mock_part.inline_data = True
        
        # Mock the SDK Image object returned by as_image()
        mock_sdk_image = MagicMock()
        mock_sdk_image.image_bytes = b"fake_image_bytes"
        mock_part.as_image.return_value = mock_sdk_image 
        
        mock_response = MagicMock()
        mock_response.parts = [mock_part]
        mock_client_instance.models.generate_content.return_value = mock_response
        
        # Mock UUID
        mock_uuid.return_value = "1234-5678"
        
        adapter = GeminiImageAdapter(mock_config_manager)
        test_output_dir = str(tmp_path / "images")
        adapter.output_dir = test_output_dir
        
        input_data = ImageGenInput(prompt="An epic fantasy hero")
        output = adapter.generate(input_data)
        
        call_kwargs = mock_client_instance.models.generate_content.call_args.kwargs
        assert call_kwargs['model'] == "gemini-3-pro-image-preview"
        assert call_kwargs['contents'] == ["An epic fantasy hero"]
        
        assert isinstance(output, ImageGenOutput)
        assert output.image_path.endswith("1234-5678.png")

def test_generate_api_error(mock_config_manager):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client_class:
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.side_effect = Exception("Test API error")
        mock_client_class.return_value = mock_client_instance
        
        adapter = GeminiImageAdapter(mock_config_manager)
        input_data = ImageGenInput(prompt="An epic fantasy hero")
        
        with pytest.raises(ImageGenerationError, match="Unexpected error during image generation"):
            adapter.generate(input_data)

def test_generate_save_success(mock_config_manager, tmp_path):
    with patch('src.modules.image_gen.gemini_adapter.genai.Client') as mock_client_class, \
         patch('src.modules.image_gen.gemini_adapter.Image.open') as mock_image_open, \
         patch('src.modules.image_gen.gemini_adapter.uuid.uuid4') as mock_uuid, \
         patch('src.modules.image_gen.gemini_adapter.os.makedirs') as mock_makedirs:
        
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance
        
        # Mock the generation response
        mock_pil_image = MagicMock()
        
        mock_part = MagicMock()
        mock_part.inline_data = True
        
        # Mock SDK Image
        mock_sdk_image = MagicMock()
        mock_sdk_image.image_bytes = b"fake_image_bytes"
        mock_part.as_image.return_value = mock_sdk_image
        
        mock_response = MagicMock()
        mock_response.parts = [mock_part]
        
        mock_client_instance.models.generate_content.return_value = mock_response
        
        # When Image.open is called with the bytes, return our mock_pil_image
        mock_image_open.return_value = mock_pil_image
        
        # Mock UUID for predictable filename
        mock_uuid.return_value = "1234-5678"
        
        adapter = GeminiImageAdapter(mock_config_manager)
        # Override output_dir for testing
        test_output_dir = str(tmp_path / "images")
        adapter.output_dir = test_output_dir
        
        input_data = ImageGenInput(prompt="A test image")
        output = adapter.generate(input_data)
        
        # Verify it tries to save the file
        expected_path = os.path.join(test_output_dir, "1234-5678.png")
        
        mock_pil_image.save.assert_called_once()
        saved_path = mock_pil_image.save.call_args[0][0]
        assert saved_path == expected_path
        
        # also check that makedirs was called with the right directory
        mock_makedirs.assert_called_once_with(test_output_dir, exist_ok=True)
        
        assert isinstance(output, ImageGenOutput)
        assert output.image_path == expected_path
