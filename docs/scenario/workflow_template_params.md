# Scenario: Workflow Template Parameter Optimization
- Given: The workflow_api_template.json file exists with current parameter values
- When: The template is loaded by ComfyUIAdapter
- Then: KSampler denoise is 0.32, ControlNet strength is 0.65, negative prompt includes anatomy terms, positive prompt is a generic placeholder

## Test Steps

- Case 1 (happy path): Verify denoise in KSampler node is 0.32
- Case 2 (happy path): Verify ControlNet strength in ControlNetApply node is 0.65
- Case 3 (happy path): Verify negative prompt includes 'deformed, bad anatomy, extra limbs, mutation'
- Case 4 (happy path): Verify positive prompt is a replaceable placeholder

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
