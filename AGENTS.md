# NMAstudio Development Guide

## Commands

### Testing
```bash
# Run all tests
python run_tests.py

# Run single test file
python tests/test_homepage_console_errors.py

# Run specific test with Playwright
python tests/test_setuppage_console_errors.py
```

### Development
```bash
# Start development server
python app.py

# Install dependencies (conda)
conda env create -f requirements.yml
conda activate nmastudio

# Install R dependencies
Rscript init.R
```

### Type Checking
```bash
# Run pyright type checker
pyright
```

## Code Style Guidelines

### Python Code
- **Imports**: Use absolute imports from project root (e.g., `from tools.utils import *`)
- **Function naming**: Use snake_case for functions, double underscore prefix for internal functions (e.g., `__modal_submit_checks`)
- **Variable naming**: Use descriptive names, avoid single letters except in loops
- **Error handling**: Use try-except blocks with specific error handling, avoid bare except
- **Dash callbacks**: Use descriptive callback function names, group related callbacks

### Dash/Frontend
- **Component IDs**: Use descriptive IDs with STORAGE suffix for dcc.Store components
- **Styling**: Use CSS classes from assets/, avoid inline styles when possible
- **Callbacks**: Always specify Input/Output types, use suppress_callback_exceptions=True
- **Documentation**: Get Dash 2.18.2 docs via MCP: `MCP_DOCKER_get-library-docs --context7CompatibleLibraryID '/plotly/dash' --topic 'callbacks'`

### Testing
- Do not write tests unless asked directly instead use the Playwright MCP
- **Test files**: Prefix with `test_`, use async Playwright API
- **Test structure**: Check console errors, page functionality, and data loading
- **Server requirement**: Tests expect server running on localhost:8050 or macas.lan:8050

### Project Structure
- **tools/**: Core functionality modules
- **assets/**: Static files (CSS, JS, images)
- **pages/**: Dash page components
- **db/**: Sample datasets
- **R_Codes/**: R statistical functions

### Refactoring goal
- we need to turn refactor the app from a single page to multipage by splitting functionality in @tools/layout.torevactor to separate pages in @pages folder
