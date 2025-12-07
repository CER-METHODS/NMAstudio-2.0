# SKT (Knowledge Translation) Module - Developer Guide

## Overview

The SKT (Scalable Knowledge Translation) module presents Network Meta-Analysis (NMA) results to different audiences through two viewing modes:

- **Standard Version** (`skt_nonexpert()`): Simplified view for clinicians and general audiences
- **Advanced Version** (`skt_layout()`): Detailed view with configuration options for methodologists

---

## File Structure

### Core Files

| File | Purpose |
|------|---------|
| `pages/knowledge_translation.py` | Page registration, layout assembly, and all callbacks |
| `tools/skt_layout.py` | UI components: `Sktpage()`, `skt_layout()`, `skt_nonexpert()`, modals |
| `tools/skt_table.py` | AG Grid components: `treat_compare_grid`, `modal_compare_grid` |
| `tools/skt_data_helpers.py` | Data extraction functions from main STORAGE |
| `assets/skt_storage.py` | SKT-specific `dcc.Store` components |

### Visualization Functions

| File | Purpose |
|------|---------|
| `tools/functions_skt_ranking.py` | P-score ranking heatmap (`__ranking_plot_skt()`) |
| `tools/functions_skt_forestplot.py` | Forest plots for grid cells |
| `tools/functions_skt_boxplot.py` | Transitivity boxplots and scatter plots |
| `tools/functions_skt_abs_forest.py` | Absolute effect forest plots |
| `tools/functions_skt_others.py` | Cytoscape elements and stylesheets |

### CSS

| File | Purpose |
|------|---------|
| `assets/style.css` | Contains SKT-specific styles (search for `skt`, `#query-title`, etc.) |

---

## Storage Architecture

### What is localStorage?

NMAstudio uses the browser's **localStorage** to persist data between sessions. localStorage is a web storage API that allows JavaScript to store key-value pairs in the browser with no expiration date. This means:

- Data survives page refreshes and browser restarts
- Data is stored per origin (domain + port), so `http://localhost:8050` has separate storage from other origins
- Storage limit is typically 5-10 MB per origin
- Data is stored as strings (JSON is serialized/deserialized automatically by Dash)

#### Accessing localStorage with Chrome DevTools

To inspect, debug, or manually modify storage values:

1. **Open Chrome DevTools**: Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
2. **Go to Application tab**: Click "Application" in the top menu bar
3. **Expand Storage > Local Storage**: In the left sidebar, expand "Local Storage"
4. **Select your origin**: Click on `http://localhost:8050`
5. **View/Edit values**: 
   - All `_STORAGE` and `_SKT` variables are listed as keys
   - Click a key to see its JSON value in the panel below
   - Double-click to edit values directly
   - Right-click to delete individual keys or clear all

**Useful DevTools operations:**
- **Clear all data**: Right-click on the origin → "Clear" (useful for testing fresh state)
- **Copy value**: Select a key, copy the JSON from the preview pane
- **Search**: Use `Ctrl+F` in the table to find specific keys
- **Console access**: In the Console tab, use `localStorage.getItem('forest_data_STORAGE')` to read or `localStorage.setItem('key', 'value')` to write

**Tip**: When debugging SKT issues, check if the required `_STORAGE` variables contain valid data. Empty or `null` values often cause callbacks to fail silently.

---

### Main STORAGE Variables (from `assets/storage.py`)

SKT reads from these main application storage variables:

```python
# Key STORAGE variables used by SKT
results_ready_STORAGE    # bool - Controls page visibility
net_data_STORAGE         # dict - Network data {"data": <json_string>}
forest_data_STORAGE      # list - Forest plot data per outcome
net_split_data_STORAGE   # list - Direct/indirect effect estimates
ranking_data_STORAGE     # list - P-score rankings per outcome
cinema_net_data_STORAGE  # list - CINeMA certainty ratings
outcome_names_STORAGE    # list - ["Outcome1", "Outcome2", ...]
project_title_STORAGE    # str  - Project title for display
```

### Creating SKT-Specific Storage Variables

SKT has its own storage file to avoid bloating the main schema. Here's how to add new SKT storage:

