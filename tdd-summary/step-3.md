# Step 3 - Write Failing Test

## Failing Tests Created

- FR-1: Palette Loader - Load from .hex File - `docs/scenario/palette_loader_hex.md` - `tests/modules/post_processing/test_palette_loader.py::TestLoadFromHexFile`
- FR-2: Palette Loader - Built-in Presets - `docs/scenario/palette_loader_presets.md` - `tests/modules/post_processing/test_palette_loader.py::TestBuiltInPresets`
- FR-3: Palette Loader - Get Preset by Name - `docs/scenario/palette_loader_get_preset.md` - `tests/modules/post_processing/test_palette_loader.py::TestGetPreset`

All 11 tests fail with ModuleNotFoundError (palette_loader module does not exist yet).
