# SKT (Knowledge Translation) STORAGE Integration Guide

This document explains how the SKT page accesses data from STORAGE and the helper functions available for developers.

## Overview

The SKT page no longer loads data from CSV files at import time. Instead, it uses **localStorage STORAGE** populated by the NMA analysis, with helper functions in `tools/skt_data_helpers.py` to parse and transform the data.

## STORAGE Data Sources

### Primary STORAGE Keys Used by SKT

| STORAGE Key | Type | Description |
|-------------|------|-------------|
| `forest_data_STORAGE` | `list[str]` | JSON strings per outcome with NMA results (Treatment, RR, CI_lower, CI_upper, Reference) |
| `net_data_STORAGE` | `dict` | Wide-format network data with study-level info, includes `effect_size1`, `effect_size2` columns |
| `net_split_data_STORAGE` | `list[str]` | Direct/indirect estimates per outcome (CI stored as formatted strings) |
| `ranking_data_STORAGE` | `list[str]` | P-scores per outcome |
| `cinema_net_data_STORAGE` | `list[str]` | CINeMA confidence ratings per outcome |
| `outcome_names_STORAGE` | `list[str]` | Outcome names, e.g., `["PASI90", "SAE", "AE"]` |
| `results_ready_STORAGE` | `bool` | Whether NMA results are available |

### Data Structure Examples

#### forest_data_STORAGE (per outcome)
```python
# Access: forest_data_STORAGE[outcome_idx]
# Returns JSON string with orient="split"
{
  "columns": ["Treatment", "RR", "CI_lower", "CI_upper", "Reference", ...],
  "index": [0, 1, 2, ...],
  "data": [
    ["ADA", 1.63, 1.43, 1.86, "ETA"],
    ["BIME", 2.84, 2.50, 3.22, "ETA"],
    ...
  ]
}
```

#### net_split_data_STORAGE (CI as formatted strings!)
```python
# IMPORTANT: direct/indirect are strings like "0.6 (0.51, 0.71)"
{
  "columns": ["comparison", "direct", "indirect", "p-value"],
  "data": [
    ["ADA:BIME", "0.6 (0.51, 0.71)", "0.56 (0.5, 0.63)", 0.437],
    ...
  ]
}
```

#### net_data_STORAGE (contains effect size type)
```python
# Access effect size per outcome:
df = pd.read_json(StringIO(net_data_STORAGE["data"]), orient="split")
effect_size_outcome1 = df["effect_size1"].iloc[0]  # e.g., "RR", "OR", "MD"
effect_size_outcome2 = df["effect_size2"].iloc[0]
```

## Helper Functions (tools/skt_data_helpers.py)

### get_skt_two_outcome_data()
**Purpose**: Generate Standard grid data combining two outcomes with certainty ratings.

```python
from tools.skt_data_helpers import get_skt_two_outcome_data

df = get_skt_two_outcome_data(
    forest_data_storage,      # list of JSON strings
    cinema_net_data_storage,  # list of JSON strings (can be empty)
    outcome_names             # list of outcome names
)
# Returns DataFrame with: Treatment, Reference, RR, CI_lower, CI_upper,
#                         RR_out2, CI_lower_out2, CI_upper_out2,
#                         Certainty_out1, Certainty_out2
```

### get_skt_network_elements()
**Purpose**: Generate cytoscape nodes and edges for network graph.

```python
from tools.skt_data_helpers import get_skt_network_elements

elements = get_skt_network_elements(net_data_storage, outcome_idx=0)
# Returns list of cytoscape elements:
# [{"data": {"id": "ADA", "label": "ADA"}}, {"data": {"source": "ADA", "target": "PBO", ...}}, ...]
```

### build_skt_advanced_row_data()
**Purpose**: Build nested row structure for Advanced grid (master-detail).

```python
from tools.skt_data_helpers import build_skt_advanced_row_data

row_data, _ = build_skt_advanced_row_data(
    forest_data_storage,
    net_split_data_storage,
    ranking_data_storage,
    cinema_net_data_storage,
    net_data_storage,
    outcome_idx=0
)
# Returns list of dicts with nested "Treatments" for master-detail grid
```

### get_skt_final_data()
**Purpose**: Merge forest data with netsplit (direct/indirect) estimates.

```python
from tools.skt_data_helpers import get_skt_final_data

df = get_skt_final_data(forest_data_storage, net_split_data_storage, outcome_idx=0)
# Returns DataFrame with: Treatment, Reference, RR, CI_lower, CI_upper,
#                         direct, direct_low, direct_up, indirect, indirect_low, indirect_up
```

