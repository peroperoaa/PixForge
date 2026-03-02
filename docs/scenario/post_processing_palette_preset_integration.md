# Scenario: Integration - palette_preset end-to-end
- Given: A real image and PostProcessingPipeline
- When: process() is called with palette_preset='sweetie-16' on a real image
- Then: Output image uses only sweetie-16 palette colors, output palette_name='sweetie-16'

## Test Steps

- Case 1 (happy path): Full integration with palette_preset='sweetie-16' produces correct output
- Case 2 (edge case): palette_preset='gb' also works end-to-end

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [ ] Refactor implementation without breaking test
- [ ] Run test and confirm still passing after refactor