**Step 1: Define in `assets/skt_storage.py`**

```python
# Schema definition
SKT_STORAGE_SCHEMA = {
    "treatment_fullnames_SKT": "dict",
    "your_new_variable_SKT": "list",  # Add your variable here
}

# Empty/default values
SKT_EMPTY_STORAGE = {
    "treatment_fullnames_SKT": {},
    "your_new_variable_SKT": [],  # Add default value
}

# Create dcc.Store components
def skt_storage_components():
    return [
        dcc.Store(id="treatment_fullnames_SKT", data=None, storage_type="local"),
        dcc.Store(id="your_new_variable_SKT", data=None, storage_type="local"),
    ]

SKT_STORAGE = skt_storage_components()
```

**Step 2: Include in `app.py`** (already done for SKT_STORAGE)

```python
from assets.skt_storage import SKT_STORAGE

def get_new_layout():
    return html.Div([
        # ... other components
        html.Div(SKT_STORAGE, style={"display": "none"}),
    ])
```

**Naming Convention**: Always suffix SKT storage variables with `_SKT`:
- `treatment_fullnames_SKT`
- `user_comments_SKT`
- `custom_ranges_SKT`

---

## Data Flow: From STORAGE to SKT Components

```
Main STORAGE (localStorage)
    │
    ├── results_ready_STORAGE ──────► Page visibility toggle
    │
    ├── net_data_STORAGE ───────────► get_skt_network_elements()
    │                                      │
    │                                      ▼
    │                                 Cytoscape graphs
    │                                 (cytoscape_skt, cytoscape_skt2)
    │
    ├── forest_data_STORAGE ────┬───► get_skt_two_outcome_data()
    │                           │          │
    ├── cinema_net_data_STORAGE ┘          ▼
    │                                 Standard grid
    │                                 (grid_treat_compare)
    │
    ├── forest_data_STORAGE ────┐
    ├── net_split_data_STORAGE  │
    ├── ranking_data_STORAGE    ├───► build_skt_advanced_row_data()
    ├── cinema_net_data_STORAGE │          │
    └── net_data_STORAGE ───────┘          ▼
                                      Advanced grid
                                      (quickstart-grid)
```

### Data Helper Functions (`skt_data_helpers.py`)

```python
# Extract network DataFrame
df = get_skt_network_data(net_data_storage)

# Get combined forest + netsplit data for outcome index
df = get_skt_final_data(forest_storage, netsplit_storage, outcome_idx=0)

# Get ranking data
df = get_skt_ranking_data(ranking_storage, outcome_idx=0)

# Get CINeMA certainty ratings
df = get_skt_cinema_data(cinema_storage, outcome_idx=0)

# Build two-outcome comparison table (Standard view)
df = get_skt_two_outcome_data(forest_storage, cinema_storage, outcome_names)

# Build nested row data for Advanced grid
row_data = build_skt_advanced_row_data(forest, netsplit, ranking, cinema, net_data, names)

# Get Cytoscape elements
elements = get_skt_network_elements(net_data_storage, outcome_idx=0)
```

---

## Writing Callbacks

### Basic Callback Pattern

```python
from dash import callback, Input, Output, State
from dash.exceptions import PreventUpdate

@callback(
    Output("your_component_id", "property"),
    Input("trigger_component", "property"),
    State("storage_component_STORAGE", "data"),
    prevent_initial_call=True,
)
def your_callback_function(trigger_value, storage_data):
    if not storage_data:
        raise PreventUpdate
    
    # Process data
    result = process_storage_data(storage_data)
    return result
```

### Page Visibility Pattern

```python
@callback(
    [
        Output("kt_not_ready_placeholder", "style"),
        Output("kt_main_content", "style"),
    ],
    Input("results_ready_STORAGE", "data"),
    prevent_initial_call=False,
)
def toggle_kt_page_visibility(results_ready):
    """Show main content only when results are ready."""
    if results_ready:
        return {"display": "none"}, {"display": "block"}
    else:
        return {"display": "block"}, {"display": "none"}
```

### Loading Data from STORAGE

