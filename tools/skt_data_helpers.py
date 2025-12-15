"""
SKT (Knowledge Translation) Data Helpers

Functions to derive SKT page data from STORAGE components.
This replaces the hardcoded CSV file loading with dynamic data from the user's project.
"""

import pandas as pd
import numpy as np
from io import StringIO
from tools.utils import get_net_data_json, get_league_table_data_list



def Generate_kt_standad_data(forest_data_STORAGE, num_outcomes, effect_sizes):
    if not forest_data_STORAGE:
        return pd.DataFrame()
    
    def to_df(item):
        if isinstance(item, pd.DataFrame):
            return item.copy()
        if isinstance(item, str):
            for orient in ("split", None):
                try:
                    return pd.read_json(StringIO(item), orient=orient) if orient else pd.read_json(item)
                except Exception:
                    pass
        return None

    dfs = []

    for i in range(min(num_outcomes, len(forest_data_STORAGE))):
        df = to_df(forest_data_STORAGE[i])
        if df is None or not {"Treatment", "Reference"}.issubset(df.columns):
            continue
        effect_s = effect_sizes[i]
        suf = f"_out{i+1}"
        col_map = {
            f"{effect_s}": f"{effect_s}{suf}",
            "CI_lower": f"CI_lower{suf}",
            "CI_upper": f"CI_upper{suf}",
        }

        keep = ["Treatment", "Reference"] + [c for c in col_map if c in df.columns]
        
        dfs.append(df[keep].rename(columns=col_map))
    
   

    if not dfs:
        return pd.DataFrame()

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on=["Treatment", "Reference"], how="outer")

    # remove duplicate unordered pairs + self comparisons
    merged["_k"] = merged.apply(
        lambda r: "::".join(sorted(map(str, [r["Treatment"], r["Reference"]]))),
        axis=1,
    )

    merged = (
        merged[merged["Treatment"] != merged["Reference"]]
        .sort_values(["_k"])
        .drop_duplicates("_k")
        .drop(columns="_k")
        .reset_index(drop=True)
    )

    # build display labels
    for i in range(1, int(num_outcomes or 1) + 1):
        effect_s = effect_sizes[i-1]
        rr, lo, hi = f"{effect_s}_out{i}", f"CI_lower_out{i}", f"CI_upper_out{i}"
        lbl = f"{rr}_label"

        if rr not in merged.columns:
            continue

        def fmt(r):
            try:
                if pd.notna(r[rr]) and pd.notna(r.get(lo)) and pd.notna(r.get(hi)):
                    return f"{float(r[rr]):.2f} \n({float(r[lo]):.2f}, {float(r[hi]):.2f})"
                if pd.notna(r[rr]):
                    return f"{float(r[rr]):.2f}"
            except Exception:
                pass
            return ""

        merged[lbl] = merged.apply(fmt, axis=1)

    return merged


