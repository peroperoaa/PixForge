# Scenario: Argument-to-Config Mapping
- Given: Parsed CLI arguments from argparse
- When: Arguments are mapped to FullPipelineConfig
- Then: Config object has correct field values including palette detection and stage mapping

## Test Steps

- Case 1 (happy path): `--prompt 'sword' --palette sweetie-16` maps to config with palette_preset='sweetie-16'
- Case 2 (hex file palette): `--palette custom.hex --input img.png --start-from pixelization` sets palette_preset to file path
- Case 3 (kmeans mode): `--colors 8` sets color_count=8
- Case 4 (auto-detect): `--auto-detect --input img.png` sets start_stage=None
- Case 5 (start-from mapping): `--start-from post_processing --input img.png` maps to PipelineStage.POST_PROCESSING
- Case 6 (no-remove-bg): `--no-remove-bg` sets remove_background=False
- Case 7 (output-dir and asset-name): Custom output dir and asset name are passed through

## Status
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
