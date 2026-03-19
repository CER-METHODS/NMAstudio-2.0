import plotly.express as px, plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
import numpy as np
import re


def _parse_first_numeric(val):
    """
    Extract the first numeric token from `val` and return as float, or None.
    Accepts formats like "1.23 (0.45, 2.34)", "1.23", "-0.5e-1".
    """
    if val is None:
        return None
    s = str(val)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None



def display_modal_barplot(cell, value, rowdata):
    if cell is None or len(cell) == 0:
        return go.Figure(data=[], layout={}), html.P(""), {"display": "none"}, {"display": "none"}

    rowdata = pd.DataFrame(rowdata)

    if not (
        "colId" in cell
        and re.fullmatch(r"(RR|OR|MD|SMD)_out\d+(?:_label)?", str(cell["colId"]))
        and cell.get("value") is not None
    ):
        return go.Figure(data=[], layout={}), html.P(""), {"display": "none"}, {"display": "none"}

    colid = str(cell["colId"])
    m = re.search(r"(RR|OR|MD|SMD)_out\d+", colid)
    metric = m.group(1)

    row_idx = cell["rowIndex"]
    treatment = rowdata.loc[row_idx, "Treatment"]
    compare = rowdata.loc[row_idx, "Reference"]
    header = html.P(f"{treatment} VS {compare}")

    # Only display barplot for RR/OR metrics
    if metric not in ["RR", "OR"]:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return empty_fig, header, {"display": "none"}, {"display": "none"}

    first_part = cell["value"].split("\n")[0]
    effect = _parse_first_numeric(first_part)

    if value is None:
        value = 20
    value = float(value)

    # ---------- RR / OR ----------
    if metric in ["RR", "OR"]:
        ab_treat = int(effect * value)

        x_data = [ab_treat, int(value)]
        y_data = [treatment, compare]

        annotations = []
        for y, x in zip(y_data, x_data):
            annotations.append(
                dict(
                    x=500,
                    y=y,
                    xref="x",
                    yref="y",
                    text=f"{x} per 1000",
                    showarrow=False,
                    font=dict(size=14),
                )
            )

    # ---------- MD / SMD ----------
    else:
        comp_val = value
        treat_val = value + effect

        x_data = [treat_val, comp_val]
        y_data = [treatment, compare]

        annotations = []
        for y, x in zip(y_data, x_data):
            annotations.append(
                dict(
                    x=x,
                    y=y,
                    xref="x",
                    yref="y",
                    text=f"{x:.2f}",
                    showarrow=False,
                    font=dict(size=14),
                )
            )

    fig = go.Figure()

    # --- gray background bar (1000) ---
    if metric in ["RR", "OR"]:
        fig.add_bar(
            x=[1000, 1000],
            y=y_data,
            orientation="h",
            marker_color="lightgray",
            opacity=1,
            hoverinfo="skip",
        )

    # --- actual values bar ---
    fig.add_bar(
        x=x_data,
        y=y_data,
        orientation="h",
        marker_color=["rgb(241,197,13)", "rgb(128,191,69)"],
    )


    fig.update_layout(
        showlegend=False,
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        width=350,
        height=150,
        autosize=True,
        bargap=0.3,
        annotations=annotations,
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 1000] if metric in ["RR", "OR"] else None,
        ),
        yaxis=dict(showgrid=False, showline=False),
    )


    return fig, header, {"display": "block"}, {"display": "block"}



# def display_modal_text(cell, value, rowdata, outcome_names):
#     if cell is None or len(cell) == 0:
#         # risk_range = html.P("")
#         info_col = html.Span("")
#         return info_col

#     rowdata = pd.DataFrame(rowdata)
#     if (
#         'colId' in cell
#         and re.fullmatch(r"(RR|OR|MD|SMD)_out\d+(?:_label)?", str(cell['colId']))
#         and cell.get('value') is not None
#     ):
#         row_idx = cell["rowIndex"]

#         if value:
#             value = int(value)
#         else:
#             value = 20

#         colid = str(cell.get("colId"))
#         # Determine outcome index from column id (expects RR_outN_label)
#         m = re.search(r"(RR|OR|MD|SMD)_out(\d+)(?:_label)?", colid)
#         idx = int(m.group(2)) if m else 1