def Generate_kt_standad_columnDefs(num_outcomes, outcome_names, effect_sizes):
    """
    Generate column definitions for standard KT data grid.

    Args:
        num_outcomes: Number of outcomes in the project
        outcome_names: List of outcome names (e.g., ["PASI90", "SAE"]) 
    Returns:
        List of column definition dicts for AG Grid.
    """
    style_certainty = {
        "white-space": "pre",
        "display": "grid",
        "text-align": "center",
        "alignItems": "center",
        "border-left": "solid 0.8px",
    }

    cols = []

    # Treatment column
    cols.append(
        {
            "headerName": "Treatment",
            "field": "Treatment",
            "suppressHeaderMenuButton": True,
            "editable": False,
            "resizable": False,
            "cellStyle": {"font-weight": "bold"},
        }
    )

    # Switch column (button)
    cols.append(
        {
            "headerName": "Switch",
            "suppressHeaderMenuButton": True,
            "field": "switch",
            "editable": False,
            "resizable": False,
            "headerComponent": "HeaderWithIcon",
            "cellRenderer": "DMC_Button",
            "cellRendererParams": {"icon": "subway:round-arrow-3", "color": "#ffc000"},
            "cellStyle": {"background-color": "white", "white-space": "pre"},
        }
    )

    # Comparator column
    cols.append(
        {
            "headerName": "Comparator",
            "field": "Reference",
            "suppressHeaderMenuButton": True,
            "editable": False,
            "resizable": False,
            "cellStyle": {"white-space": "pre", "font-weight": "bold", "border-right": "solid 0.8px"},
        }
    )

    # Add grouped columns per outcome
    for i in range(1, max(1, int(num_outcomes or 1)) + 1):
        effect_s = effect_sizes[i-1]
        header_name = None
        try:
            if outcome_names and len(outcome_names) >= i and outcome_names[i - 1]:
                header_name = outcome_names[i - 1]
        except Exception:
            header_name = None
        if not header_name:
            header_name = f"Outcome {i}"

        # display the formatted label column created by Generate_kt_standad_data
        rr_field = f"{effect_s}_out{i}_label"
        cert_field = f"Certainty_out{i}"

        children = [
            {"field": rr_field, 
             "headerName": f"{effect_s}", 
             "headerComponent": "HeaderWithIcon", "suppressHeaderMenuButton": True},
            {
                "field": cert_field,
                "suppressHeaderMenuButton": True,
                "headerName": "Certainty",
                "resizable": False,
                "headerComponent": "HeaderWithIcon",
                "tooltipField": cert_field,
                "tooltipComponentParams": {"color": "#d8f0d3"},
                "tooltipComponent": "CustomTooltip",
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},
                        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
                        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},
                    ]
                },
            },
        ]

        cols.append(
            {
                "headerName": header_name,
                "headerClass": "center-aligned-group-header",
                "resizable": False,
                "suppressStickyLabel": True,
                "children": children,
            }
        )

    return cols


# def get_skt_final_data(forest_data_storage, net_split_data_storage, outcome_idx=0):
#     """
#     Derive final_all.csv equivalent data from STORAGE.

#     Combines forest_data (NMA mixed effects) with net_split_data (direct/indirect).

#     Args:
#         forest_data_storage: List of JSON strings, one per outcome
#         net_split_data_storage: List of JSON strings with direct/indirect estimates
#         outcome_idx: Which outcome to use (0-indexed)

#     Returns:
#         DataFrame with columns: Treatment, Reference, RR, CI_lower, CI_upper, se,
#                                direct, direct_low, direct_up, indirect, indirect_low, indirect_up
#     """
#     if not forest_data_storage or len(forest_data_storage) <= outcome_idx:
#         return pd.DataFrame()

#     # Load forest data for the outcome
#     forest_json = forest_data_storage[outcome_idx]
#     if not forest_json:
#         return pd.DataFrame()

#     forest_df = pd.read_json(StringIO(forest_json), orient="split")

#     # Load netsplit data if available
#     if net_split_data_storage and len(net_split_data_storage) > outcome_idx:
#         netsplit_json = net_split_data_storage[outcome_idx]
#         if netsplit_json:
#             netsplit_df = pd.read_json(StringIO(netsplit_json), orient="split")

#             # Parse comparison column to get Treatment and Reference
#             if "comparison" in netsplit_df.columns:
#                 netsplit_df[["Treatment", "Reference"]] = netsplit_df[
#                     "comparison"
#                 ].str.split(":", expand=True)

#             # Helper function to parse CI strings like "0.6 (0.51, 0.71)"
#             def parse_ci_string(s):
#                 if pd.isna(s) or s == "" or not isinstance(s, str):
#                     return np.nan, np.nan, np.nan
#                 try:
#                     s = s.strip()
#                     if "(" not in s:
#                         return float(s), np.nan, np.nan
#                     parts = s.split("(")
#                     point = float(parts[0].strip())
#                     ci_part = parts[1].replace(")", "").strip()
#                     ci_vals = ci_part.split(",")
#                     low = float(ci_vals[0].strip())
#                     high = float(ci_vals[1].strip())
#                     return point, low, high
#                 except:
#                     return np.nan, np.nan, np.nan

#             # Parse direct/indirect columns if they are formatted strings like "0.6 (0.51, 0.71)"
#             if "direct" in netsplit_df.columns:
#                 # Check if direct is a formatted string
#                 sample_val = (
#                     netsplit_df["direct"].iloc[0] if len(netsplit_df) > 0 else None
#                 )
#                 if sample_val and isinstance(sample_val, str) and "(" in sample_val:
#                     direct_parsed = netsplit_df["direct"].apply(parse_ci_string)
#                     netsplit_df["direct_val"] = direct_parsed.apply(lambda x: x[0])
#                     netsplit_df["direct_low"] = direct_parsed.apply(lambda x: x[1])
#                     netsplit_df["direct_up"] = direct_parsed.apply(lambda x: x[2])
#                     netsplit_df["direct"] = netsplit_df["direct_val"]

