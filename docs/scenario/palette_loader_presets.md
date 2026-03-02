# Scenario: Palette Loader - Built-in Presets
- Given: PaletteLoader with built-in preset palettes
- When: Accessing preset palettes
- Then: Returns correct palettes with expected color counts and valid RGB values

## Test Steps

- Case 1 (GB preset): get_preset('gb') returns exactly 4 RGB tuples matching Game Boy green palette
- Case 2 (Sweetie-16 preset): get_preset('sweetie-16') returns exactly 16 RGB tuples
- Case 3 (valid RGB range): All built-in preset colors have R, G, B values in range 0-255

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
