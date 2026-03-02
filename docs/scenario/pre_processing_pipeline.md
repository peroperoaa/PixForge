# Scenario: PreProcessor Process Pipeline
- Given: A high-resolution image exists on disk
- When: PreProcessor.process() is called with valid PreProcessingInput
- Then: The image is loaded, optionally background-removed, cropped to square, downscaled to intermediate_size using LANCZOS, saved, and the output path is returned

## Test Steps

- Case 1 (happy path): Process a 512x512 RGB image with defaults -> produces 256x256 intermediate PNG
- Case 2 (background removal): Process with remove_background=True -> background removal is called before crop
- Case 3 (custom size): Process with intermediate_size=128 -> produces 128x128 output
- Case 4 (non-square input): Process a 640x480 image -> crops to square first, then downscales
- Case 5 (LANCZOS resampling): Verify output uses LANCZOS (not NEAREST) for smooth intermediate
- Case 6 (edge case): image_path does not exist -> raises PreProcessingError
- Case 7 (output schema): Returned PreProcessingOutput has correct original_size and intermediate_size

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