```python
@callback(
    Output("grid_treat_compare", "rowData", allow_duplicate=True),
    [
        Input("results_ready_STORAGE", "data"),
        Input("kt_page_location", "pathname"),
    ],
    [
        State("forest_data_STORAGE", "data"),
        State("cinema_net_data_STORAGE", "data"),
        State("outcome_names_STORAGE", "data"),
    ],
    prevent_initial_call="initial_duplicate",
)
def update_grid_from_storage(results_ready, pathname, forest, cinema, outcomes):
    """Load grid data when navigating to KT page."""
    if not results_ready or "/knowledge-translation" not in (pathname or ""):
        raise PreventUpdate
    
    from tools.skt_data_helpers import get_skt_two_outcome_data
    df = get_skt_two_outcome_data(forest, cinema, outcomes)
    
    return df.to_dict("records")
```

### Modal Toggle Pattern

```python
@callback(
    Output("modal_transitivity", "is_open"),
    [
        Input("trans_button", "n_clicks"),
        Input("close_trans", "n_clicks"),
    ],
    State("modal_transitivity", "is_open"),
    prevent_initial_call=True,
)
def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open
```

### Network Selection → Grid Filter Pattern

```python
@callback(
    Output("grid_treat_compare", "rowData", allow_duplicate=True),
    [
        Input("cytoscape_skt2", "selectedNodeData"),
        Input("cytoscape_skt2", "selectedEdgeData"),
    ],
    [
        State("grid_treat_compare", "rowData"),
        State("forest_data_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def filter_grid_by_network_selection(nodes, edges, current_data, forest):
    """Filter grid when user selects nodes/edges in network graph."""
    if not nodes and not edges:
        # Reset to full data
        return get_full_grid_data(forest)
    
    selected_treatments = [n["id"] for n in (nodes or [])]
    # Filter current_data based on selected_treatments
    filtered = [row for row in current_data if row["Treatment"] in selected_treatments]
    return filtered
```

### Writing to SKT Storage

```python
@callback(
    Output("treatment_fullnames_SKT", "data"),
    Input("fullname_grid", "cellValueChanged"),
    State("treatment_fullnames_SKT", "data"),
    prevent_initial_call=True,
)
def save_treatment_fullname(cell_change, current_data):
    """Save user-edited treatment full names to SKT storage."""
    if not cell_change:
        raise PreventUpdate
    
    current_data = current_data or {}
    
    # Extract changed cell info
    row_data = cell_change[0]["data"]
    treatment = row_data["Treatment"]
    fullname = row_data["FullName"]
    
    # Update storage
    current_data[treatment] = fullname
    
    return current_data
```

---

## Standard vs Advanced Mode

### Toggle Mechanism

The toggle is implemented in three parts:

**1. Toggle Switch Component** (`skt_layout.py`):
```python
def switch_table():
    return html.Div([
        html.Span("Standard", className="sw_t1"),
        daq.ToggleSwitch(
            id="toggle_grid_select",
            value=False,  # False = Standard, True = Advanced
            color="green",
            size=50,
        ),
        html.Span("Advance", className="sw_t2"),
    ])
```

**2. Container Structure** (`skt_layout.py`):
```python
def Sktpage():
    return html.Div([
        switch_table(),
        html.Div(
            [skt_nonexpert()],  # Default: Standard mode
            id="skt_sub_content"
        ),
    ])
```

**3. Toggle Callback** (`knowledge_translation.py`):
```python
@callback(
    Output("skt_sub_content", "children"),
    Input("toggle_grid_select", "value"),
    prevent_initial_call=True,
)
def toggle_skt_version(toggle_value):
    if toggle_value:
        return skt_layout()    # Advanced
    else:
        return skt_nonexpert() # Standard
```

### Placeholder Components (Important!)

When one mode is active, callbacks referencing the other mode's component IDs will fail. To prevent this, both layouts include hidden placeholder components:

