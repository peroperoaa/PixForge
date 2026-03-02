# Scenario: Auto-Detect Mode
- Given: A FullPipeline and an ArtifactDetector that scans output directories
- When: run() is called with start_stage=None
- Then: ArtifactDetector determines the entry point; pipeline executes from the detected stage

## Test Steps

- Case 1 (no artifacts): Auto-detect resolves to PROMPT, full pipeline runs
- Case 2 (image artifacts): Auto-detect resolves to PIXELIZATION with detected image path
- Case 3 (pixelized artifacts): Auto-detect resolves to POST_PROCESSING with detected pixelized path

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
