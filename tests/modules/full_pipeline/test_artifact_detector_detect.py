import os
import time
from pathlib import Path

import pytest

from src.modules.full_pipeline.artifact_detector import ArtifactDetector
from src.modules.full_pipeline.schemas import PipelineStage


class TestDetectStartStage:
    """FR-2: detect_start_stage returns recommended next stage and artifact path."""

    def test_no_artifacts_returns_prompt_none(self, tmp_path):
        """Empty directories -> (PROMPT, None)."""
        (tmp_path / "images").mkdir()
        (tmp_path / "assets").mkdir()

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PROMPT
        assert path is None

    def test_non_pixelized_images_returns_pixelization(self, tmp_path):
        """Non-pixelized images -> (PIXELIZATION, latest_image_path)."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        img = images_dir / "landscape.png"
        img.write_bytes(b"fake png")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PIXELIZATION
        assert path == img

    def test_pixelized_images_returns_post_processing(self, tmp_path):
        """Pixelized images exist -> (POST_PROCESSING, latest_pixelized_path)."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        pix = images_dir / "hero_pixelized.png"
        pix.write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.POST_PROCESSING
        assert path == pix

    def test_only_assets_returns_prompt_none(self, tmp_path):
        """Only final assets exist -> (PROMPT, None) since nothing to skip to."""
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "hero_32.png").write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PROMPT
        assert path is None

    def test_latest_file_by_mtime_chosen(self, tmp_path):
        """When multiple images exist, latest by mtime is chosen."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        older = images_dir / "older.png"
        older.write_bytes(b"old")
        # Set older mtime to past
        old_time = time.time() - 100
        os.utime(older, (old_time, old_time))

        newer = images_dir / "newer.png"
        newer.write_bytes(b"new")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PIXELIZATION
        assert path == newer

    def test_missing_output_dir_returns_prompt_none(self, tmp_path):
        """Non-existent output directory -> (PROMPT, None)."""
        nonexistent = tmp_path / "nonexistent_output"

        detector = ArtifactDetector(nonexistent)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.PROMPT
        assert path is None

    def test_pixelized_takes_priority_over_non_pixelized(self, tmp_path):
        """When both pixelized and non-pixelized images exist, pixelized (higher stage) wins."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        (images_dir / "landscape.png").write_bytes(b"fake")
        pix = images_dir / "landscape_pixelized.png"
        pix.write_bytes(b"fake")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.POST_PROCESSING
        assert path == pix

    def test_latest_pixelized_chosen_when_multiple(self, tmp_path):
        """When multiple pixelized images exist, latest by mtime is chosen."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        older_pix = images_dir / "v1_pixelized.png"
        older_pix.write_bytes(b"old")
        old_time = time.time() - 100
        os.utime(older_pix, (old_time, old_time))

        newer_pix = images_dir / "v2_pixelized.png"
        newer_pix.write_bytes(b"new")

        detector = ArtifactDetector(tmp_path)
        stage, path = detector.detect_start_stage()

        assert stage == PipelineStage.POST_PROCESSING
        assert path == newer_pix
