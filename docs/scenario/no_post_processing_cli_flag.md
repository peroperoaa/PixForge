# Scenario: No Post-Processing CLI Flag Parsing
- Given: The CLI argument parser built by `build_parser()`
- When: `--no-post-processing` flag is passed (or omitted)
- Then: `args.no_post_processing` is `True` (or `False` when omitted)

## Test Steps

- Case 1 (happy path): `--no-post-processing` flag present sets `no_post_processing` to `True`
- Case 2 (default): Flag absent defaults `no_post_processing` to `False`

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
