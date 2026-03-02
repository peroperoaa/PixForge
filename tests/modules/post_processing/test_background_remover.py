import sys
from unittest.mock import MagicMock, patch
from PIL import Image
import pytest

from src.modules.post_processing.exceptions import BackgroundRemovalError


@pytest.fixture
def mock_rembg():
    """Mock the rembg module to avoid requiring it as a real dependency."""
    mock_module = MagicMock()
    with patch.dict(sys.modules, {"rembg": mock_module}):
        yield mock_module


class TestBackgroundRemoverInit:
    """Tests for BackgroundRemover initialization."""

    def test_default_model_is_u2net(self):
        """BackgroundRemover initializes with default model 'u2net' when no model specified."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        remover = BackgroundRemover()
        assert remover.model_name == "u2net"

    def test_custom_model_name(self):
        """BackgroundRemover initializes with custom model name when explicitly provided."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        remover = BackgroundRemover(model_name="isnet-general-use")
        assert remover.model_name == "isnet-general-use"


class TestBackgroundRemoverRemove:
    """Tests for BackgroundRemover.remove method."""

    def test_remove_returns_rgba_from_rgb_input(self, mock_rembg):
        """remove returns RGBA mode image when given RGB input with mock rembg returning known alpha data."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        input_image = Image.new("RGB", (100, 80), (255, 0, 0))
        output_image = Image.new("RGBA", (100, 80), (255, 0, 0, 128))
        
        mock_session = MagicMock()
        mock_rembg.new_session.return_value = mock_session
        mock_rembg.remove.return_value = output_image

        remover = BackgroundRemover(model_name="u2net")
        result = remover.remove(input_image)

        assert result.mode == "RGBA"
        
        # Verify session creation and usage
        mock_rembg.new_session.assert_called_with("u2net")
        mock_rembg.remove.assert_called_with(input_image, session=mock_session)

    def test_remove_returns_rgba_from_rgba_input(self, mock_rembg):
        """remove returns RGBA mode image when given RGBA input (already has alpha) with mock rembg."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        input_image = Image.new("RGBA", (100, 80), (255, 0, 0, 255))
        output_image = Image.new("RGBA", (100, 80), (255, 0, 0, 128))
        mock_rembg.remove.return_value = output_image

        remover = BackgroundRemover()
        result = remover.remove(input_image)

        assert result.mode == "RGBA"
        mock_rembg.remove.assert_called_once()

    def test_output_dimensions_match_input(self, mock_rembg):
        """Output image dimensions match input image dimensions using mock rembg."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        width, height = 200, 150
        input_image = Image.new("RGB", (width, height), (0, 255, 0))
        output_image = Image.new("RGBA", (width, height), (0, 255, 0, 100))
        mock_rembg.remove.return_value = output_image

        remover = BackgroundRemover()
        result = remover.remove(input_image)

        assert result.size == (width, height)
        assert result.width == width
        assert result.height == height

    def test_remove_raises_background_removal_error_on_rembg_failure(self, mock_rembg):
        """remove raises BackgroundRemovalError when rembg throws an internal exception (mocked)."""
        from src.modules.post_processing.background_remover import BackgroundRemover

        input_image = Image.new("RGB", (100, 100), (255, 0, 0))
        mock_rembg.remove.side_effect = RuntimeError("rembg internal error")

        remover = BackgroundRemover()
        with pytest.raises(BackgroundRemovalError, match="Background removal failed"):
            remover.remove(input_image)
