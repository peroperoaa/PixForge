# Scenario: PostProcessingInput palette_preset field
- Given: PostProcessingInput schema
- When: A user provides `palette_preset='sweetie-16'`
- Then: The input is accepted and the field is stored

## Test Steps

- Case 1 (happy path): Accept palette_preset='sweetie-16' without palette_path
- Case 2 (happy path): Accept palette_preset=None (default, unchanged behavior)
- Case 3 (edge case): Reject when both palette_preset and palette_path are set (ValueError)
- Case 4 (edge case): Accept palette_preset with color_count=None (quantization still triggered)

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [ ] Refactor implementation without breaking test
- [ ] Run test and confirm still passing after refactor
