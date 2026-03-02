# Scenario: PreProcessing Schema Definitions
- Given: A user wants to configure pre-processing parameters
- When: They create PreProcessingInput with various field combinations
- Then: Valid inputs are accepted with proper defaults, invalid inputs are rejected

## Test Steps

- Case 1 (happy path): Create PreProcessingInput with all defaults - intermediate_size defaults to 256, remove_background defaults to False, crop_mode defaults to "auto"
- Case 2 (custom values): Create PreProcessingInput with custom intermediate_size=128, remove_background=True, crop_mode="center"
- Case 3 (edge case): Reject intermediate_size <= 0
- Case 4 (edge case): Reject invalid crop_mode values
- Case 5 (output schema): Create PreProcessingOutput with valid fields

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
