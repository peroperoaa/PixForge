import pytest
import tempfile
import os

from src.modules.post_processing.palette_loader import PaletteLoader


class TestLoadFromHexFile:
    """Tests for PaletteLoader.load_from_hex_file (FR-1)."""

    def test_parses_valid_hex_colors(self, tmp_path):
        """load_from_hex_file parses '0f380f\\n306230\\n8bac0f\\n9bbc0f' into 4 correct RGB tuples."""
        hex_file = tmp_path / "test.hex"
        hex_file.write_text("0f380f\n306230\n8bac0f\n9bbc0f\n")

        result = PaletteLoader.load_from_hex_file(str(hex_file))

        assert len(result) == 4
        assert result[0] == (0x0F, 0x38, 0x0F)
        assert result[1] == (0x30, 0x62, 0x30)
        assert result[2] == (0x8B, 0xAC, 0x0F)
        assert result[3] == (0x9B, 0xBC, 0x0F)

    def test_ignores_empty_lines_and_comments(self, tmp_path):
        """load_from_hex_file ignores empty lines and lines starting with '#' (comments)."""
        hex_file = tmp_path / "test.hex"
        hex_file.write_text("# This is a comment\n\n0f380f\n\n# Another comment\n306230\n8bac0f\n\n")

        result = PaletteLoader.load_from_hex_file(str(hex_file))

        assert len(result) == 3
        assert result[0] == (0x0F, 0x38, 0x0F)
        assert result[1] == (0x30, 0x62, 0x30)
        assert result[2] == (0x8B, 0xAC, 0x0F)

    def test_raises_for_invalid_hex_characters(self, tmp_path):
        """load_from_hex_file raises ValueError for hex string with invalid characters like 'ZZZZZZ'."""
        hex_file = tmp_path / "test.hex"
        hex_file.write_text("FF5733\nZZZZZZ\n00FF00\n")

        with pytest.raises(ValueError, match="[Ii]nvalid"):
            PaletteLoader.load_from_hex_file(str(hex_file))

    def test_raises_for_fewer_than_two_colors(self, tmp_path):
        """load_from_hex_file raises ValueError when file contains fewer than 2 valid colors."""
        hex_file = tmp_path / "test.hex"
        hex_file.write_text("FF5733\n")

        with pytest.raises(ValueError, match="at least 2"):
            PaletteLoader.load_from_hex_file(str(hex_file))

    def test_raises_for_empty_file(self, tmp_path):
        """load_from_hex_file raises ValueError for empty file (0 colors)."""
        hex_file = tmp_path / "test.hex"
        hex_file.write_text("")

        with pytest.raises(ValueError, match="at least 2"):
            PaletteLoader.load_from_hex_file(str(hex_file))


class TestBuiltInPresets:
    """Tests for built-in palette presets (FR-2)."""

    def test_gb_preset_has_4_colors(self):
        """get_preset('gb') returns exactly 4 RGB tuples matching Game Boy green palette."""
        palette = PaletteLoader.get_preset("gb")
        assert len(palette) == 4
        # Game Boy classic green palette
        assert palette[0] == (0x0F, 0x38, 0x0F)
        assert palette[1] == (0x30, 0x62, 0x30)
        assert palette[2] == (0x8B, 0xAC, 0x0F)
        assert palette[3] == (0x9B, 0xBC, 0x0F)

    def test_sweetie16_preset_has_16_colors(self):
        """get_preset('sweetie-16') returns exactly 16 RGB tuples."""
        palette = PaletteLoader.get_preset("sweetie-16")
        assert len(palette) == 16

    def test_all_presets_have_valid_rgb_range(self):
        """All built-in preset colors have R, G, B values in range 0-255."""
        for preset_name in ["gb", "nes", "sweetie-16"]:
            palette = PaletteLoader.get_preset(preset_name)
            for i, (r, g, b) in enumerate(palette):
                assert 0 <= r <= 255, f"Preset '{preset_name}' color {i}: R={r} out of range"
                assert 0 <= g <= 255, f"Preset '{preset_name}' color {i}: G={g} out of range"
                assert 0 <= b <= 255, f"Preset '{preset_name}' color {i}: B={b} out of range"

    def test_nes_preset_has_54_colors(self):
        """NES preset returns 54 colors."""
        palette = PaletteLoader.get_preset("nes")
        assert len(palette) == 54


class TestGetPreset:
    """Tests for PaletteLoader.get_preset (FR-3)."""

    def test_get_preset_returns_palette(self):
        """get_preset('gb') returns the GB palette."""
        palette = PaletteLoader.get_preset("gb")
        assert isinstance(palette, list)
        assert all(isinstance(c, tuple) and len(c) == 3 for c in palette)

    def test_get_preset_case_insensitive(self):
        """get_preset is case-insensitive."""
        palette_lower = PaletteLoader.get_preset("gb")
        palette_upper = PaletteLoader.get_preset("GB")
        assert palette_lower == palette_upper

    def test_get_preset_unknown_raises_valueerror(self):
        """get_preset('nonexistent') raises ValueError with descriptive message."""
        with pytest.raises(ValueError, match="[Uu]nknown.*preset"):
            PaletteLoader.get_preset("nonexistent")
