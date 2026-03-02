# Step 1 - Understand Intent (Nearest Neighbor Downscaler)

## Functional Requirements

### FR-1: Downscale Single Image
Downscaler.downscale accepts a PIL Image and an integer target size, and returns a square image of exactly target_size × target_size pixels using PIL NEAREST resampling. Non-square source images are handled (center-crop to square before scaling). RGBA mode is preserved. Raises DownscaleError for invalid target sizes (0 or negative).

### FR-2: Downscale Multiple Sizes
Downscaler.downscale_multi accepts a PIL Image and a list of integer target sizes, and returns a list of images each resized to the corresponding target size. The returned list length matches the input list length.

## Assumptions

- "Target size" is a single integer meaning both width and height (square output).
- Non-square source images are center-cropped to the largest inscribed square before downscaling.
- Target size larger than source is allowed (upscale with NEAREST).
- Image mode (RGB, RGBA, etc.) is preserved through the operation.
