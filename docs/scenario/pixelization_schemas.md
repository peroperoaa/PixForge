# Scenario: Pixelization Schemas Validation
- Given: A user provides input/output data for the pixelization module
- When: The data is used to construct PixelizationInput or PixelizationOutput
- Then: Valid data constructs successfully; invalid/missing required fields raise ValidationError

## Test Steps

- Case 1 (happy path): PixelizationInput with all fields provided validates successfully
- Case 2 (happy path): PixelizationInput with only required field (image_path) validates, optional fields default to None
- Case 3 (edge case): PixelizationInput missing required image_path raises ValidationError
- Case 4 (happy path): PixelizationOutput with all fields provided validates successfully
- Case 5 (happy path): PixelizationOutput with only required field (image_path) validates, optional fields default to None
- Case 6 (edge case): PixelizationOutput missing required image_path raises ValidationError

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
