# Step 3 - Write Tests

## Test Plan

### Unit Tests (`tests/core/test_config.py`)

- **Scenario 1: ConfigManager Priority**
    - Verify that settings are resolved in the order: Runtime > File > Environment.
    - Test `get_api_key` and `get_model`.

- **Scenario 2: Missing API Key**
    - Verify that `ValueError` is raised when API Key is missing from all sources.

- **Scenario 3: Environment Variable Fallback**
    - Verify that `get_api_key` retrieves from environment variables if not present in Runtime or File.

## Test Execution

- All tests implemented using `pytest` and `unittest.mock`.
- Tests cover the priority logic and error handling.
- `os.path.exists` and `builtins.open` are mocked to simulate file presence/absence.
- `os.environ` is patched to simulate environment variables.
