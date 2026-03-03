# Scenario: No Quantization When Palette and Colors Are Both None

- Given: A `PostProcessingInput` with `palette_preset=None`, `palette_path=None`, `color_count=None`
- When: `PostProcessingPipeline.process()` is called
- Then: The color quantizer is never invoked and the output has `palette_name=None`

## Test Steps

- Case 1 (happy path): Process with all palette/color fields `None` — quantizer not called, output images saved
- Case 2 (explicit palette works): Process with `palette_preset='sweetie-16'` — quantizer IS called
- Case 3 (explicit color_count works): Process with `color_count=8` — quantizer IS called
- Case 4 (output metadata): When no quantization, output `palette_name` is `None` and `color_count` is `None`

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
