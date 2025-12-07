# NMAstudio Refactoring Changelog

## Overview

This document details the architectural and functional changes made during the refactoring from **NMAstudio-app-main** (single-page application) to **NMAstudio-app** (multi-page application).

**Summary**: The application was transformed from a monolithic ~3000+ line `app.py` into a modular multi-page Dash application with separate concerns, persistent localStorage, comprehensive test coverage, and enhanced SKT (Knowledge Translation) module.

---

## Architecture Changes

### App Structure

| Aspect | NMAstudio-app-main | NMAstudio-app |
|--------|-------------------|---------------|
| **app.py size** | ~3133 lines | ~102 lines |
| **Routing** | Manual `dcc.Location` callback | Dash Pages (`use_pages=True`) |
| **Page registration** | `if/elif` in `display_page()` | `dash.register_page()` |
| **Callbacks** | All in app.py | Distributed in page files |
| **Navbar** | Per-page rendering | Global component |
| **Alert modals** | Inline | Centralized (`assets/alerts.py`) |

### Before (Single-Page)
```
NMAstudio-app-main/
  app.py                    # 3133 lines - ALL callbacks, routing, layouts
  tools/
    layouts.py              # Homepage, Results layouts
    layouts_KT.py           # SKT page layouts (908 lines)
    kt_table_advance.py     # Advanced AG Grid
    kt_table_standard.py    # Standard AG Grid
```

### After (Multi-Page)
```
NMAstudio-app/
  app.py                    # 102 lines - just initialization
  pages/
    homepage.py             # 528 lines - landing page
    setup.py                # 1848 lines - data upload & analysis
    results.py              # 2000+ lines - visualizations
    knowledge_translation.py # 788 lines - SKT callbacks
  tools/
    skt_layout.py           # SKT UI components
    skt_table.py            # AG Grid tables
    skt_data_helpers.py     # STORAGE data extraction
    functions_skt_*.py      # SKT visualizations
```

---

## Storage Architecture

### Session Management

| Aspect | Before | After |
|--------|--------|-------|
| **Storage type** | `memory` (lost on refresh) | `local` (localStorage persistence) |
| **Session handling** | Pickle files in `__TEMP_LOGS_AND_GLOBALS/` | Browser localStorage |
| **Data format** | Lists of JSON strings | Dicts with typed schema |

### Schema Evolution

**New storage variables added:**

| Variable | Type | Purpose |
|----------|------|---------|
| `nmastudio-version` | string | Schema version tracking ("2.0") |
| `results_ready_STORAGE` | boolean | Indicates if NMA analysis is complete |
| `number_outcomes_STORAGE` | integer | Count of outcomes (e.g., 3) |
| `outcome_names_STORAGE` | list | Outcome names (e.g., ["PASI90", "SAE"]) |
| `effect_modifiers_STORAGE` | list | Effect modifier column names |
| `R_errors_STORAGE` | dict | R execution errors for display |
| `project_title_STORAGE` | string | Project/study title |
| `protocol_link_STORAGE` | string | URL to study protocol |

**Storage format changes:**

```python
# Before (list-based)
raw_data_STORAGE = [RAW_DATA_JSON]
net_data_STORAGE = [NET_DATA_JSON]

# After (dict-based with metadata)
raw_data_STORAGE = {"data": RAW_DATA_JSON}
net_data_STORAGE = {
    "data": NET_DATA_JSON,
    "elements_out1": [...],  # Cytoscape elements
    "elements_out2": [...],
    "n_classes": 3           # RoB classes count
}
```

### SKT-Specific Storage (NEW)

Added `assets/skt_storage.py`:

```python
SKT_STORAGE_SCHEMA = {
    "treatment_fullnames_SKT": "dict",  # {"ADA": "Adalimumab", ...}
}
```

---

## Pages

### Homepage (`/` or `/home`)

**Status**: Enhanced

| Feature | Before | After |
|---------|--------|-------|
| Browser warning | Not present | Shows for non-Chrome users |
| Demo download | Present | Present |
| Tutorial link | Present | Present |
| Footer | Present | Enhanced with funding info |

### Setup Page (`/setup`)

**Status**: Major refactoring

| Feature | Before | After |
|---------|--------|-------|
| Project title input | Not present | Added with validation |
| Protocol link input | Not present | Added |
| Multi-outcome support | 2 outcomes max | Any number of outcomes |
| Data format detection | Manual | Automatic (long/contrast/iv) |
| Column mapping | Inline | Dynamic dropdowns |
| Effect modifiers | Not present | Optional selection |
| Demo loading | Hardcoded data | `psoriasisDemo.py` module |
| Save/Load project | Present | Enhanced with version tracking |
| Progress modal | Present | Centralized in `assets/modal_values.py` |

**New callbacks:**
- `update_skt_title_input()` - Sync title to SKT page
- `redirect_after_project_upload()` - Auto-navigate after load
- Project validation before save

### Results Page (`/results`)

**Status**: Refactored into separate file

| Feature | Before | After |
|---------|--------|-------|
| Network graph | Present | Enhanced with year slider |
| Forest plots | Present | Added bidimensional option |
| League table | Present | Multi-outcome support |
| Ranking plots | Present | Improved error handling |
| Consistency | Present | Present |
| Transitivity | Present | Effect modifier support |
| Funnel plots | Present | Present |

**Callback improvements:**
- All callbacks moved from `app.py` to `pages/results.py`
- Better error handling with `PreventUpdate`
- Debug logging throughout

