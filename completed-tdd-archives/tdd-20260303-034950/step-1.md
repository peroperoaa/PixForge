# Step 1 - Understand Intent

## Functional Requirements

### FR-1: CLI Argument Parsing
Create `main.py` at project root with argparse-based ArgumentParser that defines all required arguments: `--prompt`, `--input`, `--start-from`, `--aspect-ratio`, `--palette`, `--colors`, `--sizes`, `--no-remove-bg`, `--asset-name`, `--output-dir`, `--auto-detect`. Arguments should have sensible defaults and proper validation.

### FR-2: Argument-to-Config Mapping
Map parsed CLI arguments to `FullPipelineConfig`. `--palette` detects `.hex` suffix to distinguish preset names from file paths. `--start-from` accepts case-insensitive stage names. `--colors` switches to K-Means mode. `--auto-detect` sets `start_stage=None`.

### FR-3: Pipeline Execution with Progress
Invoke the orchestrator and print stage-by-stage progress lines to stdout. Print final summary with output asset paths, total time, and any errors.

### FR-4: Error Handling and Exit Codes
Exit code 0 on success, 1 on pipeline error, 2 on argument error. Handle `KeyboardInterrupt` and unexpected exceptions gracefully.

## Assumptions

- The CLI will construct real adapters (GeminiAdapter, GeminiImageAdapter, ComfyUIAdapter, PostProcessingPipeline) when running for real, but all tests will mock FullPipeline.
- `--sizes` will accept comma-separated integers (e.g., `--sizes 32,64,128`).
- `--start-from` maps: `prompt` -> PROMPT, `image` -> IMAGE, `pixelization` -> PIXELIZATION, `post_processing` -> POST_PROCESSING.
- Progress messages go to stdout since the CLI is human-facing.
- When `--auto-detect` is used alongside `--start-from`, `--auto-detect` takes precedence.
