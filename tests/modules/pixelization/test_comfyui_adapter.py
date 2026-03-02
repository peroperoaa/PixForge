import json
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.modules.pixelization.comfyui_adapter import ComfyUIAdapter
from src.modules.pixelization.comfyui_client import ComfyUIClient
from src.modules.pixelization.schemas import PixelizationInput, PixelizationOutput
from src.modules.pixelization.exceptions import (
    ComfyUIConnectionError,
    ComfyUIWorkflowError,
    PixelizationError,
)
from src.core.config import ConfigManager


SAMPLE_WORKFLOW_TEMPLATE = {
    "1": {
        "class_type": "LoadImage",
        "inputs": {
            "image": "placeholder.png"
        }
    },
    "2": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "pixel art style",
            "clip": ["4", 0]
        }
    },
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 0,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 0.55,
            "positive": ["2", 0],
            "negative": ["5", 0],
            "model": ["4", 0],
            "latent_image": ["6", 0]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "pixelized",
            "images": ["7", 0]
        }
    }
}


@pytest.fixture
def mock_config():
    """Create a mock ConfigManager."""
    config = MagicMock(spec=ConfigManager)
    config.get_comfyui_url.return_value = "http://127.0.0.1:8188"
    config.get_comfyui_workflow_template.return_value = "workflow_api_template.json"
    return config


@pytest.fixture
def mock_client():
    """Create a mock ComfyUIClient."""
    return MagicMock(spec=ComfyUIClient)


@pytest.fixture
def adapter(mock_config, mock_client):
    """Create adapter with mocked template loading."""
    template_json = json.dumps(SAMPLE_WORKFLOW_TEMPLATE)
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=template_json)):
        return ComfyUIAdapter(
            config_manager=mock_config,
            client=mock_client,
            output_dir="test_output"
        )


class TestAdapterInit:
    def test_init_with_custom_client(self, mock_config, mock_client):
        template_json = json.dumps(SAMPLE_WORKFLOW_TEMPLATE)
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_json)):
            adapter = ComfyUIAdapter(mock_config, client=mock_client)
        assert adapter.client is mock_client

    def test_init_creates_default_client(self, mock_config):
        template_json = json.dumps(SAMPLE_WORKFLOW_TEMPLATE)
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=template_json)):
            adapter = ComfyUIAdapter(mock_config)
        assert isinstance(adapter.client, ComfyUIClient)

    def test_init_missing_template(self, mock_config, mock_client):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(ComfyUIWorkflowError, match="Workflow template not found"):
                ComfyUIAdapter(mock_config, client=mock_client)

    def test_init_invalid_json_template(self, mock_config, mock_client):
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="NOT JSON {{")):
            with pytest.raises(ComfyUIWorkflowError, match="Invalid JSON"):
                ComfyUIAdapter(mock_config, client=mock_client)


class TestBuildWorkflow:
    def test_injects_image_name(self, adapter):
        workflow = adapter._build_workflow("uploaded_test.png")
        assert workflow["1"]["inputs"]["image"] == "uploaded_test.png"

    def test_injects_denoising_strength(self, adapter):
        workflow = adapter._build_workflow("test.png", denoising_strength=0.45)
        assert workflow["3"]["inputs"]["denoise"] == 0.45

    def test_injects_seed(self, adapter):
        workflow = adapter._build_workflow("test.png", seed=42)
        assert workflow["3"]["inputs"]["seed"] == 42

    def test_random_seed_when_none(self, adapter):
        workflow = adapter._build_workflow("test.png")
        seed = workflow["3"]["inputs"]["seed"]
        assert isinstance(seed, int)
        assert 0 <= seed < 2**32

    def test_injects_prompt_into_text_node(self, adapter):
        workflow = adapter._build_workflow("test.png", prompt="retro 16-bit pixel art")
        assert workflow["2"]["inputs"]["text"] == "retro 16-bit pixel art"

    def test_does_not_mutate_template(self, adapter):
        original_image = adapter._workflow_template["1"]["inputs"]["image"]
        adapter._build_workflow("changed.png")
        assert adapter._workflow_template["1"]["inputs"]["image"] == original_image


class TestExtractOutputImages:
    def test_extracts_single_image(self, adapter):
        history_result = {
            "outputs": {
                "9": {
                    "images": [{"filename": "pixelized_00001.png", "subfolder": "", "type": "output"}]
                }
            }
        }
        images = adapter._extract_output_images(history_result)
        assert len(images) == 1
        assert images[0]["filename"] == "pixelized_00001.png"

    def test_extracts_multiple_images(self, adapter):
        history_result = {
            "outputs": {
                "9": {"images": [
                    {"filename": "img1.png", "subfolder": "", "type": "output"},
                    {"filename": "img2.png", "subfolder": "", "type": "output"},
                ]},
                "10": {"images": [
                    {"filename": "img3.png", "subfolder": "sub", "type": "output"},
                ]}
            }
        }
        images = adapter._extract_output_images(history_result)
        assert len(images) == 3

    def test_returns_empty_for_no_images(self, adapter):
        history_result = {"outputs": {"9": {"text": "some text output"}}}
        images = adapter._extract_output_images(history_result)
        assert len(images) == 0


class TestGenerate:
    def test_full_lifecycle_success(self, adapter, mock_client):
        """Test the complete upload -> queue -> wait -> download flow."""
        # Setup mocks
        mock_client.upload_image.return_value = {"name": "uploaded.png", "subfolder": "", "type": "input"}
        mock_client.queue_prompt.return_value = "prompt-abc-123"
        mock_client.wait_for_completion.return_value = {
            "outputs": {
                "9": {"images": [{"filename": "pixelized_00001.png", "subfolder": "", "type": "output"}]}
            }
        }
        mock_client.get_image.return_value = b"PNG_FAKE_BYTES"

        input_data = PixelizationInput(image_path="input/test.png", prompt="pixel art", denoising_strength=0.5)

        with patch("os.makedirs"), \
             patch("builtins.open", mock_open()):
            result = adapter.generate(input_data)

        assert isinstance(result, PixelizationOutput)
        assert "pixelized_00001.png" in result.image_path
        mock_client.upload_image.assert_called_once_with("input/test.png")
        mock_client.queue_prompt.assert_called_once()
        mock_client.wait_for_completion.assert_called_once_with("prompt-abc-123")
        mock_client.get_image.assert_called_once()

    def test_raises_on_no_output_images(self, adapter, mock_client):
        mock_client.upload_image.return_value = {"name": "up.png", "subfolder": "", "type": "input"}
        mock_client.queue_prompt.return_value = "prompt-id"
        mock_client.wait_for_completion.return_value = {"outputs": {}}

        input_data = PixelizationInput(image_path="input.png")
        with pytest.raises(ComfyUIWorkflowError, match="No output images"):
            adapter.generate(input_data)

    def test_propagates_connection_error(self, adapter, mock_client):
        mock_client.upload_image.side_effect = ComfyUIConnectionError("Connection refused")

        input_data = PixelizationInput(image_path="input.png")
        with pytest.raises(ComfyUIConnectionError):
            adapter.generate(input_data)

    def test_wraps_unexpected_error(self, adapter, mock_client):
        mock_client.upload_image.side_effect = RuntimeError("unexpected")

        input_data = PixelizationInput(image_path="input.png")
        with pytest.raises(PixelizationError, match="Pixelization failed"):
            adapter.generate(input_data)