#         # Resolve outcome display name from outcome_names if provided
#         try:
#             if outcome_names and len(outcome_names) >= idx and outcome_names[idx - 1]:
#                 out = outcome_names[idx - 1]
#             else:
#                 out = f"Outcome {idx}"
#         except Exception:
#             out = f"Outcome {idx}"

#         # Outcome-specific CI columns
#         rr_low_col = f"CI_lower_out{idx}"
#         rr_up_col = f"CI_upper_out{idx}"

#         rr_low = rowdata.loc[row_idx, rr_low_col] if rr_low_col in rowdata.columns else None
#         rr_up = rowdata.loc[row_idx, rr_up_col] if rr_up_col in rowdata.columns else None

#         first_part = cell["value"].split("\n")[0]
#         rr = _parse_first_numeric(first_part)

#         treatment = rowdata.loc[row_idx, "Treatment"]
#         compare = rowdata.loc[row_idx, "Reference"]

#         ab_treat = int(rr * value) if rr is not None else 0
#         ab_diff = ab_treat - value
#         span_diff = (
#             f"{ab_diff} more per 1000"
#             if ab_diff > 0
#             else f"{abs(ab_diff)} less per 1000"
#         )

#         ab_diff_low = int(rr_low * value) - value if rr_low is not None else 0
#         span_diff_low = (
#             f"{ab_diff_low} more per 1000"
#             if ab_diff_low > 0
#             else f"{abs(ab_diff_low)} less per 1000"
#         )

#         ab_diff_up = int(rr_up * value) - value if rr_up is not None else 0
#         span_diff_up = (
#             f"{ab_diff_up} more per 1000"
#             if ab_diff_up > 0
#             else f"{abs(ab_diff_up)} less per 1000"
#         )

#     else:
#         return ""

#     span1 = html.Span(f"Outcome: {out}", className="skt_span_info2", id="modal_out_name")
#     span2 = html.Span(
#         f"Treatment: {treatment}", className="skt_span_info2", id="standard_treat"
#     )
#     span3 = html.Span(
#         f"Comparator: {compare}", className="skt_span_info2", id="standard_com"
#     )
#     span4 = html.Span(
#         f"Absolute difference: {span_diff}", className="skt_span_info2", id="standard_abs"
#     )
#     span5 = html.Span(
#         f"CI: {span_diff_low} to {span_diff_up}",
#         className="skt_span_info2",
#         id="standard_ci",
#     )
#     children = [span1, span2, span3, span4, span5]

#     return children


