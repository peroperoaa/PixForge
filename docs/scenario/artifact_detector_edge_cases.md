# Scenario: Artifact Detector - Edge Cases
- Given: Various unusual directory states
- When: ArtifactDetector operates
- Then: Handles all edge cases gracefully

## Test Steps

- Case 1: Non-image files in images/ directory are ignored
- Case 2: Nested subdirectories - only top-level files are scanned
- Case 3: Only final assets exist returns (PROMPT, None)

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