**In `skt_nonexpert()` - Placeholders for Advanced IDs:**
```python
advanced_placeholders = html.Div([
    html.Div(id="quickstart-grid", style={"display": "none"}),
    html.Div(id="cytoscape_skt", style={"display": "none"}),
    html.Div(id="kt2_nclr", children="Default", style={"display": "none"}),
    html.Div(id="kt2_eclr", children="Default", style={"display": "none"}),
    dcc.Input(id="kt2_nclr_custom", value="", style={"display": "none"}),
    dcc.Input(id="kt2_eclr_custom", value="", style={"display": "none"}),
    html.Div(id="kt2_nds", children="Default", style={"display": "none"}),
    html.Div(id="kt2_egs", children="Number of studies", style={"display": "none"}),
    dcc.Checklist(id="checklist_effects", options=[], style={"display": "none"}),
    dcc.Input(id="range_lower", style={"display": "none"}),
    html.Div(id="kt2-graph-layout-dropdown", style={"display": "none"}),
], style={"display": "none"})
```

**In `skt_layout()` - Placeholders for Standard IDs:**
```python
standard_placeholders = html.Div([
    html.Div(id="cytoscape_skt2", style={"display": "none"}),
    html.Div(id="grid_treat_compare", style={"display": "none"}),
    html.Div(id="kt-graph-layout-dropdown", style={"display": "none"}),
], style={"display": "none"})
```

**When adding new callbacks**: If your callback references components that only exist in one mode, add a placeholder in the other mode's layout function.

---

## Naming Conventions

### Component IDs

| Pattern | Example | Description |
|---------|---------|-------------|
| `*_STORAGE` | `forest_data_STORAGE` | Main app dcc.Store |
| `*_SKT` | `treatment_fullnames_SKT` | SKT-specific storage |
| `cytoscape_skt` | - | Advanced network graph |
| `cytoscape_skt2` | - | Standard network graph |
| `modal_*` | `modal_transitivity` | Modal dialogs |
| `grid_*` | `grid_treat_compare` | AG Grid components |
| `skt_*` | `skt_sub_content` | SKT container elements |
| `kt_*` | `kt_main_content` | KT page elements |
| `kt2_*` | `kt2_nclr` | Advanced mode controls |

### Functions

| Pattern | Example | Description |
|---------|---------|-------------|
| `get_skt_*` | `get_skt_final_data()` | Data extraction |
| `build_skt_*` | `build_skt_advanced_row_data()` | Complex builders |
| `__*_skt` | `__ranking_plot_skt()` | Private SKT functions |
| `__generate_skt_*` | `__generate_skt_stylesheet()` | Stylesheet generators |
| `__skt_*_forstplot` | `__skt_mix_forstplot()` | Forest plot generators |

### Files

| Pattern | Purpose |
|---------|---------|
| `skt_*.py` | Core SKT components |
| `functions_skt_*.py` | Visualization functions |

---

## Adding New Features

### Example: Adding a New SKT Storage Variable

**1. Add to `assets/skt_storage.py`:**
```python
SKT_STORAGE_SCHEMA = {
    "treatment_fullnames_SKT": "dict",
    "user_notes_SKT": "dict",  # NEW
}

SKT_EMPTY_STORAGE = {
    "treatment_fullnames_SKT": {},
    "user_notes_SKT": {},  # NEW
}

def skt_storage_components():
    return [
        dcc.Store(id="treatment_fullnames_SKT", data=None, storage_type="local"),
        dcc.Store(id="user_notes_SKT", data=None, storage_type="local"),  # NEW
    ]
```

**2. Create callback in `pages/knowledge_translation.py`:**
```python
@callback(
    Output("user_notes_SKT", "data"),
    Input("notes_input", "value"),
    State("user_notes_SKT", "data"),
    prevent_initial_call=True,
)
def save_user_notes(new_note, current_notes):
    current_notes = current_notes or {}
    # Update logic here
    return current_notes
```

### Example: Adding a New Visualization

**1. Create function in `tools/functions_skt_yourplot.py`:**
```python
import plotly.graph_objects as go

def __your_new_plot_skt(data):
    """Create your new SKT visualization."""
    fig = go.Figure()
    # Build figure...
    return fig
```

**2. Add to layout in `tools/skt_layout.py`:**
```python
from tools.functions_skt_yourplot import __your_new_plot_skt

# In skt_layout() or skt_nonexpert():
dcc.Graph(
    id="your_new_plot_skt",
    figure=__your_new_plot_skt(default_data),
)
```

