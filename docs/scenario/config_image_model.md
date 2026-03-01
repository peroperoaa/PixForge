# Scenario: ConfigManager Support for Image Models
- Given: A `ConfigManager` instance with different configurations for the image model (runtime args, file config, environment variables).
- When: Calling `get_image_model()` method on the instance,
- Then: It retrieves and returns the `image_model` name correctly prioritizing runtime args > file config > environment variables over each other, or returns a default string if not specified in any.

## Test Steps

- Case 1 (happy path - runtime priority): Run with runtime `{'image_model': 'runtime-model'}`, file `{'image_model': 'file-model'}`, and env `{'GEMINI_IMAGE_MODEL': 'env-model'}`. Should return `'runtime-model'`.
- Case 2 (happy path - file priority): Run with no runtime `image_model`, file `{'image_model': 'file-model'}`, and env `{'GEMINI_IMAGE_MODEL': 'env-model'}`. Should return `'file-model'`.
- Case 3 (happy path - env priority): Run with no runtime, no file, but env `{'GEMINI_IMAGE_MODEL': 'env-model'}`. Should return `'env-model'`.
- Case 4 (edge case - default): Run with none of the configurations set. Should return the default string `"imagen-3.0-generate-002"`.

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
