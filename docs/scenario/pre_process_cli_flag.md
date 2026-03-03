# Scenario: Pre-process CLI flag parsing
- Given: The CLI parser is built with `build_parser()`
- When: Arguments are parsed with/without `--pre-process`
- Then: `args.pre_process` is False by default, True when flag is present

## Test Steps

- Case 1 (happy path): `--pre-process` flag sets `args.pre_process` to True
- Case 2 (default): No `--pre-process` flag results in `args.pre_process` being False

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