#             if "indirect" in netsplit_df.columns:
#                 sample_val = (
#                     netsplit_df["indirect"].iloc[0] if len(netsplit_df) > 0 else None
#                 )
#                 if sample_val and isinstance(sample_val, str) and "(" in sample_val:
#                     indirect_parsed = netsplit_df["indirect"].apply(parse_ci_string)
#                     netsplit_df["indirect_val"] = indirect_parsed.apply(lambda x: x[0])
#                     netsplit_df["indirect_low"] = indirect_parsed.apply(lambda x: x[1])
#                     netsplit_df["indirect_up"] = indirect_parsed.apply(lambda x: x[2])
#                     netsplit_df["indirect"] = netsplit_df["indirect_val"]

#             # Merge with forest data
#             merge_cols = (
#                 ["Treatment", "Reference"] if "Treatment" in netsplit_df.columns else []
#             )

#             # Determine which columns to merge
#             netsplit_cols_to_merge = merge_cols.copy()
#             for col in [
#                 "direct",
#                 "direct_low",
#                 "direct_up",
#                 "indirect",
#                 "indirect_low",
#                 "indirect_up",
#             ]:
#                 if col in netsplit_df.columns:
#                     netsplit_cols_to_merge.append(col)

#             if merge_cols and len(netsplit_cols_to_merge) > len(merge_cols):
#                 forest_df = pd.merge(
#                     forest_df,
#                     netsplit_df[netsplit_cols_to_merge],
#                     on=merge_cols,
#                     how="left",
#                 )

#     return forest_df




def get_skt_cinema_data(cinema_net_data_storage, outcome_idx=0):
    """
    Get CINeMA confidence data from STORAGE.

    Args:
        cinema_net_data_storage: List of JSON strings with CINeMA data
        outcome_idx: Which outcome to use

    Returns:
        DataFrame with columns: Comparison, Confidence rating, Within-study bias, etc.
    """
    if not cinema_net_data_storage or len(cinema_net_data_storage) <= outcome_idx:
        return pd.DataFrame()

    cinema_json = cinema_net_data_storage[outcome_idx]
    if not cinema_json:
        return pd.DataFrame()

    return pd.read_json(StringIO(cinema_json), orient="split")


def get_skt_network_data(net_data_storage):
    """
    Get wide-format network data from STORAGE.

    Args:
        net_data_storage: Dict with "data" key containing JSON string

    Returns:
        DataFrame with study-level data (treat1, treat2, TE1, seTE1, etc.)
    """
    if not net_data_storage:
        return pd.DataFrame()

    json_str = get_net_data_json(net_data_storage)
    if not json_str:
        return pd.DataFrame()

    return pd.read_json(StringIO(json_str), orient="split")




#####################skt advanced data helpers #########################



def Generate_advanced_data(data, p_score, cinima_dat, out_list, long_dat):
    import pandas as pd
    import numpy as np

    df = prepare_base_dataframe(data)
    df = add_cinema_data(df, cinima_dat)
    df = add_stat_columns(df)
    df = apply_forest_plot_options(df)
    
    range_ref_ab = compute_reference_ranges(long_dat)
    row_data_default = build_grouped_rows(df)

    row_data_default = merge_reference_data(
        row_data_default, p_score, range_ref_ab
    )

    format_treatment_strings(row_data_default)

    return row_data_default

def prepare_base_dataframe(data):
    import pandas as pd

    df = pd.DataFrame(data)

    default_cols = [
        'Certainty', 'within_study', 'reporting',
        'indirectness', 'imprecision', 'heterogeneity', 'incoherence'
    ]
    for col in default_cols:
        df[col] = ''

    df['Graph'] = ''
    df['risk'] = 'Enter a number'
    df['Scale_lower'] = 'Enter a value for lower'
    df['Scale_upper'] = 'Enter a value for upper'
    df['Comments'] = ''
    df['ab_difference'] = ''
    df['rationality'] = 'Enter a reason'

    return df

