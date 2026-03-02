# Step 3 - Write Failing Test

## Failing Tests Created

- FR-1: Workflow Template Parameter Optimization - `docs/scenario/workflow_template_params.md` - `tests/scenario/test_workflow_template_params.py`
- FR-2: Dynamic Prompt Injection with Pixel-Art Prefix - `docs/scenario/dynamic_prompt_injection.md` - `tests/scenario/test_dynamic_prompt_injection.py`

All 6 new tests fail as expected (RED). 1 test (no_prompt_keeps_template_default) passes because template text stays as-is when prompt is None — this is expected once the template placeholder is in place, but currently it passes because the current code also doesn't change text when prompt is None. The test for that case still validates the new `{prompt}` placeholder value, which will be covered by the template update.
