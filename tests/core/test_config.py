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
        # Note: Since we are mocking everything to be valid, this test is slightly less effective for priority 
        # unless we vary the values. But we must enforce valid model.
        assert config_manager.get_model() == 'gemini-3.1-pro-preview'

def test_config_priority_values():
    # Setup - vary values to test priority, but ensure the "winner" is valid
    # Since we validate the result, the lower priority ones can be invalid if they are shadowed?
    # Actually ConfigManager only checks the winner.
    
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

def test_invalid_model_raises_error():
    # Setup
    runtime_args = {'gemini_model': 'gemini-1.5-flash'}
    file_content = '{}'
    env_vars = {} 

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        
        with pytest.raises(ValueError, match="Invalid model version"):
            config_manager.get_model()

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
