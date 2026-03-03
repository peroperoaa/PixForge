# Scenario: Pipeline Skips Post-Processing Stage
- Given: A `FullPipelineConfig` with `skip_post_processing=True`
- When: `FullPipeline.run()` is called
- Then: POST_PROCESSING stage is not executed; `final_asset_paths` contains the pixelized image path; POST_PROCESSING does not appear in `stage_results`

## Test Steps

- Case 1 (happy path): `skip_post_processing=True` stops pipeline after PIXELIZATION, `final_asset_paths` = [pixelized image path]
- Case 2 (default behavior): `skip_post_processing=False` runs all stages including POST_PROCESSING
- Case 3 (edge case): `skip_post_processing=True` with `start_stage=PIXELIZATION` still skips POST_PROCESSING

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
