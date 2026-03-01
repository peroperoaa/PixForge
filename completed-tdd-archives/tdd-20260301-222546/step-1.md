# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Base Image Generator Interface
- Create `src/modules/image_gen` and `tests/modules/image_gen` directories with `__init__.py`.
- Create `src/modules/image_gen/schemas.py` defining `ImageGenInput` and `ImageGenOutput` schemas.
- Create `src/modules/image_gen/interface.py` to define an abstract base class `BaseImageGenerator` that standardizes the image generation interface across different providers.
- It must accept `ImageGenInput` and return `ImageGenOutput` via an abstract method `generate(input: ImageGenInput) -> ImageGenOutput`.
- The interface must prevent direct instantiation by being strictly abstract.

## Assumptions
- `ImageGenInput` will require at least a text prompt and an optional image path (similar to `PromptInput`), and `ImageGenOutput` will have an `image_path` linking to the generated output. Both will subclass `pydantic.BaseModel`.
- The interface module `BaseImageGenerator` uses `abc.ABC` and `abc.abstractmethod`.
