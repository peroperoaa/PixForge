# Scenario: Post-Processing Interface
- Given: A need for an abstract base class for post-processing implementations
- When: BasePostProcessor is instantiated or subclassed
- Then: Direct instantiation raises TypeError; subclasses must implement process method

## Test Steps

- Case 1 (abstract enforcement): BasePostProcessor raises TypeError on direct instantiation
- Case 2 (incomplete subclass): Subclass without process method raises TypeError on instantiation
- Case 3 (happy path): Concrete subclass implementing process can be instantiated and called

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
