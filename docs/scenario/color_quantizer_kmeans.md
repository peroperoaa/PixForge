# Scenario: K-Means Color Quantization
- Given: An RGB/RGBA image with many colors
- When: `quantize_kmeans(image, n_colors)` is called
- Then: The output image has at most `n_colors` unique RGB values, alpha is preserved

## Test Steps

- Case 1 (happy path): 10x10 random color image with N=4 produces at most 4 unique RGB colors
- Case 2 (exact): Red/blue checkerboard with N=2 returns exactly red and blue
- Case 3 (error): N < 2 raises ColorQuantizationError
- Case 4 (alpha): RGBA image with alpha=128 retains alpha=128 after quantization

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