def display_modal_text(cell, value, rowdata, outcome_names, net_data):
    if cell is None or len(cell) == 0:
        return html.P(""), html.Span("")

    rowdata = pd.DataFrame(rowdata)

    if not (
        "colId" in cell
        and re.fullmatch(r"(RR|OR|MD|SMD)_out\d+(?:_label)?", str(cell["colId"]))
        and cell.get("value") is not None
    ):
        return "","",""

    row_idx = cell["rowIndex"]

    if value:
        value = float(value)
    else:
        value = 20

    colid = str(cell.get("colId"))
    m = re.search(r"(RR|OR|MD|SMD)_out(\d+)(?:_label)?", colid)
    metric = m.group(1)
    idx = int(m.group(2)) if m else 1

    # outcome name
    try:
        if outcome_names and len(outcome_names) >= idx and outcome_names[idx - 1]:
            out = outcome_names[idx - 1]
        else:
            out = f"Outcome {idx}"
    except Exception:
        out = f"Outcome {idx}"

    # CI columns
    low_col = f"CI_lower_out{idx}"
    up_col = f"CI_upper_out{idx}"

    rr_low = rowdata.loc[row_idx, low_col] if low_col in rowdata.columns else None
    rr_up = rowdata.loc[row_idx, up_col] if up_col in rowdata.columns else None

    first_part = cell["value"].split("\n")[0]
    rr = _parse_first_numeric(first_part)

    treatment = rowdata.loc[row_idx, "Treatment"]
    compare = rowdata.loc[row_idx, "Reference"]

    children = [
        html.Span(f"Outcome: {out}", className="skt_span_info2", id="modal_out_name"),
        html.Span(
            f"Treatment: {treatment}", className="skt_span_info2", id="standard_treat"
        ),
        html.Span(
            f"Comparator: {compare}", className="skt_span_info2", id="standard_com"
        ),
    ]

    # -------- RR / OR --------
    if metric in ["RR", "OR"]:
        from tools.skt_data_helpers import compute_reference_ranges
        from tools.utils import get_net_data_json
        # Load modal data
        net_dat = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
        range_ref_ab = compute_reference_ranges(net_dat, idx-1)
        min_val = int(range_ref_ab[range_ref_ab['treat'] == compare]['min_value'].values[0])
        max_val = int(range_ref_ab[range_ref_ab['treat'] == compare]['max_value'].values[0])
        range_text = html.P(f"The risk of {compare} ranges from {min_val} to {max_val} per 1000 in the dataset.")

        enter_label = html.P(f"Enter the risk for {compare} (per 1000):")
        ab_treat = int(rr * value) if rr is not None else 0
        ab_diff = ab_treat - value

        span_diff = (
            f"{ab_diff} more per 1000"
            if ab_diff > 0
            else f"{abs(ab_diff)} less per 1000"
        )

        ab_diff_low = int(rr_low * value) - value if rr_low is not None else 0
        ab_diff_up = int(rr_up * value) - value if rr_up is not None else 0

        span_diff_low = (
            f"{ab_diff_low} more per 1000"
            if ab_diff_low > 0
            else f"{abs(ab_diff_low)} less per 1000"
        )
        span_diff_up = (
            f"{ab_diff_up} more per 1000"
            if ab_diff_up > 0
            else f"{abs(ab_diff_up)} less per 1000"
        )

        children.extend(
            [
                html.Span(
                    f"Absolute difference: {span_diff}",
                    className="skt_span_info2",
                    id="standard_abs",
                ),
                html.Span(
                    f"CI: {span_diff_low} to {span_diff_up}",
                    className="skt_span_info2",
                    id="standard_ci",
                ),
            ]
        )

    # -------- MD / SMD --------
    else:
        range_text = html.P("")
        enter_label = html.P(f"Enter a value for {compare}:")
        children.extend(
            [
                html.Span(
                    f"{metric}: {rr}",
                    className="skt_span_info2",
                    id="standard_effect",
                ),
                html.Span(
                    f"CI: {rr_low.round(2)} to {rr_up.round(2)}",
                    className="skt_span_info2",
                    id="standard_ci",
                ),
            ]
        )

    return  children, enter_label, range_text



