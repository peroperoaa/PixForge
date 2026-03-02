# Scenario: Pixelization Custom Exceptions
- Given: The pixelization module encounters ComfyUI-related errors
- When: Exceptions are raised
- Then: They follow the correct inheritance hierarchy and carry appropriate messages

## Test Steps

- Case 1 (happy path): PixelizationError can be raised and caught
- Case 2 (happy path): ComfyUIConnectionError is a subclass of PixelizationError
- Case 3 (happy path): ComfyUITimeoutError is a subclass of PixelizationError
- Case 4 (happy path): ComfyUIWorkflowError is a subclass of PixelizationError
- Case 5 (edge case): Catching PixelizationError also catches all ComfyUI sub-exceptions

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
