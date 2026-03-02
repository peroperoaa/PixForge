# Step 1 - Understand Intent

## Functional Requirements

### FR-1: PipelineStage enum with ordering
PipelineStage enum must have exactly 4 members in execution order: PROMPT, IMAGE, PIXELIZATION, POST_PROCESSING. The enum must support ordering comparison operators (<, >, <=, >=).

### FR-2: FullPipelineConfig model with defaults and cross-field validation
FullPipelineConfig Pydantic model with fields: user_prompt, input_image_path, start_stage, aspect_ratio, palette_preset, color_count, target_sizes, remove_background, asset_name, output_dir. Default values: start_stage=PROMPT, palette_preset='sweetie-16', target_sizes=[32,64], remove_background=True. Cross-field validators: user_prompt required when start_stage=PROMPT; input_image_path required when start_stage > PROMPT (IMAGE, PIXELIZATION, POST_PROCESSING).

### FR-3: StageResult model
StageResult Pydantic model with fields: stage (PipelineStage), success (bool), output_path (Optional[str]), error_message (Optional[str]), duration_seconds (float).

### FR-4: FullPipelineResult model
FullPipelineResult Pydantic model with fields: stage_results (list[StageResult]), final_asset_paths (list[str]), total_duration_seconds (float).

## Assumptions

- PipelineStage enum uses IntEnum (or similar) to support natural ordering via integer values.
- user_prompt is Optional[str] with default None; required only when start_stage == PROMPT.
- input_image_path is Optional[str] with default None; required only when start_stage > PROMPT.
- aspect_ratio defaults to "1:1" following ImageGenInput pattern.
- color_count is Optional[int] with default None.
- asset_name and output_dir are Optional[str] with default None.
