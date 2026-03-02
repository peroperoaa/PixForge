# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Pixelization Module Schemas
Define Pydantic models `PixelizationInput` and `PixelizationOutput` in `src/modules/pixelization/schemas.py`.
- `PixelizationInput`: `image_path` (str, required), `image_bytes` (Optional[bytes] = None), `prompt` (Optional[str] = None), `denoising_strength` (Optional[float] = None)
- `PixelizationOutput`: `image_path` (str, required), `width` (Optional[int] = None), `height` (Optional[int] = None)

### FR-2: Pixelization Module Interface
Define `BasePixelization` abstract class in `src/modules/pixelization/interface.py` with abstract method `generate(input_data: PixelizationInput) -> PixelizationOutput`.

### FR-3: Pixelization Module Exceptions
Define custom exception classes in `src/modules/pixelization/exceptions.py`:
- `PixelizationError` (base exception)
- `ComfyUIConnectionError(PixelizationError)`
- `ComfyUITimeoutError(PixelizationError)`
- `ComfyUIWorkflowError(PixelizationError)`

## Assumptions

- Follow existing module patterns exactly (image_gen module as reference).
- All `__init__.py` files are empty.
- Schemas validation follows Pydantic v2 conventions consistent with the rest of the project.
