from typing import Any, Dict, List, Optional
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
        model = self._get_value('gemini_model', 'GEMINI_MODEL')
        if not model:
            return "gemini-2.0-flash"
        
        # if model != "gemini-3.1-pro-preview":
        #     raise ValueError("Invalid model version. Only 'gemini-3.1-pro-preview' is supported.")
            
        return model
    def get_image_model(self) -> str:
        """Retrieve Image Model name with priority logic."""
        model = self._get_value('image_model', 'GEMINI_IMAGE_MODEL')
        if not model:
            return "gemini-3.1-flash-image-preview"
        return model

    def get_comfyui_url(self) -> str:
        """Retrieve ComfyUI URL with priority logic."""
        url = self._get_value('comfyui_url', 'COMFYUI_URL')
        if not url:
            return "http://127.0.0.1:8000"
        return url

    def get_comfyui_workflow_template(self) -> str:
        """Retrieve ComfyUI workflow template path with priority logic."""
        template = self._get_value('comfyui_workflow_template', 'COMFYUI_WORKFLOW_TEMPLATE')
        if not template:
            return "workflow_api_template.json"
        return template

    def get_post_processing_output_dir(self) -> str:
        """Retrieve post-processing output directory with priority logic."""
        output_dir = self._get_value('post_processing_output_dir', 'POST_PROCESSING_OUTPUT_DIR')
        if not output_dir:
            return "./output/assets"
        return output_dir

    def get_default_color_count(self) -> int:
        """Retrieve default color count with priority logic."""
        value = self._get_value('default_color_count', 'DEFAULT_COLOR_COUNT')
        if value is None:
            return 16
        return int(value)

    def get_default_target_sizes(self) -> List[int]:
        """Retrieve default target sizes with priority logic."""
        # Check runtime config first (may be a list already)
        if 'default_target_sizes' in self.runtime_config:
            val = self.runtime_config['default_target_sizes']
            if isinstance(val, list):
                return [int(x) for x in val]
            # If it's a string, parse it
            return [int(x.strip()) for x in str(val).split(',')]

        # Check file config
        if 'default_target_sizes' in self._file_config:
            val = self._file_config['default_target_sizes']
            if isinstance(val, list):
                return [int(x) for x in val]
            return [int(x.strip()) for x in str(val).split(',')]

        # Check environment variable
        env_val = os.environ.get('DEFAULT_TARGET_SIZES')
        if env_val:
            return [int(x.strip()) for x in env_val.split(',')]

        return [32, 64]

    def get_rembg_model(self) -> str:
        """Retrieve rembg model name with priority logic."""
        model = self._get_value('rembg_model', 'REMBG_MODEL')
        if not model:
            return "u2net"
        return model