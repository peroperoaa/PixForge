import os
from pathlib import Path

import pytest

from src.modules.full_pipeline.artifact_detector import ArtifactDetector
from src.modules.full_pipeline.schemas import PipelineStage


class TestArtifactDetectorEdgeCases:
    """FR-3: Edge cases for ArtifactDetector."""

    def test_non_image_files_in_images_dir_ignored(self, tmp_path):
        """Non-image files (e.g. .txt, .json) in images/ are ignored."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "readme.txt").write_text("not an image")
        (images_dir / "metadata.json").write_text("{}")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        assert artifacts == []

    def test_non_image_files_ignored_in_detect(self, tmp_path):
        """Non-image files don't affect detect_start_stage."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "notes.txt").write_text("notes")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PROMPT
        assert path is None

    def test_only_assets_returns_prompt(self, tmp_path):
        """Only final assets exist -> (PROMPT, None)."""
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "sprite_32.png").write_bytes(b"fake")
        (assets_dir / "sprite_64.png").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PROMPT
        assert path is None
