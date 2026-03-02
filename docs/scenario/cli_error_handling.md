# Scenario: Error Handling and Exit Codes
- Given: Various error conditions during CLI execution
- When: The CLI encounters errors
- Then: Appropriate exit codes are returned and error messages are printed

## Test Steps

- Case 1 (success): Pipeline completes successfully, exit code 0
- Case 2 (pipeline error): Pipeline stage fails, exit code 1
- Case 3 (argument error): Invalid arguments, exit code 2
- Case 4 (keyboard interrupt): Ctrl+C produces graceful exit message and non-zero exit code
- Case 5 (unexpected exception): Uncaught exception exits with code 1 and prints error

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
