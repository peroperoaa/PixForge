# Scenario: Prompt Models

## Feature: Prompt Input Validation
- **Given**: A strict Pydantic model `PromptInput`.
- **When**: Validating input data.
- **Then**: It must enforce required fields and correct types.

## Feature: Prompt Output Structure
- **Given**: A strict Pydantic model `PromptOutput`.
- **When**: Creating an instance.
- **Then**: It must enforce the structure of the generated prompt.

## Feature: Schema Export
- **Given**: The `PromptOutput` model.
- **When**: Requesting the JSON schema.
- **Then**: It must return a valid JSON schema object.

## Test Steps

### Case 1: PromptInput Validation - Happy Path
- **Description**: Provide valid `text_prompt` and optional `image_path`.
- **Expectation**: Model validates successfully.

### Case 2: PromptInput Validation - Missing Required Field
- **Description**: Omit `text_prompt`.
- **Expectation**: Raise `ValidationError`.

### Case 3: PromptInput Validation - Invalid Type
- **Description**: Provide integer for `text_prompt`.
- **Expectation**: Raise `ValidationError` (strict mode is implied by "strict Pydantic schemas", although default coercion might happen unless `strict=True` is set). I will implement standard Pydantic validation first.

### Case 4: PromptOutput Validation - Happy Path
- **Description**: Provide valid `positive_prompt`, `negative_prompt`, and `style_parameters`.
- **Expectation**: Model validates successfully.

### Case 5: PromptOutput Validation - Missing Fields
- **Description**: Omit `positive_prompt` or `style_parameters`.
- **Expectation**: Raise `ValidationError`.

### Case 6: Schema Export
- **Description**: Call `PromptOutput.model_json_schema()`.
- **Expectation**: The output is a dictionary containing `properties` for `positive_prompt`, `negative_prompt`, and `style_parameters`.

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [ ] Run test and watch it failing
- [ ] Implement to make test pass
- [ ] Run test and confirm it passed
- [ ] Refactor implementation without breaking test
- [ ] Run test and confirm still passing after refactor
