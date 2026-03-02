# Scenario: Pipeline resolves palette_preset before quantization
- Given: PostProcessingPipeline with a valid image
- When: process() is called with palette_preset='sweetie-16'
- Then: PaletteLoader.get_preset('sweetie-16') is called and its result is passed to ColorQuantizer.quantize()

## Test Steps

- Case 1 (happy path): Pipeline resolves preset and passes palette to quantizer
- Case 2 (happy path): PostProcessingOutput.palette_name equals the preset name
- Case 3 (edge case): Pipeline still works with palette_path (unchanged behavior)
- Case 4 (edge case): Pipeline skips quantization when neither preset/path/count set

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [ ] Refactor implementation without breaking test
- [ ] Run test and confirm still passing after refactor
