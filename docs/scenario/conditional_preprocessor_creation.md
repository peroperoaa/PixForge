# Scenario: Conditional PreProcessor creation in pipeline factory
- Given: The `create_pipeline()` function creates the production pipeline
- When: `pre_process=True` is passed, PreProcessor is created; when `pre_process=False` (default), it is None
- Then: The FullPipeline instance has `_pre_processor` set correctly

## Test Steps

- Case 1 (default): `create_pipeline()` without pre_process flag produces pipeline with `_pre_processor is None`
- Case 2 (enabled): `create_pipeline(pre_process=True)` produces pipeline with a real PreProcessor instance
- Case 3 (edge): `run_pipeline` threads the flag correctly from parsed args through to pipeline creation

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
