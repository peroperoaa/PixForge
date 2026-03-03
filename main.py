#!/usr/bin/env python
"""CLI entry point for the pixel-art generation pipeline.

Usage examples:
    python main.py --prompt 'a pixel art sword'
    python main.py --input img.png --start-from post_processing
    python main.py --auto-detect
    python main.py --prompt 'a sword' --palette gb --sizes 32,64,128
"""

import argparse
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.config import ConfigManager
from src.modules.full_pipeline.schemas import (
    FullPipelineConfig,
    FullPipelineResult,
    PipelineStage,
)
from src.modules.full_pipeline.orchestrator import FullPipeline


# Mapping from user-facing stage names to PipelineStage enum values
_STAGE_MAP: dict[str, PipelineStage] = {
    "prompt": PipelineStage.PROMPT,
    "image": PipelineStage.IMAGE,
    "pixelization": PipelineStage.PIXELIZATION,
    "post_processing": PipelineStage.POST_PROCESSING,
}


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Pixel-art asset generation pipeline",
        epilog=(
            "Examples:\n"
            "  python main.py --prompt 'a pixel art sword'\n"
            "  python main.py --input img.png --start-from post_processing\n"
            "  python main.py --auto-detect\n"
            "  python main.py --prompt 'a sword' --palette gb --colors 8\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Text prompt for image generation (required when starting from prompt stage)",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to an input image (required when starting from image/pixelization/post_processing)",
    )
    parser.add_argument(
        "--start-from",
        type=str,
        default=None,
        dest="start_from",
        help="Pipeline stage to start from: prompt, image, pixelization, post_processing (case-insensitive)",
    )
    parser.add_argument(
        "--aspect-ratio",
        type=str,
        default="1:1",
        dest="aspect_ratio",
        help="Aspect ratio for image generation (default: 1:1)",
    )
    parser.add_argument(
        "--palette",
        type=str,
        default="sweetie-16",
        help="Color palette preset name (sweetie-16, gb, nes) or path to a .hex file (default: sweetie-16)",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=None,
        help="Number of colors for K-Means quantization (overrides palette mode)",
    )
    parser.add_argument(
        "--sizes",
        type=str,
        default="32,64",
        help="Comma-separated target asset sizes in pixels (default: 32,64)",
    )
    parser.add_argument(
        "--no-remove-bg",
        action="store_true",
        default=False,
        dest="no_remove_bg",
        help="Disable background removal",
    )
    parser.add_argument(
        "--asset-name",
        type=str,
        default=None,
        dest="asset_name",
        help="Base name for output asset files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        dest="output_dir",
        help="Output directory for generated assets",
    )
    parser.add_argument(
        "--auto-detect",
        action="store_true",
        default=False,
        dest="auto_detect",
        help="Auto-detect start stage from existing artifacts in the output directory",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug output for verbose logging and diagnostics",
    )

    return parser


def _parse_sizes(sizes_str: str) -> list[int]:
    """Parse comma-separated size string into list of ints."""
    return [int(s.strip()) for s in sizes_str.split(",")]


def _resolve_stage(start_from: str | None, auto_detect: bool) -> PipelineStage | None:
    """Resolve start stage from CLI flags.

    Returns None for auto-detect mode, or a PipelineStage value.
    Exits with code 2 on invalid stage name.
    """
    if auto_detect:
        return None

    if start_from is None:
        return PipelineStage.PROMPT

    key = start_from.strip().lower()
    if key not in _STAGE_MAP:
        valid = ", ".join(_STAGE_MAP.keys())
        print(f"Error: Invalid --start-from value '{start_from}'. Valid values: {valid}", file=sys.stderr)
        raise SystemExit(2)

    return _STAGE_MAP[key]


def args_to_config(args: argparse.Namespace) -> FullPipelineConfig:
    """Map parsed CLI arguments to a FullPipelineConfig.

    Raises SystemExit(2) on validation errors.
    """
    # Validate: at least one of --prompt, --input, or --auto-detect must be given
    if not args.prompt and not args.input and not args.auto_detect:
        print(
            "Error: At least one of --prompt, --input, or --auto-detect is required.\n"
            "Run with --help for usage information.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    start_stage = _resolve_stage(args.start_from, args.auto_detect)
    target_sizes = _parse_sizes(args.sizes)

    try:
        config = FullPipelineConfig(
            user_prompt=args.prompt,
            input_image_path=args.input,
            start_stage=start_stage,
            aspect_ratio=args.aspect_ratio,
            palette_preset=args.palette,
            color_count=args.colors,
            target_sizes=target_sizes,
            remove_background=not args.no_remove_bg,
            asset_name=args.asset_name,
            output_dir=args.output_dir,
            debug=args.debug,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)

    return config


def create_pipeline() -> FullPipeline:
    """Create a FullPipeline instance with real adapters.

    This is the production factory — tests mock this function.
    """
    from src.modules.prompt_gen.gemini_adapter import GeminiAdapter
    from src.modules.image_gen.gemini_adapter import GeminiImageAdapter
    from src.modules.pixelization.comfyui_adapter import ComfyUIAdapter
    from src.modules.post_processing.pipeline import PostProcessingPipeline

    config_manager = ConfigManager()
    return FullPipeline(
        config_manager=config_manager,
        prompt_generator=GeminiAdapter(config_manager),
        image_generator=GeminiImageAdapter(config_manager),
        pixelizer=ComfyUIAdapter(config_manager),
        post_processor=PostProcessingPipeline(),
    )


def _print_stage_progress(result: FullPipelineResult) -> None:
    """Print stage-by-stage progress and final summary."""
    print("\n=== Pipeline Execution ===\n")

    has_error = False
    for sr in result.stage_results:
        status = "OK" if sr.success else "FAILED"
        line = f"  [{status}] {sr.stage.name} ({sr.duration_seconds:.2f}s)"
        if sr.output_path:
            line += f" -> {sr.output_path}"
        if sr.error_message:
            line += f" | Error: {sr.error_message}"
            has_error = True
        print(line)

    print(f"\n=== Summary ===\n")

    if result.final_asset_paths:
        print("Output assets:")
        for p in result.final_asset_paths:
            print(f"  {p}")
    else:
        print("No output assets produced.")

    print(f"\nTotal time: {result.total_duration_seconds:.2f}s")

    if has_error:
        failed = [sr for sr in result.stage_results if not sr.success]
        print("\nErrors:")
        for sr in failed:
            print(f"  {sr.stage.name}: {sr.error_message}")


def run_pipeline(config: FullPipelineConfig) -> int:
    """Run the pipeline and print progress.

    Returns:
        Exit code: 0 on success, 1 on pipeline error, 130 on keyboard interrupt.
    """
    try:
        pipeline = create_pipeline()
        result = pipeline.run(config)
        _print_stage_progress(result)

        # Determine exit code from results
        has_failure = any(not sr.success for sr in result.stage_results)
        return 1 if has_failure else 0

    except KeyboardInterrupt:
        print("\nPipeline interrupted by user (Ctrl+C). Cancelled.")
        return 130

    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1


def main() -> int:
    """CLI entry point.

    Returns:
        Exit code: 0 success, 1 pipeline error, 2 argument error.
    """
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = args_to_config(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    return run_pipeline(config)


if __name__ == "__main__":
    sys.exit(main())
