# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Scan output directory for existing artifacts
ArtifactDetector must scan `output/images/` and `output/assets/` directories to identify existing pipeline artifacts. Files matching `*pixelized*` pattern belong to PIXELIZATION stage, other image files belong to IMAGE stage, and files in `output/assets/` belong to POST_PROCESSING stage.

### FR-2: Detect recommended start stage
`detect_start_stage` method must return a tuple of `(PipelineStage, Optional[Path])` representing the recommended NEXT stage and the path to the latest relevant artifact. When multiple artifacts exist in the same stage, the latest file by modification time is chosen.

### FR-3: Handle empty/missing directories
When no artifacts exist (empty directories or missing directories), `detect_start_stage` returns `(PipelineStage.PROMPT, None)`. When only final assets exist (nothing to skip to), also returns `(PipelineStage.PROMPT, None)`.

## Assumptions

- Image file extensions include common formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`.
- The `*pixelized*` pattern is case-insensitive matching on the filename (stem).
- "Latest file" is determined by filesystem modification time (`os.path.getmtime` or `Path.stat().st_mtime`).
- The detector takes the output directory path as a constructor parameter.
- When pixelized images exist, we recommend POST_PROCESSING as the next stage (with the pixelized image path).
- When non-pixelized images exist (but no pixelized ones), we recommend PIXELIZATION as the next stage (with the image path).
- When only assets exist, there's nothing useful to skip to, so we return PROMPT.
