# Pixel Art Generation Pipeline

A complete pipeline to generate pixel art assets from text prompts using AI image generation, pixelization, and post-processing techniques.

## Setup

1.  **Prerequisites**:
    *   Python 3.10+
    *   [ComfyUI](https://github.com/comfyanonymous/ComfyUI) installed and running locally (default port 8188).

2.  **Installation**:
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit `.env` and set your API keys (e.g., `GEMINI_API_KEY`).

## Usage

The project provides a command-line interface (CLI) via `main.py`.

### Basic Usage

Generate a pixel art asset from a text prompt:

```bash
python main.py --prompt "a pixel art sword with glowing runes"
```

### Command Line Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--prompt` | Text prompt for image generation. Required when starting from the beginning. | `None` |
| `--input` | Path to an input image. Required when starting from `image`, `pixelization`, or `post_processing` stages. | `None` |
| `--start-from` | Pipeline stage to start from: `prompt`, `image`, `pixelization`, `post_processing`. | `prompt` |
| `--aspect-ratio` | Aspect ratio for generation (e.g., `1:1`, `16:9`). | `1:1` |
| `--palette` | Color palette preset (`sweetie-16`, `gb`, `nes`) or path to a `.hex` file. | `sweetie-16` |
| `--colors` | Number of colors for K-Means quantization (overrides `--palette`). | `None` |
| `--sizes` | Comma-separated target asset sizes in pixels (e.g., `32,64`). | `32,64` |
| `--no-remove-bg` | Disable automatic background removal. | `False` |
| `--asset-name` | Base name for output files (defaults to sanitized prompt). | `None` |
| `--output-dir` | Directory to save outputs. | `output` |
| `--auto-detect` | Auto-detect existing artifacts in `output/` and resume from the latest stage. | `False` |

### Examples

**1. Customizing Output Size and Palette**

Generate a "fire potion" using the GameBoy palette, outputting 32x32 and 128x128 versions:

```bash
python main.py --prompt "fire potion" --palette gb --sizes 32,128
```

**2. Using K-Means Color Quantization**

Generate a "golden coin" using 8 extracted colors instead of a fixed palette:

```bash
python main.py --prompt "golden coin" --colors 8
```

**3. Resume from a Specific Stage**

If you have an intermediate image (e.g., `output/images/gen_001.png`) and want to re-run pixelization and post-processing:

```bash
python main.py --input output/images/gen_001.png --start-from pixelization
```

**4. Auto-Resume**

Automatically detect the latest generated file in the output directory and continue the pipeline:

```bash
python main.py --auto-detect
```

## Outputs

*   **`output/assets/`**: Final processed pixel art assets (transparent PNGs).
    *   Naming: `{asset_name}_{size}x{size}.png`
*   **`output/images/`**: Intermediate image files (original generation, pixelized versions).