def add_cinema_data(df, cinima_dat):
    for i, row in df.iterrows():
        src, trg = row['Reference'], row['Treatment']
        comps = {f'{src}:{trg}', f'{trg}:{src}'}

        cin = cinima_dat[cinima_dat['Comparison'].isin(comps)]
        if cin.empty:
            continue

        df.loc[i, 'Certainty'] = cin['Confidence rating'].iloc[0]
        df.loc[i, 'within_study'] = cin['Within-study bias'].iloc[0]
        df.loc[i, 'reporting'] = cin['Reporting bias'].iloc[0]
        df.loc[i, 'indirectness'] = cin['Indirectness'].iloc[0]
        df.loc[i, 'imprecision'] = cin['Imprecision'].iloc[0]
        df.loc[i, 'heterogeneity'] = cin['Heterogeneity'].iloc[0]
        df.loc[i, 'incoherence'] = cin['Incoherence'].iloc[0]

    return df

def add_stat_columns(df):
    df['CI_width_hf'] = df['CI_upper'] - df['RR']
    df['lower_error'] = df['RR'] - df['CI_lower']
    df['weight'] = 1 / df['CI_width_hf']
    return df.round(2)

def apply_forest_plot_options(df):
    value_effect = ['PI', 'direct', 'indirect']
    from tools.functions_skt_forestplot import __skt_options_forstplot
    return __skt_options_forstplot(
        value_effect, df, 0.2,
        scale_lower=None, scale_upper=None, refer_name=None
    )

def compute_reference_ranges(long_dat):
    import pandas as pd

    return (
        long_dat
        .groupby('treat')
        .apply(lambda g: pd.Series({
            'min_value': (g['rPASI90'] / g['nPASI90']).min() * 1000,
            'max_value': (g['rPASI90'] / g['nPASI90']).max() * 1000
        }))
        .reset_index()
    )

def build_grouped_rows(df):
    import pandas as pd

    rows = []
    grouped = df.groupby(['Reference', 'risk', 'Scale_lower', 'Scale_upper'])

    for (ref, risk, lo, hi), group in grouped:
        treatments = group_to_treatments(group)
        rows.append({
            'Reference': ref,
            'risk': risk,
            'Scale_lower': lo,
            'Scale_upper': hi,
            'Treatments': treatments
        })

    return pd.DataFrame(rows)

def group_to_treatments(group):
    return [
        {
            "Treatment": r["Treatment"],
            "RR": r["RR"],
            "direct": r["direct"],
            "Graph": r["Graph"],
            "indirect": r["indirect"],
            "p-value": r["p-value"],
            "Certainty": r["Certainty"],
            "direct_low": r["direct_low"],
            "direct_up": r["direct_up"],
            "indirect_low": r["indirect_low"],
            "indirect_up": r["indirect_up"],
            "CI_lower": r["CI_lower"],
            "CI_upper": r["CI_upper"],
            "Comments": r["Comments"],
            "ab_difference": r["ab_difference"],
            "within_study": r["within_study"],
            "reporting": r["reporting"],
            "indirectness": r["indirectness"],
            "imprecision": r["imprecision"],
            "heterogeneity": r["heterogeneity"],
            "incoherence": r["incoherence"],
        }
        for _, r in group.iterrows()
    ]

def merge_reference_data(row_df, p_score, range_ref_ab):
    row_df = row_df.merge(
        p_score, left_on='Reference', right_on='treatment', how='left'
    )

    row_df = row_df.merge(
        range_ref_ab, left_on='Reference', right_on='treat', how='left'
    )

    row_df['risk_range'] = row_df.apply(
        lambda r: f"from {int(r['min_value'])} to {int(r['max_value'])}"
        if pd.notna(r.get('min_value')) else '',
        axis=1
    )

    return row_df

def format_treatment_strings(row_df):
    for j in range(row_df.shape[0]):
        for i in range(1, len(row_df.loc[j, 'Treatments'])):
            t = row_df.loc[j, 'Treatments'][i]

            t['RR'] = f"{t['RR']}\n({t['CI_lower']}, {t['CI_upper']})"

            t['direct'] = (
                f"{t['direct']}\n({t['direct_low']}, {t['direct_up']})"
                if t['direct'] not in ['', None] else ""
            )

            t['indirect'] = (
                f"{t['indirect']}\n({t['indirect_low']}, {t['indirect_up']})"
                if t['indirect'] not in ['', None] else ""
            )