**Note**: This function parses the CI strings like `"0.6 (0.51, 0.71)"` into separate columns.

### get_skt_ranking_data()
**Purpose**: Get P-scores for treatments.

```python
from tools.skt_data_helpers import get_skt_ranking_data

df = get_skt_ranking_data(ranking_data_storage, outcome_idx=0)
# Returns DataFrame with: treatment, pscore
```

### get_skt_network_data()
**Purpose**: Get wide-format study data.

```python
from tools.skt_data_helpers import get_skt_network_data

df = get_skt_network_data(net_data_storage)
# Returns DataFrame with all study-level columns including effect_size1, effect_size2, etc.
```

### get_risk_ranges_from_wide()
**Purpose**: Calculate risk ranges per treatment from event rates.

```python
from tools.skt_data_helpers import get_risk_ranges_from_wide

df = get_risk_ranges_from_wide(net_data_storage, outcome_idx=0)
# Returns DataFrame with: treat, min_value, max_value (per 1000)
```

## Accessing Effect Size Type

The effect size type (RR, OR, MD, SMD) is stored in `net_data_STORAGE`:

```python
from tools.skt_data_helpers import get_skt_network_data

df = get_skt_network_data(net_data_storage)

# Get effect size for each outcome
effect_size_1 = df["effect_size1"].iloc[0]  # e.g., "RR"
effect_size_2 = df["effect_size2"].iloc[0]  # e.g., "RR"
effect_size_3 = df["effect_size3"].iloc[0]  # if 3 outcomes

# Or get all effect sizes as a list
num_outcomes = len(outcome_names_storage)
effect_sizes = [df[f"effect_size{i+1}"].iloc[0] for i in range(num_outcomes)]
```

## Writing Callbacks

### Pattern for STORAGE-based Callbacks

```python
@callback(
    Output("your_component", "property", allow_duplicate=True),
    [
        Input("results_ready_STORAGE", "data"),
        Input("kt_page_location", "pathname"),  # Triggers on page navigation
    ],
    [
        State("forest_data_STORAGE", "data"),
        State("net_data_STORAGE", "data"),
        # ... other STORAGE states
    ],
    prevent_initial_call="initial_duplicate",
)
def update_your_component(results_ready, pathname, forest_storage, net_storage, ...):
    if not results_ready or not forest_storage:
        raise PreventUpdate
    
    try:
        # Use helper functions to get data
        df = get_skt_two_outcome_data(forest_storage, ...)
        return df.to_dict("records")
    except Exception as e:
        print(f"[ERROR] your_callback: {e}")
        raise PreventUpdate
```

### Important Notes

1. **Use `allow_duplicate=True`** when multiple callbacks target the same output
2. **Use `prevent_initial_call="initial_duplicate"`** to allow the callback to fire on page navigation
3. **Include `kt_page_location.pathname` as Input** to trigger when user navigates to KT page
4. **Always check `results_ready`** before processing data

## File Structure

```
tools/
├── skt_data_helpers.py    # Helper functions for STORAGE → SKT data
├── skt_layout.py          # Layout components (no CSV loading)
├── skt_table.py           # Grid components (empty placeholder data)
└── functions_skt_*.py     # Other SKT functions

pages/
└── knowledge_translation.py  # Page with STORAGE callbacks

assets/
├── storage.py             # Main STORAGE definitions
└── skt_storage.py         # SKT-specific STORAGE (treatment_fullnames_SKT)
```

## Migration from CSV

Previously, SKT loaded data at import time:
```python
# OLD (removed)
data = pd.read_csv("db/skt/final_all.csv")
```

Now, data is loaded dynamically via callbacks:
```python
# NEW
@callback(...)
def update_grid(..., forest_storage, ...):
    df = get_skt_final_data(forest_storage, net_split_storage, 0)
    return df.to_dict("records")
```

## Debugging

To test helper functions with real data:

```python
# In Python REPL or test script
import json
from tools.skt_data_helpers import get_skt_two_outcome_data

# Simulate STORAGE data (copy from browser localStorage)
forest_storage = ['{"columns":["Treatment",...], "data":[...]}', ...]

df = get_skt_two_outcome_data(forest_storage, None, None)
print(df.head())
```

Check browser console for callback errors:
- "Callback failed: the server did not respond" → Check for Python exceptions in callback
- Use `print()` statements in callbacks for debugging (visible in server terminal)
