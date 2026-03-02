# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Sequential Stage Execution
FullPipeline.run executes stages PROMPT → IMAGE → PIXELIZATION → POST_PROCESSING in order when start_stage=PROMPT, chaining each stage's output into the next stage's input.

### FR-2: Stage Skipping
Pipeline skips stages before start_stage when given an explicit start point (e.g., start_stage=PIXELIZATION skips PROMPT and IMAGE).

### FR-3: Auto-Detect Mode
Pipeline uses ArtifactDetector when start_stage is None to determine the entry point and artifact path.

### FR-4: Stage Output Chaining
prompt_output.positive_prompt feeds into image_gen input, image_output.image_path feeds into pixelization input, pixelization_output.image_path feeds into post_processing input.

### FR-5: Stage Timing and Results
Each executed stage records a StageResult with timing data (duration_seconds), and FullPipelineResult contains all stage results plus total_duration_seconds.

### FR-6: Error Handling and Abort
Stage failures are caught, recorded in StageResult with error_message and success=False, and remaining stages are aborted.

### FR-7: Dependency Injection
FullPipeline accepts four module adapters (BasePromptGenerator, BaseImageGenerator, BasePixelization, BasePostProcessor) via constructor for testability.

## Assumptions

- start_stage=None in FullPipelineConfig triggers auto-detect mode. The schema needs to be updated to make start_stage Optional.
- When auto-detect resolves to a stage > PROMPT, the detected artifact_path is used as input_image_path.
- asset_name defaults to "output" if not specified in config.
- output_dir defaults to ConfigManager.get_post_processing_output_dir() if not specified.
- The orchestrator does not retry failed stages — it aborts immediately on first failure.
