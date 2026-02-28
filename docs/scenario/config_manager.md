# Scenario: ConfigManager Priority and Retrieval

## Scenario 1: ConfigManager correctly prioritizes sources (Runtime > File > Env)
- Given:
    - Runtime args: `{'api_key': 'runtime_key'}`
    - File config (`config.json`): `{'api_key': 'file_key', 'model': 'file_model'}`
    - Env vars: `API_KEY=env_key`, `MODEL=env_model`
- When: `ConfigManager` is initialized with runtime args and loads config.
- Then:
    - `get_api_key()` returns `'runtime_key'`.
    - `get_model()` returns `'file_model'`.

## Scenario 2: ConfigManager raises error when API key is missing
- Given:
    - No runtime args.
    - No file config.
    - No environment variables.
- When: `ConfigManager` is initialized.
- Then: `get_api_key()` raises a `ValueError` or `ConfigurationError`.

## Scenario 3: ConfigManager retrieves API key from Env if not in Runtime or File
- Given:
    - Runtime args: `{}`
    - File config: `{}`
    - Env vars: `API_KEY=env_key`
- When: `ConfigManager` is initialized.
- Then: `get_api_key()` returns `'env_key'`.

## Status
- [x] Write scenario document
- [ ] Write solid test according to document
- [ ] Run test and watch it failing
- [ ] Implement to make test pass
- [ ] Run test and confirm it passed
- [ ] Refactor implementation without breaking test
- [ ] Run test and confirm still passing after refactor
