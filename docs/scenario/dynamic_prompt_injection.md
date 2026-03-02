# Scenario: Dynamic Prompt Injection with Pixel-Art Prefix
- Given: A ComfyUIAdapter with a loaded workflow template
- When: _build_workflow is called with a prompt string
- Then: The positive text node text is set to 'pixel art, clean edges, limited palette, ' + the upstream prompt

## Test Steps

- Case 1 (happy path): When prompt is provided, positive text node has pixel-art prefix + prompt
- Case 2 (edge case): When prompt is None, template text remains unchanged
- Case 3 (edge case): When prompt is empty string, prefix is still prepended

## Status
- [x] Write scenario document
- [x] Write solid test according to document
- [x] Run test and watch it failing
- [x] Implement to make test pass
- [x] Run test and confirm it passed
- [x] Refactor implementation without breaking test
- [x] Run test and confirm still passing after refactor