### Knowledge Translation (`/knowledge-translation`)

**Status**: Major refactoring (NEW PAGE)

Previously embedded in main app, now a separate page with dedicated tools.

| Aspect | Before | After |
|--------|--------|-------|
| File location | `app.py` + `tools/layouts_KT.py` | `pages/knowledge_translation.py` |
| Layouts | `tools/layouts_KT.py` (908 lines) | `tools/skt_layout.py` (2000+ lines) |
| AG Grids | `kt_table_advance.py`, `kt_table_standard.py` | `tools/skt_table.py` |
| Data loading | CSV files | STORAGE extraction |
| Data helpers | None | `tools/skt_data_helpers.py` |

**New features:**
- Dynamic data loading from STORAGE (no hardcoded CSVs)
- Project title display from `project_title_STORAGE`
- Treatment fullname mapping (`treatment_fullnames_SKT`)
- Placeholder components for mode switching
- Yada tour assistant integration

---

## Tools Directory

### New Files

| File | Lines | Purpose |
|------|-------|---------|
| `skt_layout.py` | 2000+ | SKT page UI: `Sktpage()`, `skt_layout()`, `skt_nonexpert()` |
| `skt_table.py` | 433 | AG Grid components: `treat_compare_grid`, modal grids |
| `skt_data_helpers.py` | 667 | STORAGE data extraction functions |
| `functions_skt_ranking.py` | 96 | Separated SKT ranking heatmap |
| `functions_cinema.py` | 437 | CINeMA confidence validation |
| `yada.py` | 72 | Dash Yada tour assistant |
| `navbar.py` | New | Global navigation component |

### Modified Files

| File | Changes |
|------|---------|
| `utils.py` | +479 lines: pandas 2.0 compatibility, thread-safe R, STORAGE helpers |
| `functions_ranking_plots.py` | SKT function moved to `functions_skt_ranking.py`, better error handling |
| `functions_skt_others.py` | `__generate_skt_stylesheet()` signature expanded (4 -> 10 params) |
| `PATHS.py` | Deprecated server-side sessions, kept for compatibility |

### Removed Files

| File | Status |
|------|--------|
| `layouts.py` | Refactored into `pages/` |
| `layouts_KT.py` | Refactored into `tools/skt_*.py` |
| `kt_table_advance.py` | Merged into `skt_layout.py` |
| `kt_table_standard.py` | Merged into `skt_table.py` |

---

## Assets

### New Files

| File | Purpose |
|------|---------|
| `browser-warning.js` | Non-Chrome browser warning |
| `clientside.js` | Clientside callbacks |
| `skt_storage.py` | SKT-specific dcc.Store components |
| `psoriasisDemo.py` | Demo data lazy loading |
| `psoriasisDemo3outcomes.py` | 3-outcome demo data |

### Modified Files

| File | Changes |
|------|---------|
| `storage.py` | New schema, helper functions, version tracking |
| `alerts.py` | Centralized alert modals |
| `modal_values.py` | Analysis progress modal |
| `style.css` | Yada assistant styles, SKT styles |

---

## Testing Infrastructure (NEW)

**Before**: No automated tests

**After**: 6 Playwright tests covering core functionality

### Test Coverage

| Test File | Purpose |
|-----------|---------|
| `test_homepage_console_errors.py` | Homepage loads without JS errors |
| `test_setuppage_console_errors.py` | Setup page loads without JS errors |
| `test_create_3outcomes_project.py` | Project creation workflow with 3 outcomes |
| `test_upload_and_run_analysis.py` | Full CSV upload + R analysis pipeline |
| `test_knowledge_translation_page.py` | SKT page functionality |
| `test_wide_format_2outcomes.py` | Wide format data support |

### Running Tests

```bash
python tests/test_homepage_console_errors.py  # Individual test
```

---

## Configuration

### Environment Variables (NEW)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG_MODE` | `False` | Enable Dash debug mode |
| `AG_GRID_KEY` | `""` | AG Grid Enterprise license |

### `.env` Support

```python
# app.py
from dotenv import load_dotenv
load_dotenv()
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
```

---

## Documentation (NEW)

| File | Purpose |
|------|---------|
| `AGENTS.md` | Development guidelines, project rules |
| `docs/SKT_DEVELOPER_GUIDE.md` | SKT module architecture and patterns |
| `docs/CHANGELOG_REFACTORING.md` | This document |

---

## Breaking Changes

1. **Storage format**: Projects saved with the old version need migration
2. **Import paths**: `from tools.layouts_KT import *` -> `from tools.skt_layout import *`
3. **Session data**: Server-side pickle files no longer used
4. **URL paths**: `/skt` -> `/knowledge-translation`

---

## Migration Notes

### For Developers

1. Callbacks now use `@callback` decorator (not `@app.callback`)
2. Storage data accessed via `State("*_STORAGE", "data")`
3. SKT functions prefixed with `skt_` or `__*_skt`
4. Check `NMAstudio-app-main` before editing functions (per AGENTS.md)

### For Users

1. Browser localStorage stores project data
2. Clear localStorage to reset: DevTools > Application > Local Storage > Clear
3. Demo projects load from embedded data, not CSV files
4. Chrome recommended (warning shown for other browsers)

---

## Version

- **Schema version**: 2.0
- **Refactoring date**: December 2024
- **Based on**: NMAstudio-app-main (single-page version)
