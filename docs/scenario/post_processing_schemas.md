# Scenario: Post-Processing Schemas
- Given: A need to validate post-processing input parameters and serialize output
- When: PostProcessingInput or PostProcessingOutput is constructed
- Then: Validation enforces constraints; serialization produces correct types

## Test Steps

- Case 1 (happy path): PostProcessingInput accepts valid fields including target_sizes=[32,64], remove_background=True, color_count=16
- Case 2 (edge case): PostProcessingInput rejects empty target_sizes list
- Case 3 (edge case): PostProcessingInput rejects target_sizes containing non-positive integers (0 or negative)
- Case 4 (palette mode): PostProcessingInput accepts palette_path without color_count
- Case 5 (K-Means mode): PostProcessingInput accepts color_count without palette_path
- Case 6 (output serialization): PostProcessingOutput serializes output_paths as list of file path strings

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
