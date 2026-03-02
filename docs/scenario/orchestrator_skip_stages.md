# Scenario: Stage Skipping
- Given: A FullPipeline with all four module adapters injected
- When: run() is called with start_stage > PROMPT (e.g., PIXELIZATION) and a valid input_image_path
- Then: Only stages from start_stage onwards execute; earlier stages are skipped

## Test Steps

- Case 1 (skip to IMAGE): start_stage=IMAGE, only IMAGE/PIXELIZATION/POST_PROCESSING execute
- Case 2 (skip to PIXELIZATION): start_stage=PIXELIZATION, only PIXELIZATION/POST_PROCESSING execute
- Case 3 (skip to POST_PROCESSING): start_stage=POST_PROCESSING, only POST_PROCESSING executes

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
