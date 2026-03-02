# Scenario: Pipeline Execution with Progress
- Given: A valid FullPipelineConfig and a mocked FullPipeline
- When: The CLI invokes the pipeline and it completes
- Then: Progress lines are printed for each executing stage and a final summary is displayed

## Test Steps

- Case 1 (happy path): Full pipeline prints progress for all 4 stages and summary with asset paths and total time
- Case 2 (partial run): Start from pixelization prints progress only for pixelization and post_processing
- Case 3 (error in stage): Pipeline error produces error info in summary
- Case 4 (output summary format): Summary includes output paths line and total time line

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
