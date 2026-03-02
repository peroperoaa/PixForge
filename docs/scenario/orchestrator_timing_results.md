# Scenario: Timing and Results
- Given: A FullPipeline with all stages executing
- When: run() completes (either fully or with a failure)
- Then: FullPipelineResult contains StageResult for each executed stage with duration_seconds and total_duration_seconds

## Test Steps

- Case 1 (all stages timed): Each StageResult has duration_seconds >= 0
- Case 2 (total duration): total_duration_seconds >= sum of individual stage durations (approximately)
- Case 3 (final_asset_paths): On success, final_asset_paths contains post_processing output_paths

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
