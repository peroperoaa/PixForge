import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from src.modules.pixelization.comfyui_client import ComfyUIClient
from src.modules.pixelization.exceptions import (
    ComfyUIConnectionError,
    ComfyUITimeoutError,
    ComfyUIWorkflowError,
)
import requests


class TestComfyUIClientInit:
    def test_default_init(self):
        client = ComfyUIClient()
        assert client.base_url == "http://127.0.0.1:8000"
        assert client.timeout == 300
        assert client.client_id  # UUID

    def test_custom_init(self):
        client = ComfyUIClient(base_url="http://192.168.1.100:9000/", timeout=60)
        assert client.base_url == "http://192.168.1.100:9000"  # trailing slash stripped
        assert client.timeout == 60


class TestUploadImage:
    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_upload_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "test.png", "subfolder": "", "type": "input"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = ComfyUIClient()
        with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
            result = client.upload_image("test.png")

        assert result["name"] == "test.png"
        mock_post.assert_called_once()

    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_upload_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        client = ComfyUIClient()
        with patch("builtins.open", mock_open(read_data=b"fake")):
            with pytest.raises(ComfyUIConnectionError, match="Failed to connect"):
                client.upload_image("test.png")

    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_upload_timeout(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Timed out")

        client = ComfyUIClient()
        with patch("builtins.open", mock_open(read_data=b"fake")):
            with pytest.raises(ComfyUITimeoutError, match="Upload timed out"):
                client.upload_image("test.png")


class TestQueuePrompt:
    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_queue_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"prompt_id": "abc-123"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = ComfyUIClient()
        prompt_id = client.queue_prompt({"1": {"class_type": "KSampler"}})
        assert prompt_id == "abc-123"

    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_queue_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("refused")

        client = ComfyUIClient()
        with pytest.raises(ComfyUIConnectionError):
            client.queue_prompt({})

    @patch("src.modules.pixelization.comfyui_client.requests.post")
    def test_queue_missing_prompt_id(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "bad workflow"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        client = ComfyUIClient()
        with pytest.raises(ComfyUIWorkflowError, match="missing prompt_id"):
            client.queue_prompt({})


class TestGetHistory:
    @patch("src.modules.pixelization.comfyui_client.requests.get")
    def test_get_history_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"abc-123": {"outputs": {}}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = ComfyUIClient()
        history = client.get_history("abc-123")
        assert "abc-123" in history

    @patch("src.modules.pixelization.comfyui_client.requests.get")
    def test_get_history_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("refused")

        client = ComfyUIClient()
        with pytest.raises(ComfyUIConnectionError):
            client.get_history("abc-123")


class TestGetImage:
    @patch("src.modules.pixelization.comfyui_client.requests.get")
    def test_get_image_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"PNG_IMAGE_BYTES"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        client = ComfyUIClient()
        data = client.get_image("result.png")
        assert data == b"PNG_IMAGE_BYTES"

    @patch("src.modules.pixelization.comfyui_client.requests.get")
    def test_get_image_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("refused")

        client = ComfyUIClient()
        with pytest.raises(ComfyUIConnectionError):
            client.get_image("result.png")


class TestWaitForCompletion:
    @patch("src.modules.pixelization.comfyui_client.ComfyUIClient.get_history")
    @patch("src.modules.pixelization.comfyui_client.websocket.create_connection")
    def test_wait_success(self, mock_ws_create, mock_get_history):
        mock_ws = MagicMock()
        # Simulate receiving messages: first a progress msg, then completion
        mock_ws.recv.side_effect = [
            json.dumps({"type": "progress", "data": {"value": 50, "max": 100}}),
            json.dumps({"type": "executing", "data": {"prompt_id": "abc-123", "node": "5"}}),
            json.dumps({"type": "executing", "data": {"prompt_id": "abc-123", "node": None}}),
        ]
        mock_ws_create.return_value = mock_ws

        mock_get_history.return_value = {"abc-123": {"outputs": {"9": {"images": [{"filename": "out.png"}]}}}}

        client = ComfyUIClient()
        result = client.wait_for_completion("abc-123")
        assert "outputs" in result
        mock_ws.close.assert_called_once()

    @patch("src.modules.pixelization.comfyui_client.websocket.create_connection")
    def test_wait_timeout(self, mock_ws_create):
        import websocket as ws_lib
        mock_ws = MagicMock()
        mock_ws.recv.side_effect = ws_lib.WebSocketTimeoutException("timeout")
        mock_ws_create.return_value = mock_ws

        client = ComfyUIClient(timeout=5)
        with pytest.raises(ComfyUITimeoutError, match="timed out"):
            client.wait_for_completion("abc-123")
        mock_ws.close.assert_called_once()

    @patch("src.modules.pixelization.comfyui_client.websocket.create_connection")
    def test_wait_connection_refused(self, mock_ws_create):
        mock_ws_create.side_effect = ConnectionRefusedError("refused")

        client = ComfyUIClient()
        with pytest.raises(ComfyUIConnectionError, match="connection refused"):
            client.wait_for_completion("abc-123")

    @patch("src.modules.pixelization.comfyui_client.ComfyUIClient.get_history")
    @patch("src.modules.pixelization.comfyui_client.websocket.create_connection")
    def test_wait_execution_error(self, mock_ws_create, mock_get_history):
        mock_ws = MagicMock()
        mock_ws.recv.return_value = json.dumps({
            "type": "execution_error",
            "data": {"prompt_id": "abc-123", "error": "Node failed"}
        })
        mock_ws_create.return_value = mock_ws

        client = ComfyUIClient()
        with pytest.raises(ComfyUIWorkflowError, match="Execution error"):
            client.wait_for_completion("abc-123")
        mock_ws.close.assert_called_once()

    @patch("src.modules.pixelization.comfyui_client.websocket.create_connection")
    def test_wait_skips_binary_frames(self, mock_ws_create):
        """Binary frames (preview images) should be silently skipped."""
        mock_ws = MagicMock()
        mock_ws.recv.side_effect = [
            b"\x89PNG\r\n",  # binary preview frame
            json.dumps({"type": "executing", "data": {"prompt_id": "abc-123", "node": None}}),
        ]
        mock_ws_create.return_value = mock_ws

        with patch.object(ComfyUIClient, "get_history", return_value={"abc-123": {"outputs": {}}}):
            client = ComfyUIClient()
            result = client.wait_for_completion("abc-123")
            assert result == {"outputs": {}}
