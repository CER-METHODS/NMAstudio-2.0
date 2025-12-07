# NMAstudio Development Guide

## Commands

### Development
```bash
# Start development server
python app.py

# Install dependencies (conda)
conda env create -f requirements.yml
conda activate nmastudio

# Install R dependencies
Rscript init.R

# Type checking
pyright
```

### Testing
```bash
# Run single test
python tests/test_homepage_console_errors.py
```

## Code Style

### Python
- **Imports**: Absolute from project root (`from tools.utils import *`)
- **Functions**: `snake_case`, `__double_underscore` for internal
- **Constants**: `UPPER_CASE`
- **Error handling**: Try-except with specific exceptions, avoid bare except

### Dash Components
- **Component IDs**: Descriptive with `_STORAGE` suffix for dcc.Store
- **Styling**: Use CSS classes from assets/, avoid inline styles
- **Callbacks**: Use `@callback` decorator, specify Input/Output types
- **Docs**: Get via MCP: `MCP_DOCKER_get-library-docs --context7CompatibleLibraryID '/plotly/dash'`

### SKT Module
- Keep SKT functions in `functions_skt_*.py` files, not in main `functions_*.py`
- SKT storage variables use `_SKT` suffix
- See `docs/SKT_DEVELOPER_GUIDE.md` for architecture details

### Testing
- Do not write tests unless asked directly
- Use Playwright MCP for browser automation
- Server must be running on localhost:8050

## Project Structure

```
NMAstudio-app/
  app.py                 # App initialization (use_pages=True)
  pages/                 # Dash pages
    homepage.py          # Landing page (/)
    setup.py             # Data upload & analysis (/setup)
    results.py           # Visualizations (/results)
    knowledge_translation.py  # SKT module (/knowledge-translation)
  tools/                 # Core functionality
    skt_*.py             # SKT module components
    functions_*.py       # Visualization functions
    utils.py             # Shared utilities
  assets/                # CSS, JS, storage schemas
    storage.py           # Main STORAGE schema
    skt_storage.py       # SKT-specific storage
  R_Codes/               # R functions (netmeta)
  db/                    # Sample datasets
  tests/                 # Playwright tests
  docs/                  # Developer documentation
```

## Key Files

| File | Purpose |
|------|---------|
| `assets/storage.py` | STORAGE schema and dcc.Store components |
| `assets/skt_storage.py` | SKT-specific storage |
| `tools/skt_layout.py` | SKT page UI components |
| `tools/skt_data_helpers.py` | Extract data from STORAGE for SKT |
| `docs/SKT_DEVELOPER_GUIDE.md` | SKT architecture and patterns |
| `docs/CHANGELOG_REFACTORING.md` | Architecture changes from main version |

## Laws

- ALWAYS check NMAstudio-app-main before editing a function
- NEVER edit NMAstudio-app-main
- Get library docs from MCP context7 when needed
- Keep STORAGE schema consistent in localStorage
