# Scenario: BasePromptGenerator Interface
- Given: An abstract base class `BasePromptGenerator`
- When: Instantiated directly
- Then: Raise `TypeError` indicating abstract methods

## Test Steps

- Case 1 (abstract instantiation): Try to instantiate `BasePromptGenerator` directly, should raise `TypeError`.
- Case 2 (incomplete mock subclass): Try to subclass `BasePromptGenerator` without implementing `generate`, instantiation should raise `TypeError`.
- Case 3 (complete mock subclass): Subclass `BasePromptGenerator` and implement `generate`, instantiation works.

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
