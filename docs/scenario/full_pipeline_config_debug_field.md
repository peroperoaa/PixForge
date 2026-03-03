# Scenario: FullPipelineConfig debug field
- Given: A user constructs a FullPipelineConfig
- When: The `debug` field is omitted or explicitly set
- Then: The field defaults to False when omitted, and stores the explicit value when provided

## Test Steps

- Case 1 (happy path): Construct config with only user_prompt; verify debug defaults to False
- Case 2 (explicit True): Construct config with debug=True; verify it is True
- Case 3 (explicit False): Construct config with debug=False; verify it is False

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
