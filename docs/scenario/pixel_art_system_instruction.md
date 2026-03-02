# Scenario: Pixel-Art System Instruction
- Given: A GeminiAdapter is instantiated with a valid ConfigManager
- When: `_construct_request` is called with a PromptInput
- Then: The returned GenerateContentConfig's system_instruction contains pixel-art-specific constraints: 'centered', 'simple background' or 'transparent background', 'clear outlines', 'front view' or '3/4 view'

## Test Steps

- Case 1 (happy path): system_instruction contains all required pixel-art keywords
- Case 2 (positive_prompt directive): system_instruction instructs the model to include pixel-art-friendly directives in the positive_prompt output
- Case 3 (negative_prompt directive): system_instruction instructs the model to include common pixel-art anti-patterns in the negative_prompt

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
