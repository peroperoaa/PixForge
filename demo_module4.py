"""Module 4 Demo: Post-Processing Pipeline Integration Test.

Runs the full post-processing pipeline on a pixelized image from Module 3 output.
Pipeline stages:
  1. Background removal (via rembg)
  2. Color quantization (K-Means, 16 colors)
  3. Downscaling to multiple target sizes (32x32, 64x64)
  4. Asset export to output/assets/

Usage:
  python demo_module4.py                          # Use defaults
  python demo_module4.py --image path/to/img.png  # Specify source image
  python demo_module4.py --no-remove-bg           # Skip background removal
  python demo_module4.py --colors 8               # Use 8 colors instead of 16
  python demo_module4.py --sizes 32 64 128        # Custom target sizes
"""

import argparse
import glob
import os
import sys

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.modules.post_processing.pipeline import PostProcessingPipeline
from src.modules.post_processing.schemas import PostProcessingInput, PostProcessingOutput


def find_source_image() -> str:
    """Find an existing pixelized image from Module 3 output or any image in output/images/."""
    search_patterns = [
        "output/images/*pixelized*.png",
        "output/images/*pixel*.png",
        "output/images/*.png",
        "output/images/*.jpg",
        "output/*.png",
    ]
    for pattern in search_patterns:
        files = sorted(glob.glob(pattern))
        if files:
            return files[0]
    return ""


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable units."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments with sensible defaults."""
    parser = argparse.ArgumentParser(
        description="Module 4: Post-Processing Pipeline Demo",
    )
    parser.add_argument(
        "--image",
        type=str,
        default="",
        help="Path to source image. Auto-detected from output/images/ if omitted.",
    )
    parser.add_argument(
        "--asset-name",
        type=str,
        default="demo_asset",
        help="Base name for output asset files (default: demo_asset).",
    )
    parser.add_argument(
        "--no-remove-bg",
        action="store_true",
        help="Skip background removal stage.",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=16,
        help="Number of colors for K-Means quantization (default: 16).",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[32, 64],
        help="Target output sizes in pixels (default: 32 64).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/assets",
        help="Directory for output assets (default: output/assets).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("  Module 4: Post-Processing Pipeline - Demo")
    print("=" * 60)

    # ── Step 1: Locate source image ──────────────────────────────
    print("\n[1/5] Locating source image...")
    image_path = args.image or find_source_image()

    if not image_path:
        print("  ERROR: No source image found.")
        print("  Searched in: output/images/*.png, output/images/*.jpg, output/*.png")
        print("  Please run demo_module3.py first to generate a pixelized image,")
        print("  or specify an image with: python demo_module4.py --image <path>")
        print("\n  Exiting gracefully — no images to process.")
        return

    if not os.path.isfile(image_path):
        print(f"  ERROR: Specified image not found: {image_path}")
        print("  Please check the path and try again.")
        return

    file_size = os.path.getsize(image_path)
    print(f"  Source image: {image_path}")
    print(f"  File size:    {format_file_size(file_size)}")

    # Quick image info
    from PIL import Image

    with Image.open(image_path) as img:
        print(f"  Dimensions:   {img.size[0]}x{img.size[1]} px")
        print(f"  Mode:         {img.mode}")

    # ── Step 2: Configure pipeline input ─────────────────────────
    print("\n[2/5] Configuring post-processing pipeline...")
    remove_bg = not args.no_remove_bg
    color_count = args.colors
    target_sizes = args.sizes
    output_dir = args.output_dir
    asset_name = args.asset_name

    print(f"  Remove background: {remove_bg}")
    print(f"  Color quantization: K-Means with {color_count} colors")
    print(f"  Target sizes:       {target_sizes}")
    print(f"  Output directory:   {output_dir}")
    print(f"  Asset name:         {asset_name}")

    input_data = PostProcessingInput(
        image_path=image_path,
        asset_name=asset_name,
        target_sizes=target_sizes,
        remove_background=remove_bg,
        color_count=color_count,
        output_dir=output_dir,
    )

    # ── Step 3: Initialize pipeline ──────────────────────────────
    print("\n[3/5] Initializing PostProcessingPipeline...")
    pipeline = PostProcessingPipeline()
    print("  Pipeline components:")
    print("    - BackgroundRemover (rembg, u2net)")
    print("    - ColorQuantizer (K-Means / palette)")
    print("    - Downscaler (nearest-neighbor)")
    print("  Pipeline ready.")

    # ── Step 4: Execute pipeline ─────────────────────────────────
    print("\n[4/5] Executing post-processing pipeline...")
    if remove_bg:
        print("  Stage 1: Removing background... (this may take a few seconds)")
    else:
        print("  Stage 1: Background removal SKIPPED (--no-remove-bg)")
    print(f"  Stage 2: Quantizing to {color_count} colors via K-Means...")
    print(f"  Stage 3: Downscaling to {len(target_sizes)} target size(s)...")

    try:
        output: PostProcessingOutput = pipeline.process(input_data)
    except Exception as e:
        print(f"\n  PIPELINE ERROR: {type(e).__name__}: {e}")
        print("  The pipeline encountered an error during processing.")
        print("  Check that all required dependencies are installed:")
        print("    pip install rembg pillow scikit-learn numpy")
        return

    print("  Pipeline completed successfully!")

    # ── Step 5: Verify output files ──────────────────────────────
    print("\n[5/5] Verifying output files...")
    print(f"  Output paths ({len(output.output_paths)} files):")

    all_valid = True
    for i, path in enumerate(output.output_paths):
        expected_size = output.target_sizes[i]
        exists = os.path.isfile(path)
        status = "OK" if exists else "MISSING"

        if exists:
            fsize = os.path.getsize(path)
            with Image.open(path) as out_img:
                w, h = out_img.size
                mode = out_img.mode
                dim_ok = (w == expected_size and h == expected_size)
                dim_status = "EXACT" if dim_ok else f"MISMATCH (expected {expected_size}x{expected_size})"
                if not dim_ok:
                    all_valid = False

            print(f"    [{status}] {path}")
            print(f"           Dimensions: {w}x{h} px — {dim_status}")
            print(f"           File size:  {format_file_size(fsize)}")
            print(f"           Mode:       {mode}")
        else:
            all_valid = False
            print(f"    [{status}] {path}")

    # Summary
    print("\n" + "=" * 60)
    if all_valid and len(output.output_paths) > 0:
        print("  SUCCESS: All output assets generated and verified!")
        print(f"  Color count: {output.color_count}")
        if output.palette_name:
            print(f"  Palette:     {output.palette_name}")
        print(f"  Assets:      {len(output.output_paths)} files in {output_dir}/")
    else:
        print("  WARNING: Some outputs failed verification — see details above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
