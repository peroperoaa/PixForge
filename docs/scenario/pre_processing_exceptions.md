# Scenario: PreProcessing Exceptions
- Given: The pre-processing module needs a proper error hierarchy
- When: Errors occur during processing
- Then: Specific exception types are raised that inherit from PreProcessingError

## Test Steps

- Case 1 (happy path): PreProcessingError is the base exception class
- Case 2 (inheritance): BackgroundRemovalError, CropError, DownscaleError all inherit from PreProcessingError
- Case 3 (catch base): Catching PreProcessingError catches all subtype exceptions

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