**3. Add callback in `pages/knowledge_translation.py`:**
```python
@callback(
    Output("your_new_plot_skt", "figure"),
    Input("results_ready_STORAGE", "data"),
    State("your_data_STORAGE", "data"),
    prevent_initial_call=True,
)
def update_your_plot(results_ready, data):
    from tools.functions_skt_yourplot import __your_new_plot_skt
    return __your_new_plot_skt(data)
```

---

## Common Pitfalls

1. **Duplicate Component IDs**: Standard and Advanced modes can share IDs (e.g., `title_skt`) since only one is active at a time. However, CSS selectors must account for this.

2. **Missing Placeholders**: If you add a callback that references a component only in one mode, add a placeholder in the other mode's layout or you'll get "nonexistent object" errors.

3. **Storage Data Format**: Main STORAGE often wraps data as `{"data": <json_string>}`. Use the helper functions in `skt_data_helpers.py` to extract properly.

4. **Multi-outcome Lists**: `forest_data_STORAGE`, `ranking_data_STORAGE`, etc. are lists where index 0 = first outcome, index 1 = second outcome.

5. **Initial Call Prevention**: Use `prevent_initial_call="initial_duplicate"` when you need to allow updates on page navigation but prevent double-firing.

---

## Testing

Run the SKT test suite:
```bash
cd NMAstudio-app
python tests/test_knowledge_translation_page.py
```

The test covers:
- Redirect when results not ready
- Demo loading
- Standard/Advanced toggle
- Component visibility
- Console error checking

---

## Deployment Configuration

### Environment Variables

NMAstudio uses a `.env` file for configuration. Create one in the project root:

```bash
# .env file example
DEBUG_MODE=False
AG_GRID_KEY=your-ag-grid-enterprise-license-key-here
```

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_MODE` | Enable Dash debug mode (hot reload, error details) | `False` |
| `AG_GRID_KEY` | AG Grid Enterprise license key for advanced features | `""` (empty) |

The `.env` file is loaded automatically via `python-dotenv` in `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()

DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "yes")
```

AG Grid license is read in `tools/skt_layout.py` and `tools/skt_table.py`:

```python
AG_GRID_KEY = os.environ.get("AG_GRID_KEY", "")
```

### Disabling Yada (Dashboard Assistant) for Production

The Yada assistant (`dash-yada`) provides interactive guided tours. To disable it for production:

**Option 1: Comment out in `tools/skt_layout.py`**

In `skt_nonexpert()` function (around line 1707-1740):

```python
# Comment out these lines:
# from tools.yada import yada_stand
# ...
# yada_stand,
```

**Option 2: Conditional import based on DEBUG_MODE**

Modify `tools/skt_layout.py`:

```python
import os
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

# In skt_nonexpert() function:
if DEBUG_MODE:
    from tools.yada import yada_stand
    yada_component = yada_stand
else:
    yada_component = html.Div()  # Empty placeholder

# Then use yada_component in the layout instead of yada_stand
```

**Option 3: Remove from requirements (not recommended)**

If you never need Yada, remove from `requirements.yml`:

```yaml
# Remove this line:
# - dash-yada==0.0.1
```

### Production Deployment Checklist

1. **Set environment variables:**
   ```bash
   DEBUG_MODE=False
   AG_GRID_KEY=<your-license-key>
   ```

2. **Disable/configure Yada** (see above)

3. **Review print statements:** Many callbacks have `[DEBUG]` print statements. These are harmless but can be removed for cleaner logs.

4. **Host binding** is configured in `app.py`:
   ```python
   app.run(host="0.0.0.0", port=8050, debug=DEBUG_MODE)
   ```

5. **Consider using a production WSGI server** (gunicorn, waitress):
   ```bash
   gunicorn app:server -b 0.0.0.0:8050
   ```

---

## Related Documentation

- `AGENTS.md` - Project-wide coding guidelines
- `assets/storage.py` - Main STORAGE schema
- `assets/skt_storage.py` - SKT storage schema
