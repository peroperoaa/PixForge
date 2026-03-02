# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Add palette_preset field to PostProcessingInput
PostProcessingInput should accept an Optional[str] `palette_preset` field that names a built-in palette preset (e.g. 'sweetie-16').

### FR-2: Mutual exclusion of palette_preset and palette_path
If both `palette_preset` and `palette_path` are set simultaneously, PostProcessingInput must raise a ValueError via a model-level validator.

### FR-3: Pipeline resolves palette_preset before quantization
PostProcessingPipeline.process must resolve `palette_preset` via `PaletteLoader.get_preset()` to obtain the actual palette, then pass it to `ColorQuantizer.quantize()`.

### FR-4: PostProcessingOutput.palette_name reflects preset name
When `palette_preset` is used, `PostProcessingOutput.palette_name` should equal the preset name string (not a file path basename).

## Assumptions

- The `palette_preset` field accepts any string that `PaletteLoader.get_preset()` can resolve. Invalid preset names will raise ValueError at pipeline runtime, not at schema validation.
- When `palette_preset` is set, quantization is triggered even if `color_count` is None.
- The existing behavior for `palette_path` and `color_count` remains unchanged.
