import pytest
from unittest.mock import patch, mock_open
import os
from src.core.config import ConfigManager

# Scenario 1: ConfigManager correctly prioritizes sources (Runtime > File > Env)
def test_config_priority():
    # Setup
    runtime_args = {'api_key': 'runtime_key'}
    file_content = '{"api_key": "file_key", "model": "file_model"}'
    env_vars = {'API_KEY': 'env_key', 'MODEL': 'env_model'}

    with patch('builtins.open', mock_open(read_data=file_content)), \
         patch('os.path.exists', return_value=True), \
         patch.dict(os.environ, env_vars):
        
        config_manager = ConfigManager(runtime_config=runtime_args)
        
        # Priority 1: Runtime > File > Env
        assert config_manager.get_api_key() == 'runtime_key'
        
        # Priority 2: Runtime (missing) > File > Env
        assert config_manager.get_model() == 'file_model'

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
