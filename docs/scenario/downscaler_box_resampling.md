# Scenario: Switch Downscaler to BOX Resampling
- Given: A PIL Image of any size and mode (RGB/RGBA)
- When: Downscaler.downscale(image, target_size) is called
- Then: Returns a square PIL Image of exactly target_size × target_size pixels using BOX (area-average) resampling

## Test Steps

- Case 1 (area averaging): 4x4 checkerboard downscaled to 2x2 produces averaged colors (gray), not sampled single pixels
- Case 2 (solid color): 100x100 solid-color image downscaled to 10x10 preserves the exact solid color
- Case 3 (error handling): target_size <= 0 still raises DownscaleError

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
