import pytest
from unittest.mock import patch, mock_open
import os
from src.core.config import ConfigManager

# Scenario 1: ConfigManager correctly prioritizes sources (Runtime > File > Env)
def test_config_priority():
    # Setup
    runtime_args = {'api_key': 'runtime_key', 'gemini_model': 'gemini-3.1-pro-preview'}
    file_content = '{"api_key": "file_key", "gemini_model": "gemini-3.1-pro-preview"}'
    env_vars = {'API_KEY': 'env_key', 'GEMINI_MODEL': 'gemini-3.1-pro-preview'}

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        
        # Priority 1: Runtime > File > Env
        assert config_manager.get_api_key() == 'runtime_key'
        
        # Priority 2: Runtime (missing) > File > Env
        assert config_manager.get_model() == 'gemini-3.1-pro-preview'

def test_config_priority_values():
    # Setup - vary values to test priority, but ensure the "winner" is valid
    
    runtime_args = {'gemini_model': 'gemini-3.1-pro-preview'}
    file_content = '{"gemini_model": "invalid-model"}'
    env_vars = {'GEMINI_MODEL': 'invalid-model'}

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_model() == 'gemini-3.1-pro-preview'

# Scenario 3: ConfigManager retrieves API key from Env if not in Runtime or File
def test_config_from_env():
    # Setup
    runtime_args = {}
    file_content = '{}'
    env_vars = {'API_KEY': 'env_key'}

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        
        assert config_manager.get_api_key() == 'env_key'

# def test_invalid_model_raises_error():
#     # Setup
#     runtime_args = {'gemini_model': 'gemini-1.5-flash'}
#     file_content = '{}'
#     env_vars = {} 

#     with patch('builtins.open', mock_open(read_data=file_content)), \
#          patch('os.path.exists', return_value=True), \
#          patch.dict(os.environ, env_vars):
        
#         config_manager = ConfigManager(runtime_config=runtime_args)
        
#         with pytest.raises(ValueError, match="Invalid model version"):
#             config_manager.get_model()

# Scenario 2: ConfigManager raises error when API key is missing
def test_missing_api_key_raises_error():
    # Setup
    runtime_args = {}
    file_content = '{}'
    env_vars = {} # Empty env

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        
        with pytest.raises(ValueError, match="API Key not found"):
            config_manager.get_api_key()

# Scenario: ConfigManager Support for Image Models
def test_image_model_runtime_priority():
    runtime_args = {'image_model': 'runtime-model'}
    file_content = '{"image_model": "file-model"}'
    env_vars = {'GEMINI_IMAGE_MODEL': 'env-model'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_image_model() == 'runtime-model'

def test_image_model_file_priority():
    runtime_args = {}
    file_content = '{"image_model": "file-model"}'
    env_vars = {'GEMINI_IMAGE_MODEL': 'env-model'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_image_model() == 'file-model'

def test_image_model_env_priority():
    runtime_args = {}
    file_content = '{}'
    env_vars = {'GEMINI_IMAGE_MODEL': 'env-model'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_image_model() == 'env-model'

def test_image_model_default():
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_image_model() == 'gemini-3-pro-image-preview'

# Scenario: ComfyUI URL configuration
def test_comfyui_url_default():
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_comfyui_url() == 'http://127.0.0.1:8000'

def test_comfyui_url_from_env():
    runtime_args = {}
    file_content = '{}'
    env_vars = {'COMFYUI_URL': 'http://192.168.1.100:8188'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_comfyui_url() == 'http://192.168.1.100:8188'

def test_comfyui_url_runtime_override():
    runtime_args = {'comfyui_url': 'http://localhost:9000'}
    file_content = '{}'
    env_vars = {'COMFYUI_URL': 'http://192.168.1.100:8188'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_comfyui_url() == 'http://localhost:9000'

# Scenario: ComfyUI workflow template configuration
def test_comfyui_workflow_template_default():
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_comfyui_workflow_template() == 'workflow_api_template.json'

def test_comfyui_workflow_template_from_env():
    runtime_args = {}
    file_content = '{}'
    env_vars = {'COMFYUI_WORKFLOW_TEMPLATE': 'custom_workflow.json'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_comfyui_workflow_template() == 'custom_workflow.json'


# ===== Post-Processing Configuration Tests =====

# Scenario: get_post_processing_output_dir
def test_post_processing_output_dir_default():
    """Returns './output/assets' when no config is set."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_post_processing_output_dir() == './output/assets'

def test_post_processing_output_dir_runtime_override():
    """Returns runtime override value when provided."""
    runtime_args = {'post_processing_output_dir': '/custom/path'}
    file_content = '{}'
    env_vars = {'POST_PROCESSING_OUTPUT_DIR': '/env/path'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_post_processing_output_dir() == '/custom/path'

def test_post_processing_output_dir_from_env():
    """Returns value from env when no runtime config."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {'POST_PROCESSING_OUTPUT_DIR': '/env/path'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_post_processing_output_dir() == '/env/path'


# Scenario: get_default_color_count
def test_default_color_count_default():
    """Returns 16 when no config is set."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_color_count() == 16

def test_default_color_count_from_env_string():
    """Returns integer from environment variable string."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {'DEFAULT_COLOR_COUNT': '32'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_color_count() == 32

def test_default_color_count_runtime_override():
    """Runtime arg overrides env variable."""
    runtime_args = {'default_color_count': 64}
    file_content = '{}'
    env_vars = {'DEFAULT_COLOR_COUNT': '32'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_color_count() == 64


# Scenario: get_default_target_sizes
def test_default_target_sizes_default():
    """Returns [32, 64] when no config is set."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_target_sizes() == [32, 64]

def test_default_target_sizes_from_env_string():
    """Parses comma-separated env string '32,64,128' into int list."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {'DEFAULT_TARGET_SIZES': '32,64,128'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_target_sizes() == [32, 64, 128]

def test_default_target_sizes_runtime_override():
    """Runtime arg overrides env variable."""
    runtime_args = {'default_target_sizes': [16, 32, 64, 128]}
    file_content = '{}'
    env_vars = {'DEFAULT_TARGET_SIZES': '32,64'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_default_target_sizes() == [16, 32, 64, 128]

# Scenario: get_rembg_model
def test_rembg_model_default():
    """Returns 'u2net' when no config is set."""
    runtime_args = {}
    file_content = '{}'
    env_vars = {}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars, clear=True):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_rembg_model() == 'u2net'

def test_rembg_model_runtime_override():
    """Runtime arg overrides env variable."""
    runtime_args = {'rembg_model': 'isnet-general-use'}
    file_content = '{}'
    env_vars = {'REMBG_MODEL': 'u2net'}
    
    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        assert config_manager.get_rembg_model() == 'isnet-general-use'
