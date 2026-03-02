"""Artifact detector for identifying existing pipeline outputs."""

from pathlib import Path
from typing import Optional

from src.modules.full_pipeline.schemas import PipelineStage

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class ArtifactDetector:
    """Scans output directories to identify existing pipeline artifacts
    and recommend the optimal start stage."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)

    def scan_output_directory(self) -> list[dict]:
        """Scan output/images/ and output/assets/ for existing artifacts.

        Returns a list of dicts with keys: 'stage', 'path', 'mtime'.
        Files matching '*pixelized*' (case-insensitive) -> PIXELIZATION stage.
        Other image files in images/ -> IMAGE stage.
        Files in assets/ -> POST_PROCESSING stage.
        """
        artifacts: list[dict] = []

        images_dir = self.output_dir / "images"
        if images_dir.is_dir():
            for f in images_dir.iterdir():
                if not f.is_file():
                    continue
                if f.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                if "pixelized" in f.stem.lower():
                    stage = PipelineStage.PIXELIZATION
                else:
                    stage = PipelineStage.IMAGE
                artifacts.append({
                    "stage": stage,
                    "path": f,
                    "mtime": f.stat().st_mtime,
                })

        assets_dir = self.output_dir / "assets"
        if assets_dir.is_dir():
            for f in assets_dir.iterdir():
                if not f.is_file():
                    continue
                artifacts.append({
                    "stage": PipelineStage.POST_PROCESSING,
                    "path": f,
                    "mtime": f.stat().st_mtime,
                })

        return artifacts

    def detect_start_stage(self) -> tuple[PipelineStage, Optional[Path]]:
        """Detect the recommended next pipeline stage based on existing artifacts.

        Returns:
            A tuple of (next_stage, artifact_path):
            - (PROMPT, None) when no artifacts or only assets exist.
            - (PIXELIZATION, image_path) when non-pixelized images are the highest stage.
            - (POST_PROCESSING, pixelized_path) when pixelized images exist.
        """
        artifacts = self.scan_output_directory()

        if not artifacts:
            return PipelineStage.PROMPT, None

        # Filter by stage, pick latest by mtime
        pixelized = [a for a in artifacts if a["stage"] == PipelineStage.PIXELIZATION]
        images = [a for a in artifacts if a["stage"] == PipelineStage.IMAGE]

        if pixelized:
            latest = max(pixelized, key=lambda a: a["mtime"])
            return PipelineStage.POST_PROCESSING, latest["path"]

        if images:
            latest = max(images, key=lambda a: a["mtime"])
            return PipelineStage.PIXELIZATION, latest["path"]

        # Only assets exist - nothing useful to skip to
        return PipelineStage.PROMPT, None
