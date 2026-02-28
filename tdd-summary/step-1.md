# Step 1 - Understand Intent

## Functional Requirements

### FR-1: ConfigManager Initialization
- The `ConfigManager` should accept runtime arguments (e.g., a dictionary) during initialization.
- It should also support loading from a configuration file (e.g., `config.json`) and environment variables (`.env`).

### FR-2: Configuration Loading Priority
- Priority order: Runtime args > File (`config.json`) > Environment variables (`.env`).
- If a key exists in multiple sources, the value from the highest priority source is used.

### FR-3: Retrieve API Key
- Provide a method to retrieve the API Key.
- Raise a specific error if the API Key is not found in any source.

### FR-4: Retrieve Model
- Provide a method to retrieve the Model name.
- Default value can be handled if specified, but the prompt implies explicit retrieval.

## Assumptions

- `python-dotenv` is available for loading `.env` files.
- `config.json` is a standard JSON file.
- Runtime arguments are passed as a dictionary to the constructor.
