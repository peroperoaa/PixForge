# Step 1 - Understand Intent

## Functional Requirements

### FR-1: PreProcessing Schema Definitions
Define PreProcessingInput and PreProcessingOutput Pydantic schemas with proper validation. PreProcessingInput includes image_path (str), remove_background (bool, default False), intermediate_size (int, default 256), crop_mode (str, default "auto"). PreProcessingOutput includes image_path (str), original_size (tuple[int,int]), intermediate_size (int).

### FR-2: PreProcessor Process Pipeline
Implement PreProcessor.process() method that loads a high-res image, optionally removes background, crops to square, downscales to intermediate_size using LANCZOS resampling, saves and returns the result path.

### FR-3: Subject-Aware Cropping
Implement subject-aware cropping: when the image has an alpha channel, use the alpha bounding box to center the subject in a square crop. Fallback to center crop when no alpha channel is available.

### FR-4: PreProcessing Exceptions
Define proper exception hierarchy for the pre-processing module: PreProcessingError (base), BackgroundRemovalError, CropError, DownscaleError.

## Assumptions

- The pre-processing module reuses the rembg-based background removal approach from post_processing (mocked in tests).
- crop_mode "auto" means: use alpha bounding box if available, fallback to center crop.
- crop_mode "center" means: always use center crop regardless of alpha channel.
- The output image is always saved as PNG.
- LANCZOS resampling is used (not NEAREST like post_processing) because this is an intermediate step before pixelization where smooth downscale is desired.
