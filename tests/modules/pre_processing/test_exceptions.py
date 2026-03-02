"""Tests for pre-processing exception hierarchy."""

import pytest


class TestPreProcessingExceptions:
    """Tests for the pre-processing exception hierarchy."""

    def test_base_exception_is_exception(self):
        """PreProcessingError inherits from Exception."""
        from src.modules.pre_processing.exceptions import PreProcessingError

        assert issubclass(PreProcessingError, Exception)
        exc = PreProcessingError("test error")
        assert str(exc) == "test error"

    def test_background_removal_error_inherits_base(self):
        """BackgroundRemovalError inherits from PreProcessingError."""
        from src.modules.pre_processing.exceptions import (
            PreProcessingError,
            BackgroundRemovalError,
        )

        assert issubclass(BackgroundRemovalError, PreProcessingError)

    def test_crop_error_inherits_base(self):
        """CropError inherits from PreProcessingError."""
        from src.modules.pre_processing.exceptions import (
            PreProcessingError,
            CropError,
        )

        assert issubclass(CropError, PreProcessingError)

    def test_downscale_error_inherits_base(self):
        """DownscaleError inherits from PreProcessingError."""
        from src.modules.pre_processing.exceptions import (
            PreProcessingError,
            DownscaleError,
        )

        assert issubclass(DownscaleError, PreProcessingError)

    def test_catch_base_catches_all_subtypes(self):
        """Catching PreProcessingError catches all subtype exceptions."""
        from src.modules.pre_processing.exceptions import (
            PreProcessingError,
            BackgroundRemovalError,
            CropError,
            DownscaleError,
        )

        for exc_class in [BackgroundRemovalError, CropError, DownscaleError]:
            with pytest.raises(PreProcessingError):
                raise exc_class(f"test {exc_class.__name__}")
