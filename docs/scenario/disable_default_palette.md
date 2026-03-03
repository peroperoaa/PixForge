# Scenario: Default Palette Preset is None

- Given: No `--palette` or `--colors` CLI argument is provided
- When: The CLI parses arguments and maps them to `FullPipelineConfig`
- Then: `FullPipelineConfig.palette_preset` is `None` and `color_count` is `None`

## Test Steps

- Case 1 (happy path): `FullPipelineConfig()` with only `user_prompt` has `palette_preset=None`
- Case 2 (explicit palette): `FullPipelineConfig(palette_preset='sweetie-16')` sets it correctly
- Case 3 (CLI default): `parse_args(['--prompt', 'x'])` produces `args.palette == None`
- Case 4 (CLI explicit): `parse_args(['--prompt', 'x', '--palette', 'gb'])` produces `args.palette == 'gb'`
- Case 5 (args_to_config default): `args_to_config` with no palette arg produces `config.palette_preset == None`
- Case 6 (args_to_config explicit): `args_to_config` with `--palette sweetie-16` produces `config.palette_preset == 'sweetie-16'`

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
