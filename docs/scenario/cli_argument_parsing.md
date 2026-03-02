# Scenario: CLI Argument Parsing
- Given: A user invokes `python main.py` with various flags
- When: argparse processes the arguments
- Then: All arguments are parsed with correct types and defaults

## Test Steps

- Case 1 (happy path): `--prompt 'a pixel art sword'` parses prompt correctly
- Case 2 (all flags): All flags provided are parsed with correct values
- Case 3 (defaults): No optional flags uses sensible defaults
- Case 4 (sizes parsing): `--sizes 32,64,128` parsed as list of ints
- Case 5 (start-from case insensitive): `--start-from Post_Processing` accepted
- Case 6 (mutual exclusivity): `--prompt` and `--input` can coexist for img2img
- Case 7 (no args): No args at all triggers argument error (exit code 2)

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
