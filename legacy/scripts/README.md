# Legacy Route Migration Scripts

Scripts to extract Flask routes and generate FastAPI contract-first routers.

## Prerequisites

To run these scripts, you need:

1. **Flask app dependencies installed**:
   - The legacy Flask service and its dependencies must be available
   - This typically requires the `fundbox-common` and other internal packages

2. **Environment variables** (minimal values for route extraction):
   ```bash
   export API_FLASK_SESSION_SECRET_KEY=dummy-secret-for-route-export
   export API_OAUTH_ENFORCE_SSL=false
   export API_SQLALCHEMY_DATABASE_URI=sqlite:///:memory:
   ```

3. **Python path**:
   - The script automatically adds `api__backup_20260114_1349/src` to `sys.path`
   - Or ensure Flask app is importable from your Python environment

## Usage

### 1. Export Flask Routes

```bash
python legacy/scripts/export_routes.py
```

**Outputs**:
- `artifacts/flask_routes.json` - Machine-readable route inventory
- `artifacts/flask_routes.txt` - Human-readable route table

**What it does**:
- Imports Flask app from legacy service
- Extracts all routes from `app.url_map`
- Excludes HEAD/OPTIONS unless explicitly defined
- Extracts blueprint names, docstrings, and endpoint names

### 2. Generate FastAPI Routers

```bash
python legacy/scripts/generate_fastapi_routers.py
```

**Outputs**:
- `src/gateway/routers/legacy/*.py` - Generated router modules
- `src/gateway/routers/legacy/__init__.py` - Module exports

**What it does**:
- Reads `artifacts/flask_routes.json`
- Groups routes by blueprint or path segment
- Generates FastAPI router modules with proxy handlers
- Skips routes that collide with gateway endpoints
- Normalizes Flask path syntax to FastAPI format

### 3. Wire Routers into Gateway

```bash
python legacy/scripts/wire_routers.py
```

**What it does**:
- Updates `src/gateway/main.py` to include all legacy routers
- Inserts router includes before the catch-all proxy router
- Ensures proper route ordering

## Troubleshooting

### "No module named 'fundbox'"

The Flask app requires internal `fundbox` packages. Options:

1. **Install dependencies**: Ensure `fundbox-common` and other required packages are installed
2. **Use proper environment**: Run in an environment where Flask app dependencies are available
3. **Mock mode** (for testing): Modify export script to use a minimal Flask app for demonstration

### "Failed to import Flask app"

Check:
- `api__backup_20260114_1349/src/` exists and is accessible
- `Core.py` and `App.py` are present in that directory
- Required environment variables are set (even dummy values)

### Routes Not Generated

- Check `artifacts/flask_routes.json` exists and is valid JSON
- Verify routes were exported successfully
- Check for error messages during generation

## Script Details

### export_routes.py

- **Purpose**: Extract routes from Flask `url_map` at runtime
- **Dependencies**: Flask app must be importable
- **Output**: JSON and text inventory files

### generate_fastapi_routers.py

- **Purpose**: Generate FastAPI router code from route inventory
- **Dependencies**: None (pure code generation)
- **Output**: Python router modules

### wire_routers.py

- **Purpose**: Automatically wire generated routers into main.py
- **Dependencies**: Generated routers must exist
- **Output**: Modified `src/gateway/main.py`

## Manual Alternative

If scripts can't run due to missing dependencies, you can:

1. **Manually inspect Flask routes**:
   - Start Flask app in debug mode
   - Access `app.url_map` in Python shell
   - Export routes manually

2. **Manually create routers**:
   - Follow the pattern in `src/gateway/routers/legacy/*.py`
   - Use `proxy_to_upstream()` for handlers
   - Group by blueprint or path segment

3. **Manually wire routers**:
   - Import routers in `src/gateway/main.py`
   - Include before proxy router
