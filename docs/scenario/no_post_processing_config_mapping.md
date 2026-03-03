# Scenario: No Post-Processing Config Mapping
- Given: CLI args with `no_post_processing` set to `True` or `False`
- When: `args_to_config()` is called
- Then: The returned `FullPipelineConfig` has `skip_post_processing` matching the flag value

## Test Steps

- Case 1 (happy path): `no_post_processing=True` maps to `skip_post_processing=True`
- Case 2 (default): `no_post_processing=False` maps to `skip_post_processing=False`

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