def display_modal_data(cell, rowdata, df_modal, m):
    # Convert rowdata to DataFrame
    rowdata = pd.DataFrame(rowdata)

    metric = m.group(1)
    idx = int(m.group(2))

    # Parse the numeric value from the clicked cell (if needed)
    rr_clicked = _parse_first_numeric(cell.get("value"))

    row_idx = cell["rowIndex"]
    treatment = rowdata.loc[row_idx, "Treatment"]
    compare = rowdata.loc[row_idx, "Reference"]

    # Filter df_modal based on selected treatments and comparisons
    filtered_df = df_modal[
        ((df_modal["treat1"] == treatment) & (df_modal["treat2"] == compare))
        | ((df_modal["treat1"] == compare) & (df_modal["treat2"] == treatment))
    ]

    # Determine TE and seTE column names for this outcome index
    te_col = f"TE{idx}"
    se_col = f"seTE{idx}"

    if te_col not in filtered_df.columns or se_col not in filtered_df.columns:
        # nothing to compute
        return filtered_df.to_dict("records")

    # compute point estimate and CI depending on metric
    filtered_df = filtered_df[filtered_df[te_col].notna()].copy()
    filtered_df["TE_up"] = filtered_df[te_col] + 1.96 * filtered_df[se_col]
    filtered_df["TE_low"] = filtered_df[te_col] - 1.96 * filtered_df[se_col]

    # Use metric-specific column names (e.g., 'OR', 'OR_up', 'OR_low' or 'MD', 'MD_up', 'MD_low')
    eff = metric
    eff_up = f"{metric}_up"
    eff_low = f"{metric}_low"

    if metric in ("RR", "OR"):
        # TE is log-scale -> exponentiate
        filtered_df[eff] = np.exp(filtered_df[te_col])
        filtered_df[eff_up] = np.exp(filtered_df["TE_up"])
        filtered_df[eff_low] = np.exp(filtered_df["TE_low"])
    else:
        # MD / SMD: leave on original scale
        filtered_df[eff] = filtered_df[te_col]
        filtered_df[eff_up] = filtered_df["TE_up"]
        filtered_df[eff_low] = filtered_df["TE_low"]

    # Adjust rows where 'treat1' and 'treat2' need to be swapped
    mask = (filtered_df["treat1"] == compare) & (filtered_df["treat2"] == treatment)
    if mask.any():
        filtered_df.loc[mask, ["treat1", "treat2"]] = filtered_df.loc[
            mask, ["treat2", "treat1"]
        ].values

        # For RR/OR (log scale): negate log-TE values for swapped arms, then
        # recompute metric-specific effect columns on the appropriate scale.
        if metric in ("RR", "OR"):
            for col in [te_col, "TE_up", "TE_low"]:
                filtered_df.loc[mask, col] = -filtered_df.loc[mask, col]

            # Recompute effects for masked rows
            filtered_df.loc[mask, eff] = np.exp(filtered_df.loc[mask, te_col])
            filtered_df.loc[mask, eff_up] = np.exp(filtered_df.loc[mask, "TE_up"])
            filtered_df.loc[mask, eff_low] = np.exp(filtered_df.loc[mask, "TE_low"])
        else:
            # MD / SMD: invert sign for swapped arms
            for col in [te_col, "TE_up", "TE_low", eff, eff_up, eff_low]:
                filtered_df.loc[mask, col] = -filtered_df.loc[mask, col]

    # Create a display CI column `RR_ci` for compatibility with the UI,
    ci_col = f"{metric}_ci"

    if not filtered_df.empty:
        def _format_ci(row):
            try:
                val = row.get(eff)
                lo = row.get(eff_low)
                hi = row.get(eff_up)
                return f"{round(val,2)}\n({round(lo,2)} to {round(hi,2)})"
            except Exception:
                return ""

        filtered_df[ci_col] = filtered_df.apply(_format_ci, axis=1)
    else:
        filtered_df[ci_col] = pd.Series(dtype="str")

    # Replace 'bias' values with descriptive terms
    filtered_df["rob"] = filtered_df["rob"].replace(
        {1: "Low", 2: "Moderate", 3: "High"}
    )

    # Add 'ntc' and 'link' columns
    # filtered_df["ntc"] = "NTC00001"
    filtered_df["link"] = (
        "https://www.nejm.org/doi/10.1056/NEJMoa1314258?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%20%200www.ncbi.nlm.nih.gov"
    )
    # filtered_df.to_csv("db/skt/modal_debug.csv", index=False)
    # Return the filtered DataFrame as a dictionary
    return filtered_df.to_dict("records")



def display_modal_column( m, effect_modifiers, df_modal):
    metric = m.group(1)
    ci_col = f"{metric}_ci"
    style_certainty = {
        "white-space": "pre",
        "display": "grid",
        "text-align": "center",
        "alignItems": "center",
        "border-left": "solid 0.8px",
    }


    modal_treat_compare = [
   
        {"headerName": "Study", 
        "field": "studlab",
        "suppressHeaderMenuButton": True,
        "editable": False,
        "resizable": False,
        'cellStyle': {
            'background-color': '#ffecb3',
            },
        # "cellRenderer": "StudyLink",
        },
        

        {"headerName": f"{metric}", 
        "field": f"{ci_col}",
        "suppressHeaderMenuButton": True,
        "editable": False,
        "resizable": False,
        'cellStyle': {
            'background-color': '#ffecb3',
            }
        },
        
        {"headerName": "Study size", 
        "field": "sample_size",
        "suppressHeaderMenuButton": True,
        "editable": False,
        "resizable": False,
        'cellStyle': {
            'background-color': '#ffecb3',
            }
        },
    ]
    df_modal = pd.DataFrame(df_modal)
    
    for eff_mod in effect_modifiers:
        if eff_mod in df_modal.columns:
            field = eff_mod
        elif f"{eff_mod}1" in df_modal.columns:
            field = f"{eff_mod}1"
        else:
            continue 
            
        modal_treat_compare.append(
            {
                "headerName": eff_mod,
                "field": field,
                "suppressHeaderMenuButton": True,
                "editable": False,
                "resizable": False,
                'cellStyle': {
                    'background-color': '#ffecb3',
                    }
            }
        )

   
    modal_treat_compare.append(       
            {"headerName": "Risk of bias", 
            "field": "rob",
            "suppressHeaderMenuButton": True,
            "editable": False,
            "resizable": False,
            'cellStyle':{
                        "styleConditions": [
                        {"condition": "params.value == 'High'", "style": {"backgroundColor": "#B85042", **style_certainty}},   
                        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},
                        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
                            ]}
            }
        )


    return modal_treat_compare