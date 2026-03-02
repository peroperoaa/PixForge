"""Palette loader for parsing .hex palette files and providing built-in presets."""

from typing import List, Tuple


# Type alias for a palette: list of (R, G, B) tuples
Palette = List[Tuple[int, int, int]]


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert a 6-character hex string to an (R, G, B) tuple.

    Raises:
        ValueError: If the hex string contains invalid characters or is not 6 chars.
    """
    hex_str = hex_str.strip()
    if len(hex_str) != 6:
        raise ValueError(
            f"Invalid hex color '{hex_str}': expected 6 characters, got {len(hex_str)}"
        )
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color '{hex_str}': contains non-hex characters")
    return (r, g, b)


# Built-in palette presets
_PRESETS: dict[str, Palette] = {
    "gb": [
        (0x0F, 0x38, 0x0F),
        (0x30, 0x62, 0x30),
        (0x8B, 0xAC, 0x0F),
        (0x9B, 0xBC, 0x0F),
    ],
    "nes": [
        (0x00, 0x00, 0x00),
        (0xFC, 0xFC, 0xFC),
        (0xF8, 0xF8, 0xF8),
        (0xBC, 0xBC, 0xBC),
        (0x7C, 0x7C, 0x7C),
        (0xA4, 0x00, 0x00),
        (0xFC, 0x00, 0x00),
        (0xFC, 0x74, 0x60),
        (0xFC, 0xBC, 0xB0),
        (0xA4, 0x40, 0x00),
        (0xFC, 0x88, 0x00),
        (0xFC, 0xA0, 0x44),
        (0xFC, 0xD8, 0xA8),
        (0xA4, 0x64, 0x00),
        (0xFC, 0xBC, 0x00),
        (0xFC, 0xD0, 0x00),
        (0xFC, 0xE4, 0xA0),
        (0x04, 0x78, 0x00),
        (0x00, 0xBC, 0x00),
        (0x58, 0xD8, 0x54),
        (0xD4, 0xFC, 0xA0),
        (0x00, 0x64, 0x00),
        (0x00, 0xA8, 0x00),
        (0x00, 0xA8, 0x44),
        (0xB8, 0xF8, 0xB8),
        (0x00, 0x50, 0x78),
        (0x00, 0x88, 0x88),
        (0x00, 0xA8, 0x84),
        (0xB8, 0xF8, 0xD8),
        (0x00, 0x48, 0x78),
        (0x00, 0x78, 0xF8),
        (0x34, 0x98, 0xFC),
        (0xA4, 0xE4, 0xFC),
        (0x00, 0x00, 0xA4),
        (0x00, 0x00, 0xFC),
        (0x68, 0x88, 0xFC),
        (0xB8, 0xB8, 0xFC),
        (0x44, 0x00, 0x8C),
        (0x68, 0x44, 0xFC),
        (0x98, 0x78, 0xF8),
        (0xD8, 0xB8, 0xF8),
        (0xA4, 0x00, 0x6C),
        (0xD8, 0x00, 0xCC),
        (0xFC, 0x44, 0xFC),
        (0xF8, 0xB8, 0xF8),
        (0xA4, 0x00, 0x48),
        (0xE4, 0x00, 0x58),
        (0xFC, 0x78, 0x98),
        (0xFC, 0xBC, 0xBC),
        (0x58, 0x58, 0x58),
        (0xA4, 0xA4, 0xA4),
        (0x00, 0x00, 0x00),
        (0x08, 0x08, 0x08),
        (0xFC, 0xFC, 0xFC),
    ],
    "sweetie-16": [
        (0x1A, 0x1C, 0x2C),
        (0x5D, 0x27, 0x5D),
        (0xB1, 0x3E, 0x53),
        (0xEF, 0x7D, 0x57),
        (0xFF, 0xCD, 0x75),
        (0xA7, 0xF0, 0x70),
        (0x38, 0xB7, 0x64),
        (0x25, 0x71, 0x79),
        (0x29, 0x36, 0x6F),
        (0x3B, 0x5D, 0xC9),
        (0x41, 0xA6, 0xF6),
        (0x73, 0xEF, 0xF7),
        (0xF4, 0xF4, 0xF4),
        (0x94, 0xB0, 0xC2),
        (0x56, 0x6C, 0x86),
        (0x33, 0x3C, 0x57),
    ],
}


class PaletteLoader:
    """Loads color palettes from .hex files and provides built-in presets."""

    @staticmethod
    def load_from_hex_file(file_path: str) -> Palette:
        """Parse a Lospec .hex palette file into a list of (R, G, B) tuples.

        The .hex format has one 6-character hex color code per line.
        Empty lines and lines starting with '#' (comments) are ignored.

        Args:
            file_path: Path to the .hex palette file.

        Returns:
            List of (R, G, B) tuples.

        Raises:
            ValueError: If the file contains invalid hex strings or fewer than 2 colors.
            FileNotFoundError: If the file does not exist.
        """
        with open(file_path, "r") as f:
            lines = f.readlines()

        colors: Palette = []
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                color = _hex_to_rgb(stripped)
            except ValueError:
                raise ValueError(
                    f"Invalid hex color '{stripped}' on line {line_num}"
                )
            colors.append(color)

        if len(colors) < 2:
            raise ValueError(
                f"Palette must contain at least 2 colors, got {len(colors)}"
            )

        return colors

    @staticmethod
    def get_preset(name: str) -> Palette:
        """Get a built-in palette preset by name.

        Args:
            name: Preset name (case-insensitive). Available: 'gb', 'nes', 'sweetie-16'.

        Returns:
            List of (R, G, B) tuples for the preset palette.

        Raises:
            ValueError: If the preset name is not recognized.
        """
        key = name.lower()
        if key not in _PRESETS:
            available = ", ".join(sorted(_PRESETS.keys()))
            raise ValueError(
                f"Unknown preset '{name}'. Available presets: {available}"
            )
        return list(_PRESETS[key])
