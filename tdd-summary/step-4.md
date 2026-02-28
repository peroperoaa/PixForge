# Step 4 - Implement

## Implementation Details

### `src/core/config.py`

- Implemented `ConfigManager` class with priority logic:
    1. Runtime Arguments (`self.runtime_config`)
    2. File Configuration (`self._file_config` from `config.json`)
    3. Environment Variables (`os.environ`)

- `__init__` loads `.env` using `load_dotenv` and then attempts to read `config.json` via `_load_config()`.
- `_get_value(key, env_key)` implements the priority checking.
- `get_api_key()` raises `ValueError` if key is missing.
- `get_model()` defaults to returning a value or falling back to environment, currently returns what's found.

## Verification

- Tests pass successfully.
- Requirements for priority handling are met.
