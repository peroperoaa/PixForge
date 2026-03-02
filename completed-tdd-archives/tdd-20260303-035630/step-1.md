# Step 1 - Understand Intent

## Functional Requirements

### FR-1: Pixel-Art-Optimized System Instruction
Update the `GeminiAdapter._construct_request` system_instruction to constrain generated prompts for pixel-art-friendly compositions. The system instruction must mention: centered subject, simple/transparent background, clear outlines, front or 3/4 view, and limited detail suitable for pixel art.

### FR-2: PromptOutput style_parameters Schema Documentation for Pixel Art
Update the `PromptOutput.style_parameters` field description/documentation to include pixel-art constraint guidance (e.g., expected keys like `view_angle`, `background_type`, `outline_style`).

### FR-3: Unit Tests Verify New System Instruction Content
Update existing unit tests to verify the new system instruction contains pixel-art-specific keywords: 'centered', 'simple background' or 'transparent background', 'clear outlines', 'front view' or '3/4 view'.

## Assumptions

- We are updating the existing system_instruction string in `GeminiAdapter._construct_request`, not adding a new method.
- The pixel-art constraints are additive guidance within the system instruction—the model still generates positive_prompt, negative_prompt, and style_parameters in JSON.
- "Generated PromptOutput.positive_prompt includes pixel-art-friendly directives" means the system instruction instructs the model to embed such directives in the positive_prompt output, not that we hardcode them in code.
- Existing tests that check for `"You are an expert prompt engineer"` will need updating to match the new instruction text.
