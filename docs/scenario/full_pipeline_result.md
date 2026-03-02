# Scenario: FullPipelineResult Model
- Given: The FullPipelineResult model is defined in src/modules/full_pipeline/schemas.py
- When: A user creates a FullPipelineResult to aggregate pipeline execution outcomes
- Then: stage_results list, final_asset_paths list, and total_duration_seconds are stored correctly

## Test Steps

- Case 1 (happy path): Create result with multiple stage results and final asset paths
- Case 2 (empty): Create result with empty lists and zero duration
- Case 3 (required fields): Missing required fields raises ValidationError

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
