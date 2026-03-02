"""Tests for dynamic prompt injection with pixel-art prefix (FR-2)."""
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.modules.pixelization.comfyui_adapter import ComfyUIAdapter
from src.modules.pixelization.comfyui_client import ComfyUIClient
from src.core.config import ConfigManager


SAMPLE_WORKFLOW = {
    "1": {
        "class_type": "LoadImage",
        "inputs": {"image": "placeholder.png"}
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {"text": "{prompt}", "clip": ["11", 1]}
    },
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 0, "steps": 20, "cfg": 7.0,
            "sampler_name": "euler", "scheduler": "normal",
            "denoise": 0.32,
            "positive": ["10", 0], "negative": ["5", 0],
            "model": ["11", 0], "latent_image": ["6", 0]
        }
    },
    "5": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "blurry, smooth, anti-aliased, photorealistic, 3d render, noise, artifacts, deformed, bad anatomy, extra limbs, mutation",
            "clip": ["11", 1]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {"filename_prefix": "pixelized", "images": ["7", 0]}
    },
    "10": {
        "class_type": "ControlNetApply",
        "inputs": {
            "conditioning": ["2", 0], "control_net": ["8", 0],
            "image": ["1", 0], "strength": 0.65
        }
    }
}

PIXEL_ART_PREFIX = "pixel art, clean edges, limited palette, "


@pytest.fixture
def mock_config():
    config = MagicMock(spec=ConfigManager)
    config.get_comfyui_url.return_value = "http://127.0.0.1:8000"
    config.get_comfyui_workflow_template.return_value = "workflow_api_template.json"
    return config


@pytest.fixture
def mock_client():
    return MagicMock(spec=ComfyUIClient)


@pytest.fixture
def adapter(mock_config, mock_client):
    template_json = json.dumps(SAMPLE_WORKFLOW)
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=template_json)):
        return ComfyUIAdapter(
            config_manager=mock_config,
            client=mock_client,
            output_dir="test_output"
        )


class TestDynamicPromptInjection:
    """Verify that _build_workflow injects prompts with pixel-art prefix."""

    def test_prompt_with_prefix_injected(self, adapter):
        """When a prompt is provided, it must be prefixed with pixel-art terms."""
        workflow = adapter._build_workflow("test.png", prompt="retro game character")
        text = workflow["2"]["inputs"]["text"]
        assert text == PIXEL_ART_PREFIX + "retro game character"

    def test_no_prompt_keeps_template_default(self, adapter):
        """When prompt is None, template text remains unchanged."""
        workflow = adapter._build_workflow("test.png", prompt=None)
        text = workflow["2"]["inputs"]["text"]
        assert text == "{prompt}"

    def test_empty_prompt_still_prefixed(self, adapter):
        """Even an empty prompt string should get the prefix prepended."""
        workflow = adapter._build_workflow("test.png", prompt="")
        text = workflow["2"]["inputs"]["text"]
        assert text == PIXEL_ART_PREFIX
