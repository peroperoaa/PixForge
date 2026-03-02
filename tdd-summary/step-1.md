# Step 1 - Understand Intent (Color Quantizer)

## Functional Requirements

### FR-1: Palette Loader - Load from .hex File
PaletteLoader.load_from_hex_file parses Lospec .hex palette files (one hex color per line, e.g. 'FF5733') into a list of (R, G, B) tuples. Empty lines and comment lines (starting with '#') are ignored. Invalid hex strings raise ValueError. Files with fewer than 2 valid colors raise ValueError.

### FR-2: Palette Loader - Built-in Presets
PaletteLoader provides a built-in presets dictionary containing classic palettes: GB (4 colors), NES (54 colors), and Sweetie-16 (16 colors). All preset colors have R, G, B values in range 0-255.

### FR-3: Palette Loader - Get Preset by Name
PaletteLoader.get_preset(name) returns a palette (list of RGB tuples) by preset name. Raises ValueError with a descriptive message for unknown preset names.

## Assumptions

- .hex file format: one 6-character hex color code per line (no '#' prefix on color lines)
- Lines starting with '#' are treated as comments and skipped
- Preset name lookup is case-insensitive (e.g. 'GB' and 'gb' both work)
- PaletteLoader is a class with static/class methods (no instance state needed)
