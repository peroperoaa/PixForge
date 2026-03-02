# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Workflow Template Parameter Optimization
Update workflow_api_template.json: set KSampler denoise to 0.32, ControlNet strength to 0.65. Replace the hardcoded positive prompt text with a generic placeholder. Update negative prompt to include anatomy-preserving terms ('deformed, bad anatomy, extra limbs, mutation').

### FR-2: Dynamic Prompt Injection with Pixel-Art Prefix
Update ComfyUIAdapter._build_workflow to always inject the upstream prompt into the positive text node with a pixel-art prefix: prepend 'pixel art, clean edges, limited palette, ' before the upstream prompt. When no prompt is supplied, the template default is used as-is.

### FR-3: Update Existing Tests for New Parameter Values
Update existing pixelization unit tests to reflect new denoise (0.32), ControlNet strength (0.65), negative prompt terms, and dynamic prompt prefix behavior.

## Assumptions

- The positive prompt node is node "2" (CLIPTextEncode) and the negative prompt node is node "5" (CLIPTextEncode) in the workflow template.
- The ControlNet strength is in node "10" (ControlNetApply).
- When a prompt is passed to _build_workflow, it should be prefixed. When prompt is None, the template text stays unchanged.
- The pixel-art prefix is exactly: 'pixel art, clean edges, limited palette, '
