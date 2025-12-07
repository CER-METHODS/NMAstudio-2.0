# NMAstudio Web Application

## About

NMAstudio is an interactive web application to produce and visualize network meta-analyses. It provides:

- Interactive network graphs
- Forest plots (NMA, pairwise, bidimensional)
- League tables with RoB/CINeMA coloring
- Ranking plots (P-scores)
- Consistency and transitivity assessment
- Funnel plots
- Knowledge Translation (SKT) module for clinicians

The app is deployed at: **www.nmastudioapp.com**

## Requirements

- Python 3.11+
- R with `netmeta`, `dplyr`, `metafor` packages
- Conda (recommended) or pip

## Local Development

### 1. Clone and setup environment

```bash
git clone <repository-url>
cd NMAstudio-app

# Create conda environment
conda env create -f requirements.yml
conda activate nmastudio

# Install R dependencies
Rscript init.R
```

### 2. Configure environment (optional)

Create a `.env` file:
```bash
DEBUG_MODE=True
AG_GRID_KEY=your-ag-grid-license-key
```

### 3. Run the app

```bash
python app.py
```

Open browser at: **http://localhost:8050**

## Testing

```bash
python tests/test_homepage_console_errors.py
```

## Project Structure

```
NMAstudio-app/
  app.py              # Main application entry
  pages/              # Dash pages (homepage, setup, results, knowledge_translation)
  tools/              # Core functions and SKT module
  assets/             # CSS, JS, storage schemas
  R_Codes/            # R functions for NMA
  tests/              # Playwright tests
  docs/               # Developer documentation
```

## Documentation

- [SKT Developer Guide](docs/SKT_DEVELOPER_GUIDE.md) - Knowledge Translation module
- [Refactoring Changelog](docs/CHANGELOG_REFACTORING.md) - Architecture changes

## Deployment

See `HEROKU INSTRUCTIONS` for Heroku deployment.

## License

See [LICENSE.txt](LICENSE.txt)
