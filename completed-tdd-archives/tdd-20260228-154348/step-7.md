# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Prompt Input Model
Define a strict Pydantic model `PromptInput` to validate user input.
- `text_prompt`: String, required.
- `image_path`: String, optional.

### FR-2: Prompt Output Model
Define a strict Pydantic model `PromptOutput` to structure the generation result.
- `positive_prompt`: String, required.
- `negative_prompt`: String, required.
- `style_parameters`: Dictionary, required (or optional, assuming required based on description "Define PromptOutput model (positive_prompt, negative_prompt, style_parameters)").

### FR-3: JSON Schema Export
The `PromptOutput` model must be capable of exporting its JSON schema, which is a built-in feature of Pydantic but needs verification.

## Assumptions
- `style_parameters` will be a dictionary of strings to any type, or a specific model if detailed later. For now, I'll assume `Dict[str, Any]`.
- We are using Pydantic V2.
