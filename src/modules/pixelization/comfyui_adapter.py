import copy
import json
import logging
import os
import random
from typing import Any, Dict, Optional

from src.core.config import ConfigManager
from src.modules.pixelization.comfyui_client import ComfyUIClient
from src.modules.pixelization.exceptions import (
    ComfyUIWorkflowError,
    PixelizationError,
)
from src.modules.pixelization.interface import BasePixelization
from src.modules.pixelization.schemas import PixelizationInput, PixelizationOutput

logger = logging.getLogger(__name__)


class ComfyUIAdapter(BasePixelization):
    """Adapter that orchestrates ComfyUI workflow execution for pixelization."""

    # Default node IDs in the workflow template (can be overridden)
    NODE_LOAD_IMAGE = "1"
    NODE_KSAMPLER = "3"
    NODE_SAVE_IMAGE = "9"

    def __init__(
        self,
        config_manager: ConfigManager,
        client: Optional[ComfyUIClient] = None,
        output_dir: str = "output/images",
    ):
        self.config_manager = config_manager
        self.output_dir = output_dir
        self._template_path = config_manager.get_comfyui_workflow_template()

        if client is not None:
            self.client = client
        else:
            base_url = config_manager.get_comfyui_url()
            self.client = ComfyUIClient(base_url=base_url)

        self._workflow_template = self._load_template()

    def _load_template(self) -> Dict[str, Any]:
        """Load the workflow API JSON template from disk."""
        if not os.path.exists(self._template_path):
            raise ComfyUIWorkflowError(
                f"Workflow template not found: {self._template_path}"
            )
        try:
            with open(self._template_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ComfyUIWorkflowError(
                f"Invalid JSON in workflow template {self._template_path}: {e}"
            ) from e

    def _build_workflow(
        self,
        uploaded_image_name: str,
        prompt: Optional[str] = None,
        denoising_strength: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build a workflow by injecting dynamic values into the template."""
        workflow = copy.deepcopy(self._workflow_template)

        # Inject uploaded image filename into LoadImage node
        if self.NODE_LOAD_IMAGE in workflow:
            workflow[self.NODE_LOAD_IMAGE]["inputs"]["image"] = uploaded_image_name

        # Inject KSampler parameters
        if self.NODE_KSAMPLER in workflow:
            ksampler = workflow[self.NODE_KSAMPLER]["inputs"]
            if seed is not None:
                ksampler["seed"] = seed
            else:
                ksampler["seed"] = random.randint(0, 2**32 - 1)
            if denoising_strength is not None:
                ksampler["denoise"] = denoising_strength
            if prompt is not None:
                # If there's a positive prompt text node linked, we update it
                # Look for a CLIPTextEncode node that feeds into the KSampler positive input
                positive_ref = ksampler.get("positive")
                if isinstance(positive_ref, list) and len(positive_ref) >= 1:
                    positive_node_id = str(positive_ref[0])
                    if positive_node_id in workflow:
                        workflow[positive_node_id]["inputs"]["text"] = prompt

        return workflow

    def _extract_output_images(self, history_result: Dict[str, Any]) -> list:
        """Extract output image filenames from ComfyUI history result."""
        images = []
        outputs = history_result.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for img_info in node_output["images"]:
                    images.append({
                        "filename": img_info["filename"],
                        "subfolder": img_info.get("subfolder", ""),
                        "type": img_info.get("type", "output"),
                    })
        return images

    def generate(self, input_data: PixelizationInput) -> PixelizationOutput:
        """Execute the full pixelization pipeline:
        1. Upload input image to ComfyUI
        2. Build workflow with dynamic parameters
        3. Queue the prompt
        4. Wait for completion
        5. Download result and save locally
        """
        logger.info(f"Starting pixelization for: {input_data.image_path}")

        try:
            # Step 1: Upload input image
            logger.info("Uploading image to ComfyUI...")
            upload_result = self.client.upload_image(input_data.image_path)
            uploaded_name = upload_result["name"]
            logger.info(f"Image uploaded as: {uploaded_name}")

            # Step 2: Build workflow
            workflow = self._build_workflow(
                uploaded_image_name=uploaded_name,
                prompt=input_data.prompt,
                denoising_strength=input_data.denoising_strength,
            )
            logger.info("Workflow built successfully")

            # Step 3: Queue prompt
            prompt_id = self.client.queue_prompt(workflow)
            logger.info(f"Prompt queued with ID: {prompt_id}")

            # Step 4: Wait for completion
            logger.info("Waiting for ComfyUI execution...")
            history_result = self.client.wait_for_completion(prompt_id)
            logger.info("Execution completed")

            # Step 5: Download and save output image
            output_images = self._extract_output_images(history_result)
            if not output_images:
                raise ComfyUIWorkflowError("No output images found in execution result")

            # Take the first output image
            first_image = output_images[0]
            image_bytes = self.client.get_image(
                filename=first_image["filename"],
                subfolder=first_image["subfolder"],
                folder_type=first_image["type"],
            )

            # Save to local output directory
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, first_image["filename"])
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Output saved to: {output_path}")

            return PixelizationOutput(image_path=output_path)

        except PixelizationError:
            raise
        except Exception as e:
            raise PixelizationError(f"Pixelization failed: {e}") from e
