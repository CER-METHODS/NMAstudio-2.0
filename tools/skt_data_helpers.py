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
def Generate_advanced_data(data, p_score, net_dat, effect_size, out_idx, consistency_data,lower):
    n_treatments = len(p_score)
    df = prepare_base_dataframe(data)
    df = add_stat_columns(df, effect_size)
    df = apply_forest_plot_options(df, effect_size, n_treatments, consistency_data, lower)
    if effect_size in ['RR', 'OR', 'HR']:
        range_ref_ab = compute_reference_ranges(net_dat, out_idx)
    else:
        range_ref_ab = pd.DataFrame(columns=['treat', 'min_value', 'max_value'])

    row_data_default = build_grouped_rows(df, effect_size)

    row_data_default = merge_reference_data(
        row_data_default, p_score, range_ref_ab
    )
    
    format_treatment_strings(row_data_default, effect_size)
    
    return row_data_default

def prepare_base_dataframe(data):
    df = pd.DataFrame(data)

    default_cols = [
        'Certainty', 'within_study', 'reporting',
        'indirectness', 'imprecision',
        'heterogeneity', 'incoherence'
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

def add_stat_columns(df, effect_size):
    df['CI_width_hf'] = df['CI_upper'] - df[effect_size]
    df['lower_error'] = df[effect_size] - df['CI_lower']
    df['weight'] = 1 / df['CI_width_hf']
    return df.round(2)

def apply_forest_plot_options(df, effect_size, n_treatments, consistency_data, lower):
    from tools.functions_skt_forestplot import __skt_options_forstplot
    value_effect = ['PI', 'direct', 'indirect']

    return __skt_options_forstplot(
        value_effect,
        df,
        consistency_data,
        lower,
        effect_size,
        n_treatments,
        scale_lower=None,
        scale_upper=None,
        refer_name=None
    )

def compute_reference_ranges(net_dat, outcome_idx):
    ev1 = f"event1{outcome_idx+1}"
    n1  = f"n1{outcome_idx+1}"
    ev2 = f"event2{outcome_idx+1}"
    n2  = f"n2{outcome_idx+1}"

    long_df = pd.concat(
        [
            net_dat[['treat1', ev1, n1]].rename(
                columns={'treat1': 'treat', ev1: 'event', n1: 'n'}
            ),
            net_dat[['treat2', ev2, n2]].rename(
                columns={'treat2': 'treat', ev2: 'event', n2: 'n'}
            )
        ],
        ignore_index=True
    )
    
    long_df = long_df.dropna(subset=['event', 'n'])

    return (
        long_df
        .groupby('treat')
        .apply(lambda g: pd.Series({
            'min_value': (g['event'] / g['n']).min() * 1000,
            'max_value': (g['event'] / g['n']).max() * 1000
        }))
        .reset_index()
    )

def build_grouped_rows(df, effect_size):
    rows = []
    grouped = df.groupby(['Reference', 'risk', 'Scale_lower', 'Scale_upper'])

    for (ref, risk, lo, hi), group in grouped:
        rows.append({
            'Reference': ref,
            'risk': risk,
            'Scale_lower': lo,
            'Scale_upper': hi,
            'Treatments': group_to_treatments(group, effect_size)
        })

    return pd.DataFrame(rows)

def group_to_treatments(group, effect_size):
    return [
        {
            "Treatment": r["Treatment"],
            effect_size: r[effect_size],
            "direct": r.get("direct"),
            "Graph": r["Graph"],
            "indirect": r.get("indirect"),
            "p-value": r.get("p-value"),
            "Certainty": r["Certainty"],
            "direct_low": r.get("direct_lower"),
            "direct_up": r.get("direct_upper"),
            "indirect_low": r.get("indirect_lower"),
            "indirect_up": r.get("indirect_upper"),
            "CI_lower": r["CI_lower"],
            "CI_upper": r["CI_upper"],
            "pre_lower": r.get("pre_lower"),
            "pre_upper": r.get("pre_upper"),
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
    p_score = p_score.round(2)
    row_df = row_df.merge(
        p_score,
        left_on='Reference',
        right_on='treatment',
        how='left'
    )

    row_df = row_df.merge(
        range_ref_ab,
        left_on='Reference',
        right_on='treat',
        how='left'
    )

    row_df['risk_range'] = row_df.apply(
        lambda r: (
            f"from {int(r['min_value'])} to {int(r['max_value'])}"
            if pd.notna(r.get('min_value')) else ''
        ),
        axis=1
    )

    return row_df


def format_treatment_strings(row_df, effect_size):
    for j in range(len(row_df)):
        treatments = row_df.at[j, 'Treatments']

        for i in range(1, len(treatments)):
            t = treatments[i]
            # Main effect
            if not pd.isna(t.get(effect_size)):
                t[effect_size] = (
                    f"{t[effect_size]}\n({t['CI_lower']}, {t['CI_upper']})"
                )
            else:
                t[effect_size] = ""

            # Direct
            if not pd.isna(t.get('direct')):
                t['direct'] = (
                    f"{t['direct']}\n({t['direct_low']}, {t['direct_up']})"
                )
            else:
                t['direct'] = ""

            # Indirect
            if not pd.isna(t.get('indirect')):
                t['indirect'] = (
                    f"{t['indirect']}\n({t['indirect_low']}, {t['indirect_up']})"
                )
            else:
                t['indirect'] = ""



############################################################################

def Generate_advanced_columnDefs(effect_size):
    # Base definition for all columns, in the original order
    masterColumnDefs = [
        {
            "headerName": "Reference Treatment",
            "filter": True,
            "field": "Reference",
            "headerComponent": "HeaderWithIcon",
            "cellRenderer": "agGroupCellRenderer",
            'cellStyle': {'border-left': 'solid 0.8px', 'border-right': 'solid 0.8px'}
        },
        {"headerName": "P score\n(Ranking)", "field": "pscore", "editable": True,
         'cellStyle': {'border-right': 'solid 0.8px'}},
    ]

    # For RR, OR, HR, add these extra columns in order
    if effect_size in ['RR', 'OR', 'HR']:
        masterColumnDefs.extend([
            {"headerName": "Range of the risk\n(in dataset)", "field": "risk_range",
             "headerComponent": "HeaderWithIcon", "editable": True,
             'cellStyle': {'border-right': 'solid 0.8px'}},
            {"headerName": "Risk per 1000", "field": "risk", "editable": True,
             "headerComponent": "HeaderWithIcon",
             'cellStyle': {'color': 'grey', 'border-right': 'solid 0.8px'}},
            {"headerName": "The rationality of selecting the risk", "field": "rationality",
             "editable": True, "headerComponent": "HeaderWithIcon",
             'cellStyle': {'color': 'grey', 'border-right': 'solid 0.8px'}}
        ])

    # Columns always at the end
    masterColumnDefs.extend([
        {"headerName": "Scale lower\n(forestplots)", "field": "Scale_lower",
         "headerComponent": "HeaderWithIcon", "editable": True,
         'cellStyle': {'color': 'grey', 'border-right': 'solid 0.8px'}},
        {"headerName": "Scale upper\n(forestplots)", "field": "Scale_upper",
         "headerComponent": "HeaderWithIcon", "editable": True,
         'cellStyle': {'color': 'grey', 'border-right': 'solid 0.8px'}}
    ])

    return masterColumnDefs

############################################################################
def Generate_advanced_detailColumnDefs(effect_size):
    style_certainty = {
        'white-space': 'pre',
        'display': 'grid',
        'text-align': 'center',
        'align-items': 'center',
        'border-left': 'solid 0.8px'
    }

    style_mixed = {
        'border-left': 'solid 0.8px',
        # 'background-color': 'white',
        'text-align': 'center',
        'white-space': 'pre',
        'display': 'grid',
        'line-height': 'normal',
        'align-items': 'center'
    }

    def mixed_cell_style():
        return {
            "styleConditions": [
                {"condition": "params.value =='RR'", "style": style_mixed},
                {"condition": "params.data.CI_lower < 1 && params.data.CI_upper < 1", "style": {"color": "red", **style_mixed}},
                {"condition": "params.data.CI_lower > 1 && params.data.CI_upper > 1", "style": {"color": "red", **style_mixed}},
                {"condition": "!(params.data.CI_lower < 1 && params.data.CI_upper < 1) && !(params.data.CI_lower > 1 && params.data.CI_upper > 1)", "style": style_mixed}
            ]
        }

    # Columns common to all effect sizes
    detailColumnDefs = [
        {"field": "Treatment", "headerName": "Treatment", "sortable": False, "filter": True, "width": 130,
         "headerComponent": "HeaderWithIcon", "resizable": True,
         'cellStyle': {'display': 'grid', "text-align": 'center', 'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},

        {"field": effect_size, "headerName": "Mixed effect\n(95%CI)", "width": 180, "resizable": True,
         'cellStyle': mixed_cell_style()},

        {"field": "Graph", "cellRenderer": "DCC_GraphClickData", "headerName": "Forest plot",
         "headerComponent": "HeaderWithIcon", "width": 300, "resizable": True,
         'cellStyle': {'border-left': 'solid 0.8px', ''
         'border-right': 'solid 0.8px', 
        #  'background-color': 'white'
         }},

        {"field": "direct", "headerName": "Direct effect\n(95%CI)", "headerComponent": "HeaderWithIcon",
         "width": 170, "resizable": True,
         'cellStyle': {'color': '#707B7C', 'text-align': 'center', 'display': 'grid', 'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},

        {"field": "indirect", "headerName": "Indirect effect\n(95%CI)", "width": 170, "resizable": True,
         'cellStyle': {'color': '#ABB2B9', 'text-align': 'center', 'display': 'grid', 'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},

        {"field": "p-value", "headerName": "p-value\n(Consistency)", "width": 140, "resizable": True,
         'cellStyle': {'text-align': 'center', 'display': 'grid', 'line-height': 'normal', 'white-space': 'pre', 'align-items': 'center'}},

        {"field": "Certainty", "headerName": "Certainty", "headerComponent": "HeaderWithIcon", "filter": True,
         "width": 110, "resizable": True, "tooltipField": 'Certainty',
         "tooltipComponentParams": {"color": '#d8f0d3'}, "tooltipComponent": "CustomTooltip",
         'cellStyle': {"styleConditions": [
             {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},
             {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},
             {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}}
         ]}},

        {"field": "Comments", "width": 120, "headerComponent": "HeaderWithIcon", "resizable": True, "editable": True,
         'cellStyle': {'border-left': 'solid 0.5px', 'text-align': 'center', 'display': 'grid', 'border-right': 'solid 0.8px'}},
    ]

    if effect_size in ['RR', 'OR', 'HR']:
        detailColumnDefs.insert(2, {"field": "ab_difference", "headerName": "Absolute Difference",
                                    "headerComponent": "HeaderWithIcon", "width": 180, "resizable": True,
                                    'cellStyle': {'border-left': 'solid 0.8px', 
                                                #   'background-color': 'white',
                                                  'text-align': 'center', 'white-space': 'pre', 'display': 'grid',
                                                  'line-height': 'normal', 'align-items': 'center'}})

    return detailColumnDefs


import re
import pandas as pd

def _first_number(x):
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+", str(x))
    return float(m.group()) if m else None


def _change_abs_diff(change, rowData, effect_size):
    df = pd.DataFrame(rowData).reset_index(drop=True)
    row_idx = change["rowIndex"]
    base_risk = int(change["value"])

    df.at[row_idx, "risk"] = base_risk
    treatments = pd.DataFrame(df.at[row_idx, "Treatments"])

    for i in range(1, len(treatments)):
        eff = _first_number(treatments.at[i, effect_size])
        ci_lo = _first_number(treatments.at[i, "CI_lower"])
        ci_up = _first_number(treatments.at[i, "CI_upper"])

        if eff is None or ci_lo is None or ci_up is None:
            continue

        risk_t = int(base_risk * eff)
        diff = risk_t - base_risk
        sign = "more" if diff > 0 else "less"

        lo = int(base_risk * ci_lo) - base_risk
        up = int(base_risk * ci_up) - base_risk

        treatments.at[i, "ab_difference"] = (
            f"\n{abs(diff)} {sign} per 1000\n"
            f"({abs(lo)} to {abs(up)})"
        )

        for k in ["direct", "indirect"]:
            val = _first_number(treatments.at[i, k])
            lo_k = _first_number(treatments.at[i, f"{k}_low"])
            up_k = _first_number(treatments.at[i, f"{k}_up"])
            treatments.at[i, k] = (
                f"{val}\n({lo_k}, {up_k})" if val is not None else ""
            )

    df.at[row_idx, "Treatments"] = treatments.to_dict("records")
    return df.to_dict("records")

#############################################################################

import plotly.express as px, plotly.graph_objects as go

def update_indirect_direct(row):
    if pd.isna(row["direct"]):
        row["indirect"] = pd.NA
    elif pd.isna(row["indirect"]):
        row["direct"] = pd.NA
    return row


from dash import ctx

def update_kt_plots_scale(value_effect, value_change, lower, rowData, effect_size):
    df = pd.DataFrame(rowData)

    triggered = ctx.triggered_id

    # --------------------------------------------------
    # 1. value_effect changed → update ALL rows
    #    even if value_effect == []
    # --------------------------------------------------
    if triggered == "checklist_effects":
        for i in range(len(df)):
            row = df.iloc[i]

            row_scale_lower = _first_number(row.get("Scale_lower"))
            row_scale_upper = _first_number(row.get("Scale_upper"))

            df.iloc[i] = __kt_options_forstplot_row(
                value_effect,
                row,
                lower,
                row_scale_lower,
                row_scale_upper,
                effect_size
            )

    # --------------------------------------------------
    # 2. scale cell changed → update ONLY that row
    # --------------------------------------------------
    elif triggered == "quickstart-grid" and value_change and value_change[0]['colId']!= 'risk' and value_change[0]["value"] is not None:
        row_idx = value_change[0]["rowIndex"]
        col_id = value_change[0]["colId"]

        row = df.iloc[row_idx]

        row_scale_lower = _first_number(row.get("Scale_lower"))
        row_scale_upper = _first_number(row.get("Scale_upper"))

        # override with edited cell
        if col_id == "Scale_lower":
            row_scale_lower = _first_number(value_change[0]["value"])
        elif col_id == "Scale_upper":
            row_scale_upper = _first_number(value_change[0]["value"])

        df.iloc[row_idx] = __kt_options_forstplot_row(
            value_effect,
            row,
            lower,
            row_scale_lower,
            row_scale_upper,
            effect_size
        )

    return df.to_dict("records")


def __kt_options_forstplot_row(value_effect, row, lower, scale_lower, scale_upper, effect_size):
    treatments_orig = pd.DataFrame(row["Treatments"])  # keep original
    treatments = treatments_orig.copy()                # work on copy

    # Apply _first_number only to relevant numeric columns
    numeric_cols = [c for c in treatments.columns if c not in ("Graph", "Treatment")]
    for col in numeric_cols:
        treatments[col] = treatments[col].apply(_first_number)

    up_rng_max, low_rng_min = treatments.CI_upper.mean(), treatments.CI_lower.mean()
    up_mix_max, low_mix_min = treatments[effect_size].max(), treatments[effect_size].min()

    # Compute row-specific scale
    if scale_lower is not None and scale_upper is not None:
        range_scale = [np.log10(scale_lower), np.log10(scale_upper)] if effect_size in ["RR", "OR"] else [scale_lower, scale_upper]
    elif scale_lower is not None:
        range_scale = [np.log10(scale_lower), np.log10(max(up_rng_max, up_mix_max))] if effect_size in ["RR", "OR"] else [scale_lower, max(up_rng_max, up_mix_max)]
    elif scale_upper is not None:
        range_scale = [np.log10(min(low_rng_min, 0.1, low_mix_min)), np.log10(scale_upper)] if effect_size in ["RR", "OR"] else [min(low_rng_min, low_mix_min), scale_upper]
    else:
        range_scale = [np.log10(min(low_rng_min, 0.1, low_mix_min)), np.log10(max(up_rng_max, 10, up_mix_max))] if effect_size in ["RR", "OR"] else [min(low_rng_min, low_mix_min), max(up_rng_max, up_mix_max)]

    fig_template = go.Figure(go.Scatter(y=[], x=[]))

    tick0 = 10 ** range_scale[0] + 0.1
    tick_end = 10 ** range_scale[1] - 1

    tick_values1 = np.linspace(tick0, 1, num=5).round(2)
    tick_values2 = np.linspace(1, tick_end, num=5).astype(int)
    tick_values = np.concatenate((tick_values1, tick_values2[1:]))
    # Insert 1 at the beginning of the array
    # tick_values = np.insert(tick_values, 0, 1)
    # dtick=(tick_end - tick0) / 9
    fig_template.update_layout(
        xaxis=dict(
            range=range_scale,
            tickmode="auto",
            tickformat=".1f",
            # tickvals=tick_values
        ),
        dragmode=False,
        showlegend=False,
        yaxis_visible=False,
        yaxis_showticklabels=False,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
        plot_bgcolor="rgba(0,0,0,0)",
        height=100,
        margin=dict(l=0, r=0),
    )
    fig_template.update_xaxes(
        ticks="outside",
        type="log" if effect_size in ["RR", "OR"] else "linear",
        showgrid=False,
        # autorange=True,
        showline=True,
        # tickcolor='rgba(0,0,0,0)',
        linecolor="black",
    )

    treatments_orig.at[0, "Graph"] = fig_template
    num_line = len(value_effect) + 1

    for i in range(1, len(treatments)):
        filter_df = treatments.iloc[[i]].apply(update_indirect_direct, axis=1).reset_index(drop=True)
        filter_df["CI_width_hf"] = ""
        filter_df["lower_error"] = ""
        filter_df["name"] = ""

        CI_upper = filter_df['CI_upper'][0]
        CI_lower = filter_df['CI_lower'][0]
        filter_df.at[0, "CI_width_hf"] = CI_upper - filter_df[f"{effect_size}"][0]
        filter_df.at[0, "lower_error"] = filter_df[f"{effect_size}"][0] - CI_lower
        filter_df = pd.concat([filter_df] * num_line, ignore_index=True)
    
        for index, value in enumerate(reversed(value_effect)):
            if value == "PI":
                CI_upper = filter_df["pre_upper"][index]
                CI_lower = filter_df["pre_lower"][index]
                filter_df["CI_width_hf"][index] = CI_upper - filter_df[effect_size][index]
                filter_df["lower_error"][index] = filter_df[effect_size][index] - CI_lower
                filter_df["name"][index] = "PI"
            else:
                filter_df["Treatment"][index] = value
                filter_df[effect_size][index] = filter_df[value][index]
                filter_df["CI_width_hf"][index] = filter_df[f"{value}_up"][index] - filter_df[value][index]
                filter_df["lower_error"][index] = filter_df[value][index] - filter_df[f"{value}_low"][index]
                filter_df["name"][index] = value
          
        colors = {
                "indirect": "#ABB2B9",
                "direct": "#707B7C",
                "PI": "red",
                "other": "black",
            }

        hovert_template = {
            "indirect": "indirect estimate with CI" + "<extra></extra>",
            "direct": "direct estimate with CI" + "<extra></extra>",
            "PI": "mixed estimate with CI & PI" + "<extra></extra>",
            "other": "mixed estimate with CI & PI" + "<extra></extra>",
        }
        
        fig = go.Figure()
        for idx in range(filter_df.shape[0]):
            data_point = filter_df.iloc[idx]
            value = data_point[f"{effect_size}"]
            if pd.isna(value):
                continue
            name = data_point["name"]
            (
                fig.add_trace(
                    go.Scatter(
                        x=[data_point[f"{effect_size}"]],
                        y=[data_point["Treatment"]],
                        # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                        error_x=dict(
                            type="data",
                            color=colors[name]
                            if name in colors
                            else colors["other"],
                            array=[data_point["CI_width_hf"]],
                            arrayminus=[data_point["lower_error"]],
                            visible=True,
                        ),
                        marker=dict(
                            color=colors[name]
                            if name in colors
                            else colors["other"],
                            size=8,
                        ),
                        showlegend=False,
                        hovertemplate=hovert_template[name]
                        if name in hovert_template
                        else hovert_template["other"],
                    )
                ),
            )
            fig.update_xaxes(
                ticks="outside",
                type="log" if effect_size in ["RR", "OR"] else "linear",
                range=range_scale,
            )

        fig.update_layout(
            barmode="group",
            bargap=0.25,
            xaxis=dict(range=range_scale, type="log" if effect_size in ["RR", "OR"] else "linear"),
            # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            xaxis_visible=False,
            xaxis_showticklabels=False,
            margin=dict(l=0, r=0, t=0, b=0),
            autosize=True,
            height=80,  # Set the height to 82 pixels
            # width=200,  # Set the width to 200 pixels
            shapes=[
                dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=f"{1/(1-lower)}" if effect_size in ["RR", "OR"] else f"{lower}",
                    y0="0",
                    x1=f"{1-lower}" if effect_size in ["RR", "OR"] else f"{-lower}",
                    y1="1",
                    fillcolor="orange",
                    opacity=0.4,
                    line_width=0,
                    layer="below",
                ),
            ],
            # template="plotly_dark",
        )

        fig.add_trace(
            go.Scatter(
                x=[1/(1-lower), 1-lower] if effect_size in ["RR", "OR"] else [0 - lower, 0 + lower],  # x-coordinate in the middle of the shape
                y=[
                    0,
                    0,
                ],  # y-coordinate (doesn't matter, since it's vertical shape)
                mode="markers",
                marker=dict(color="rgba(0, 0, 0, 0)", size=5),
                hovertemplate="<b>Range of equivalence</b>: %{x} <extra></extra>",
                hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)"),
            )
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
            plot_bgcolor="rgba(0,0,0,0)",
        )

        fig.add_shape(
            type="line",
            yref="paper",
            y0=0,
            y1=1,
            xref="x",
            x0=1 if effect_size in ["RR", "OR"] else 0,
            x1=1 if effect_size in ["RR", "OR"] else 0,
            line=dict(color="green", width=2, dash="dot"),
            layer="below",
        )

        treatments_orig.at[i, "Graph"] = fig

    row["Treatments"] = treatments_orig.to_dict("records")
    return row
