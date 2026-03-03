# Scenario: Pipeline Debug Output
- Given: A FullPipeline orchestrator with mocked modules
- When: `run()` is called with `config.debug=True`
- Then: `[DEBUG]` lines appear in stdout showing stage-specific information

## Test Steps

- Case 1 (happy path, debug=True): Full pipeline run prints debug lines for all stages (PROMPT, IMAGE, PIXELIZATION, POST_PROCESSING)
- Case 2 (debug=False): Full pipeline run produces no `[DEBUG]` lines in stdout
- Case 3 (with pre-processor, debug=True): Pipeline run with pre-processor prints additional debug line for pre-processed image path
- Case 4 (stage failure): Debug lines appear for completed stages but not for failed/skipped stages

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
