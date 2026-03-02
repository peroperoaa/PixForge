import os
import sys
import glob

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config import ConfigManager
from src.modules.pixelization.comfyui_adapter import ComfyUIAdapter
from src.modules.pixelization.schemas import PixelizationInput
from src.modules.pixelization.exceptions import (
    ComfyUIConnectionError,
    ComfyUITimeoutError,
    ComfyUIWorkflowError,
    PixelizationError,
)


def find_input_image() -> str:
    """Find an existing image in the output/images directory to use as input."""
    patterns = ["output/images/*.png", "output/images/*.jpg", "output/*.png"]
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            return files[0]
    return ""


def main():
    print("=" * 60)
    print("  Module 3: ComfyUI Pixelization Engine - Demo")
    print("=" * 60)

    # Step 1: Initialize ConfigManager
    print("\n[1/5] Initializing ConfigManager...")
    config = ConfigManager()

    comfyui_url = config.get_comfyui_url()
    template_path = config.get_comfyui_workflow_template()
    print(f"  ComfyUI URL: {comfyui_url}")
    print(f"  Workflow Template: {template_path}")

    # Step 2: Find input image
    print("\n[2/5] Locating input image...")
    image_path = find_input_image()
    if not image_path:
        print("  ERROR: No input image found in output/images/")
        print("  Please run demo_module2.py first to generate a source image,")
        print("  or place a PNG/JPG file in output/images/")
        return

    print(f"  Input image: {image_path}")
    file_size = os.path.getsize(image_path) / 1024
    print(f"  File size: {file_size:.1f} KB")

    # Step 3: Instantiate ComfyUIAdapter
    print("\n[3/5] Instantiating ComfyUIAdapter...")
    try:
        adapter = ComfyUIAdapter(config_manager=config)
        print("  Adapter initialized successfully")
    except ComfyUIWorkflowError as e:
        print(f"  ERROR: Workflow template issue - {e}")
        return
    except Exception as e:
        print(f"  ERROR: Failed to initialize adapter - {e}")
        return

    # Step 4: Run pixelization
    print("\n[4/5] Running pixelization pipeline...")
    print("  - Uploading image to ComfyUI...")
    print("  - Building workflow with ControlNet + Pixel Art checkpoint...")
    print("  - Queuing prompt and waiting for execution...")
    print("  (This may take 30-120 seconds depending on GPU)")
    print()

    input_data = PixelizationInput(
        image_path=image_path,
        prompt="pixel art, 16-bit style, clean pixel edges, retro game asset",
        denoising_strength=0.55,
    )

    try:
        output = adapter.generate(input_data)
    except ComfyUIConnectionError as e:
        print(f"  CONNECTION ERROR: ComfyUI is not running or unreachable!")
        print(f"  Details: {e}")
        print(f"\n  Please ensure ComfyUI is running at: {comfyui_url}")
        print("  Start it with: python main.py --listen")
        return
    except ComfyUITimeoutError as e:
        print(f"  TIMEOUT ERROR: Execution took too long!")
        print(f"  Details: {e}")
        return
    except ComfyUIWorkflowError as e:
        print(f"  WORKFLOW ERROR: ComfyUI encountered an error during execution!")
        print(f"  Details: {e}")
        print("  Check that the required models/checkpoints are installed in ComfyUI.")
        return
    except PixelizationError as e:
        print(f"  ERROR: Pixelization failed - {e}")
        return

    # Step 5: Verify output
    print("\n[5/5] Verifying output...")
    print(f"  Output path: {output.image_path}")

    if os.path.exists(output.image_path):
        output_size = os.path.getsize(output.image_path) / 1024
        print(f"  File size: {output_size:.1f} KB")
        print("\n" + "=" * 60)
        print("  SUCCESS: Pixelized image generated and saved!")
        print("=" * 60)
    else:
        print("  WARNING: Output file was not found on disk!")


if __name__ == "__main__":
    main()
