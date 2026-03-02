# Scenario: PipelineStage Enum with Ordering
- Given: The PipelineStage enum is defined in src/modules/full_pipeline/schemas.py
- When: A user references PipelineStage members or compares them
- Then: The enum has exactly 4 members (PROMPT, IMAGE, PIXELIZATION, POST_PROCESSING) supporting ordering comparison

## Test Steps

- Case 1 (happy path): Enum has exactly 4 members in correct order
- Case 2 (ordering): PROMPT < IMAGE < PIXELIZATION < POST_PROCESSING
- Case 3 (equality): Same stages compare equal
- Case 4 (comparison operators): <=, >=, >, < all work correctly

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
