# Scenario: Sequential Stage Execution
- Given: A FullPipeline with all four module adapters injected
- When: run() is called with start_stage=PROMPT and a valid user_prompt
- Then: All four stages execute in order (PROMPT → IMAGE → PIXELIZATION → POST_PROCESSING) and FullPipelineResult contains results for all four stages

## Test Steps

- Case 1 (happy path): Full pipeline from PROMPT to POST_PROCESSING with all stages succeeding
- Case 2 (output chaining): Verify prompt_output.positive_prompt is passed to image_gen, image_output.image_path to pixelization, pixelization_output.image_path to post_processing

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
