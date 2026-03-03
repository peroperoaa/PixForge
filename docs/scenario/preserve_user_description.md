# Scenario: Preserve User Description in Prompt Generation
- Given: A GeminiAdapter is instantiated with a valid ConfigManager
- When: SYSTEM_INSTRUCTION is inspected
- Then: It explicitly states the user input is a scene description (not a command) and requires the user's subject/description to be the core of positive_prompt

## Test Steps

- Case 1 (happy path): SYSTEM_INSTRUCTION contains directive that user input is a scene description
- Case 2 (core subject): SYSTEM_INSTRUCTION contains directive that user description must be the core/subject of positive_prompt
- Case 3 (not a command): SYSTEM_INSTRUCTION contains wording indicating user input is NOT an instruction/command

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
