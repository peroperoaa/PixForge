# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Post-Processing Schemas
Define `PostProcessingInput` and `PostProcessingOutput` Pydantic models in `src/modules/post_processing/schemas.py`.
- `PostProcessingInput`: `image_path` (str), `asset_name` (str), `target_sizes` (list[int], non-empty, all positive), `remove_background` (bool, default False), `color_count` (Optional[int]), `palette_path` (Optional[str]), `output_dir` (Optional[str])
- Validation: `target_sizes` must be non-empty and contain only positive integers
- Validation: At least one of `palette_path` or `color_count` must be provided
- `PostProcessingOutput`: `output_paths` (list[str]), `target_sizes` (list[int]), `color_count` (Optional[int]), `palette_name` (Optional[str])

### FR-2: Post-Processing Interface
Define `BasePostProcessor` abstract class in `src/modules/post_processing/interface.py` with abstract method `process(input_data: PostProcessingInput) -> PostProcessingOutput`.
- Cannot be instantiated directly
- Subclasses must implement `process` method

### FR-3: Post-Processing Exceptions
Define exception hierarchy in `src/modules/post_processing/exceptions.py`:
- `PostProcessingError` (base exception)
- `BackgroundRemovalError(PostProcessingError)`
- `ColorQuantizationError(PostProcessingError)`
- `DownscaleError(PostProcessingError)`

## Assumptions

- Follow existing module patterns (pixelization module as reference).
- All `__init__.py` files are empty.
- Schemas validation follows Pydantic v2 conventions consistent with the rest of the project.
- `palette_path` and `color_count` validation: at least one must be non-None.
