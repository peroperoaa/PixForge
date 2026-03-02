# Scenario: StageResult Model
- Given: The StageResult model is defined in src/modules/full_pipeline/schemas.py
- When: A user creates a StageResult to record stage execution outcome
- Then: All fields are stored correctly with proper types

## Test Steps

- Case 1 (happy path): Create successful StageResult with output_path
- Case 2 (failure): Create failed StageResult with error_message
- Case 3 (required fields): Missing stage or success raises ValidationError

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
