# Scenario: Unit Tests Verify Pixel-Art System Instruction
- Given: The existing test_gemini_adapter.py tests check system_instruction content
- When: Tests are updated for the new pixel-art-optimized instruction
- Then: Tests verify the presence of pixel-art keywords in system_instruction and pass

## Test Steps

- Case 1 (happy path): Updated test_construct_request verifies pixel-art keywords in system_instruction
- Case 2 (backward compat): Existing generate tests still pass with the updated instruction

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
