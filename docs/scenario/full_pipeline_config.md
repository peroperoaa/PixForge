# Scenario: FullPipelineConfig Model with Defaults and Validation
- Given: The FullPipelineConfig model is defined in src/modules/full_pipeline/schemas.py
- When: A user creates a FullPipelineConfig instance
- Then: Default values are applied correctly and cross-field validators enforce constraints

## Test Steps

- Case 1 (happy path): Create config with user_prompt, start_stage=PROMPT, verify defaults
- Case 2 (defaults): start_stage=PROMPT, palette_preset='sweetie-16', target_sizes=[32,64], remove_background=True
- Case 3 (cross-validation prompt): Missing user_prompt when start_stage=PROMPT raises ValidationError
- Case 4 (cross-validation image): Missing input_image_path when start_stage=IMAGE raises ValidationError
- Case 5 (cross-validation pixelization): Missing input_image_path when start_stage=PIXELIZATION raises ValidationError
- Case 6 (cross-validation post_processing): Missing input_image_path when start_stage=POST_PROCESSING raises ValidationError
- Case 7 (valid image stage): Providing input_image_path when start_stage=IMAGE succeeds
- Case 8 (all fields): All fields set explicitly work correctly

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
