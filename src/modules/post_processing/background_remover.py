from PIL import Image

from src.modules.post_processing.exceptions import BackgroundRemovalError


class BackgroundRemover:
    """Wraps the rembg library to remove image backgrounds and produce alpha-channel PNGs."""

    def __init__(self, model_name: str = "u2net"):
        """Initialize BackgroundRemover.

        Args:
            model_name: The rembg model to use for background removal.
                Defaults to 'u2net'.
        """
        self.model_name = model_name

    def remove(self, image: Image.Image) -> Image.Image:
        """Remove background from an image and return an RGBA image with alpha channel.

        Args:
            image: Input PIL Image (RGB or RGBA).

        Returns:
            PIL Image in RGBA mode with background removed via alpha channel.

        Raises:
            BackgroundRemovalError: If background removal fails for any reason.
        """
        try:
            import rembg

            session = rembg.new_session(self.model_name)
            result = rembg.remove(image, session=session)

            if not isinstance(result, Image.Image):
                raise BackgroundRemovalError(
                    "rembg did not return a valid PIL Image"
                )

            return result.convert("RGBA")

        except BackgroundRemovalError:
            raise
        except Exception as e:
            raise BackgroundRemovalError(
                f"Background removal failed: {e}"
            ) from e
