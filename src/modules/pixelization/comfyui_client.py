import json
import uuid
import requests
import websocket
from typing import Any, Dict, Optional
from src.modules.pixelization.exceptions import (
    ComfyUIConnectionError,
    ComfyUITimeoutError,
    ComfyUIWorkflowError,
)


class ComfyUIClient:
    """Low-level HTTP/WebSocket client for communicating with ComfyUI API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout  # seconds
        self.client_id = str(uuid.uuid4())

    def upload_image(self, image_path: str, subfolder: str = "", overwrite: bool = True) -> Dict[str, Any]:
        """Upload an image to ComfyUI via POST /upload/image.
        Returns the JSON response from ComfyUI (contains name, subfolder, type).
        """
        url = f"{self.base_url}/upload/image"
        try:
            with open(image_path, "rb") as f:
                files = {"image": (image_path.split("/")[-1].split("\\")[-1], f, "image/png")}
                data = {"subfolder": subfolder, "overwrite": str(overwrite).lower()}
                response = requests.post(url, files=files, data=data, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.ConnectionError as e:
            raise ComfyUIConnectionError(f"Failed to connect to ComfyUI at {self.base_url}: {e}") from e
        except requests.exceptions.Timeout as e:
            raise ComfyUITimeoutError(f"Upload timed out after {self.timeout}s: {e}") from e
        except Exception as e:
            raise ComfyUIWorkflowError(f"Image upload failed: {e}") from e

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        """Submit a workflow to ComfyUI via POST /prompt.
        Returns the prompt_id.
        """
        url = f"{self.base_url}/prompt"
        payload = {"prompt": workflow, "client_id": self.client_id}
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result["prompt_id"]
        except requests.exceptions.ConnectionError as e:
            raise ComfyUIConnectionError(f"Failed to connect to ComfyUI at {self.base_url}: {e}") from e
        except requests.exceptions.Timeout as e:
            raise ComfyUITimeoutError(f"Queue prompt timed out after {self.timeout}s: {e}") from e
        except KeyError as e:
            raise ComfyUIWorkflowError(f"Unexpected response format (missing prompt_id): {e}") from e
        except Exception as e:
            raise ComfyUIWorkflowError(f"Queue prompt failed: {e}") from e

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """Retrieve execution history for a given prompt_id via GET /history/{prompt_id}."""
        url = f"{self.base_url}/history/{prompt_id}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            raise ComfyUIConnectionError(f"Failed to connect to ComfyUI at {self.base_url}: {e}") from e
        except Exception as e:
            raise ComfyUIWorkflowError(f"Get history failed: {e}") from e

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
        """Download a generated image via GET /view.
        Returns raw image bytes.
        """
        url = f"{self.base_url}/view"
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.content
        except requests.exceptions.ConnectionError as e:
            raise ComfyUIConnectionError(f"Failed to connect to ComfyUI at {self.base_url}: {e}") from e
        except Exception as e:
            raise ComfyUIWorkflowError(f"Get image failed: {e}") from e

    def wait_for_completion(self, prompt_id: str) -> Dict[str, Any]:
        """Connect via WebSocket and block until the given prompt_id finishes execution.
        Returns the output data from the execution.
        Raises ComfyUITimeoutError if execution exceeds self.timeout.
        """
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/ws?clientId={self.client_id}"

        try:
            ws = websocket.create_connection(ws_url, timeout=self.timeout)
        except ConnectionRefusedError as e:
            raise ComfyUIConnectionError(f"WebSocket connection refused at {ws_url}: {e}") from e
        except Exception as e:
            raise ComfyUIConnectionError(f"WebSocket connection failed: {e}") from e

        try:
            while True:
                try:
                    raw = ws.recv()
                except websocket.WebSocketTimeoutException as e:
                    raise ComfyUITimeoutError(
                        f"WebSocket timed out waiting for prompt {prompt_id} after {self.timeout}s"
                    ) from e

                if isinstance(raw, bytes):
                    continue  # skip binary preview frames

                message = json.loads(raw)
                msg_type = message.get("type")
                msg_data = message.get("data", {})

                if msg_type == "executing":
                    if msg_data.get("prompt_id") == prompt_id and msg_data.get("node") is None:
                        # Execution complete
                        break

                if msg_type == "execution_error":
                    if msg_data.get("prompt_id") == prompt_id:
                        raise ComfyUIWorkflowError(
                            f"Execution error for prompt {prompt_id}: {msg_data}"
                        )
        finally:
            ws.close()

        # Fetch results from history
        history = self.get_history(prompt_id)
        if prompt_id not in history:
            raise ComfyUIWorkflowError(f"Prompt {prompt_id} not found in history")
        return history[prompt_id]
