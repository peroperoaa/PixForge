# Scenario: Artifact Detector - Detect Start Stage
- Given: An output directory with various combinations of artifacts
- When: detect_start_stage is called
- Then: Returns the correct (PipelineStage, Optional[Path]) tuple recommending the next stage and the relevant artifact path

## Test Steps

- Case 1 (happy path - no artifacts): Empty directories -> returns (PROMPT, None)
- Case 2 (happy path - non-pixelized images only): Returns (PIXELIZATION, latest_image_path)
- Case 3 (happy path - pixelized images exist): Returns (POST_PROCESSING, latest_pixelized_path)
- Case 4 (edge case): Only assets exist -> returns (PROMPT, None) since nothing to skip to
- Case 5 (edge case): Multiple images - latest by mtime is chosen
- Case 6 (edge case): Missing output directory -> returns (PROMPT, None)
- Case 7: Both pixelized and non-pixelized images exist - pixelized takes priority (higher stage)

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
