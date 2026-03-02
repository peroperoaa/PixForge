import os
import time
from pathlib import Path

import pytest

from src.modules.full_pipeline.artifact_detector import ArtifactDetector
from src.modules.full_pipeline.schemas import PipelineStage


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


class TestScanOutputDirectory:
    """FR-1: Scan output directory for existing artifacts."""

    def test_classifies_non_pixelized_images_as_image_stage(self, tmp_path):
        """Regular images in images/ are classified as IMAGE stage."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "landscape.png").write_bytes(b"fake png")
        (images_dir / "portrait.jpg").write_bytes(b"fake jpg")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        image_artifacts = [a for a in artifacts if a["stage"] == PipelineStage.IMAGE]
        assert len(image_artifacts) == 2

    def test_classifies_pixelized_images_as_pixelization_stage(self, tmp_path):
        """Files matching *pixelized* pattern are classified as PIXELIZATION stage."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "hero_pixelized_v2.png").write_bytes(b"fake")
        (images_dir / "landscape_pixelized.jpg").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        pix_artifacts = [a for a in artifacts if a["stage"] == PipelineStage.PIXELIZATION]
        assert len(pix_artifacts) == 2

    def test_classifies_assets_as_post_processing_stage(self, tmp_path):
        """Files in assets/ are classified as POST_PROCESSING stage."""
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "hero_32.png").write_bytes(b"fake")
        (assets_dir / "hero_64.png").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        asset_artifacts = [a for a in artifacts if a["stage"] == PipelineStage.POST_PROCESSING]
        assert len(asset_artifacts) == 2

    def test_empty_directory_returns_no_artifacts(self, tmp_path):
        """Empty output directory yields empty artifact list."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        assert artifacts == []

    def test_missing_subdirectories_no_error(self, tmp_path):
        """Missing images/ and assets/ subdirectories don't cause errors."""
        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        assert artifacts == []

    def test_pixelized_pattern_case_insensitive(self, tmp_path):
        """'Pixelized' pattern matching is case-insensitive."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "hero_PIXELIZED.png").write_bytes(b"fake")
        (images_dir / "char_Pixelized_v1.jpg").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        pix_artifacts = [a for a in artifacts if a["stage"] == PipelineStage.PIXELIZATION]
        assert len(pix_artifacts) == 2

    def test_mixed_artifacts_classified_correctly(self, tmp_path):
        """Mixed directory with all types classifies each correctly."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()

        (images_dir / "landscape.png").write_bytes(b"fake")
        (images_dir / "landscape_pixelized.png").write_bytes(b"fake")
        (assets_dir / "hero_32.png").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        artifacts = detector.scan_output_directory()

        stages = {a["stage"] for a in artifacts}
        assert PipelineStage.IMAGE in stages
        assert PipelineStage.PIXELIZATION in stages
        assert PipelineStage.POST_PROCESSING in stages
        assert len(artifacts) == 3
