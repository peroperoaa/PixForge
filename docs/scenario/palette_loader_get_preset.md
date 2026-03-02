# Scenario: Palette Loader - Get Preset by Name
- Given: PaletteLoader with built-in presets
- When: get_preset is called with a preset name
- Then: Returns the matching palette or raises ValueError for unknown names

## Test Steps

- Case 1 (happy path): get_preset('gb') returns the GB palette
- Case 2 (unknown preset): get_preset('nonexistent') raises ValueError with descriptive message

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
