# Scenario: Color Quantizer Dispatch
- Given: An image and either color_count or palette
- When: `quantize(image, color_count=N)` or `quantize(image, palette=P)` is called
- Then: The correct quantization method is dispatched

## Test Steps

- Case 1: Providing palette dispatches to quantize_palette
- Case 2: Providing only color_count dispatches to quantize_kmeans

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
