# Scenario: Error Handling and Abort
- Given: A FullPipeline where one module adapter raises an exception
- When: run() is called and a stage fails
- Then: The failure is recorded in StageResult with success=False and error_message; remaining stages are aborted

## Test Steps

- Case 1 (prompt stage failure): Prompt generator raises; result shows failure, no further stages run
- Case 2 (mid-pipeline failure): Image gen succeeds but pixelization raises; result shows IMAGE success then PIXELIZATION failure
- Case 3 (timing recorded): Even on failure, duration_seconds is recorded for the failed stage

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
