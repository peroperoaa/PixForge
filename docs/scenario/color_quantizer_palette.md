# Scenario: Palette-Based Color Quantization
- Given: An RGB/RGBA image and a fixed palette of colors
- When: `quantize_palette(image, palette)` is called
- Then: Every pixel in the output matches one of the palette colors, alpha is preserved

## Test Steps

- Case 1 (nearest): Pure red (255,0,0) maps to (200,0,0) in a 3-color palette
- Case 2 (gb palette): GB 4-color palette produces output with only those 4 colors
- Case 3 (strict): Output contains zero colors not present in the input palette
- Case 4 (alpha): RGBA image with alpha=0 retains alpha=0 after quantization

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
