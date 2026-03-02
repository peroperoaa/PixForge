# Scenario: Palette Loader - Load from .hex File
- Given: A .hex palette file with one hex color code per line
- When: PaletteLoader.load_from_hex_file is called with the file path
- Then: Returns a list of (R, G, B) tuples parsed from valid color lines

## Test Steps

- Case 1 (happy path): Parse '0f380f\n306230\n8bac0f\n9bbc0f' into 4 correct RGB tuples
- Case 2 (comments & blanks): Ignore empty lines and lines starting with '#'
- Case 3 (invalid hex): Raise ValueError for hex string with invalid characters like 'ZZZZZZ'
- Case 4 (too few colors): Raise ValueError when file contains fewer than 2 valid colors

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
