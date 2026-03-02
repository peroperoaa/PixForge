# Scenario: Downscale Single Image
- Given: A PIL Image of any size and mode (RGB/RGBA)
- When: Downscaler.downscale(image, target_size) is called
- Then: Returns a square PIL Image of exactly target_size × target_size pixels using NEAREST resampling

## Test Steps

- Case 1 (happy path): 256x256 RGBA image downscaled to 32 → 32x32 RGBA
- Case 2 (happy path): 512x512 RGB image downscaled to 64 → 64x64 RGB
- Case 3 (mode preservation): RGBA image stays RGBA after downscale
- Case 4 (pixel fidelity): 4x4 checkerboard downscaled to 2x2 produces exact nearest-neighbor pixels (no blending)
- Case 5 (invalid size zero): target_size=0 raises DownscaleError
- Case 6 (invalid size negative): target_size=-1 raises DownscaleError
- Case 7 (non-square source): 256x128 image downscaled to 32 → 32x32

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
