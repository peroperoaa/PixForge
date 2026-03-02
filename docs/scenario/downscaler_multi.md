# Scenario: Downscale Multiple Sizes
- Given: A PIL Image and a list of integer target sizes
- When: Downscaler.downscale_multi(image, target_sizes) is called
- Then: Returns a list of images sized to each target, list length == len(target_sizes)

## Test Steps

- Case 1 (happy path): [32, 64, 128] returns 3 images with matching dimensions

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor

**IMPORTANT**: Only update above status when a step is confirmed complete. Do not hallucinate.
