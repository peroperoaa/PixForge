# Step 1 - Understand Intent

## Functional Requirements

### FR-1: ConfigManager Support for Image Models
Update `ConfigManager` to handle different model keys for image generation.
Add `get_image_model()` method to `ConfigManager` that retrieves the image generation model. It must prioritize the CLI runtime argument `--image-model` over the environment variable `GEMINI_IMAGE_MODEL`. If neither is present, it returns a default string.

## Assumptions

- The CLI runtime argument `--image-model` corresponds to the key `'image_model'` in the `runtime_config` dictionary.
- The default string to return if no model is specified is `"imagen-3.0-generate-002"`.
- We also check the configuration file using the key `'image_model'` in the `file_config` to be consistent with the ConfigManager's existing priority pattern (Runtime > File > Env) although the requirement only strictly mandates prioritizing CLI over `.env`.
