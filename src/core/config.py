from typing import Any, Dict, Optional
import os
import json
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, runtime_config: Optional[Dict[str, Any]] = None, config_path: str = "config.json"):
        self.runtime_config = runtime_config or {}
        self.config_path = config_path
        self._file_config = {}
        
        # Load environment variables from .env file
        load_dotenv()
        
        self._load_config()

    def _load_config(self):
        """Load configuration from the file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._file_config = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file exists but is invalid or unreadable, we might want to log it
                # For now, we'll treat it as empty config
                self._file_config = {}
        else:
            self._file_config = {}

    def _get_value(self, key: str, env_key: str) -> Optional[str]:
        """
        Retrieve value with priority: Runtime > File > Env
        """
        # 1. Runtime
        if key in self.runtime_config:
            return str(self.runtime_config[key])
        
        # 2. File
        if key in self._file_config:
            return str(self._file_config[key])
            
        # 3. Environment Variable
        return os.environ.get(env_key)

    def get_api_key(self) -> str:
        """Retrieve API Key with priority logic."""
        api_key = self._get_value('api_key', 'API_KEY')
        if not api_key:
            raise ValueError("API Key not found in Runtime args, Config file, or Environment variables.")
        return api_key

    def get_model(self) -> str:
        """Retrieve Model name with priority logic."""
        # Default model if not specified anywhere could be handled here or by caller.
        # Requirement says "Missing key raises appropriate error" for API Key.
        # For model, let's assume similar behavior or a default if appropriate.
        # Based on test Scenario 1, it expects a value from file.
        model = self._get_value('model', 'MODEL')
        if not model:
            return "gemini-2.5-flash"
        return model
        return model
