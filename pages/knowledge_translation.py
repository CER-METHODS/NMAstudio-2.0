# Knowledge Translation Page
# Ported from NMAstudio-app-main/tools/layouts_KT.py

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.exceptions import PreventUpdate

from tools.skt_layout import (
    Sktpage,
    switch_table,
    skt_layout,
    skt_nonexpert,
    model_transitivity,
    model_skt_stand1,
    model_skt_stand2,
    model_skt_compare_simple,
    model_fullname,
    model_ranking,
    grid,
    row_data,
    row_data_default,
)
from tools.skt_table import treat_compare_grid, modal_compare_grid
from tools.functions_skt_others import (
    get_skt_elements,
    skt_stylesheet,
    __generate_skt_stylesheet,
    __generate_skt_stylesheet2,
)
from tools.functions_skt_boxplot import __show_boxplot, __show_scatter
from tools.functions_skt_abs_forest import __Change_Abs
from assets.cytoscape_styleesheeet import get_stylesheet

# Navbar is added globally in app.py, not needed here
from tools.skt_data_helpers import (
    get_skt_network_elements,
    get_skt_two_outcome_data,
    build_skt_advanced_row_data,
    get_skt_network_data,
    get_effect_modifier_data,
)
import pandas as pd
import numpy as np
from io import StringIO

# Register page with Dash
dash.register_page(
    __name__, path="/knowledge-translation", name="Knowledge Translation"
)

# Page layout with redirect support
layout = html.Div(
    id="kt_page",
    children=[
        # Hidden location component for redirects when results are reset
        dcc.Location(id="kt_page_location", refresh=True),
        # Placeholder shown when results are not ready
        # Note: Navbar is added globally in app.py, no need to add here
        html.Div(
            id="kt_not_ready_placeholder",
            style={"display": "none"},
            children=[
                html.Div(
                    [
                        html.H3(
                            "No Results Available",
                            style={
                                "text-align": "center",
                                "color": "#5c7780",
                                "margin-top": "100px",
                            },
                        ),
                        html.P(
                            "Please upload and process your data in the Setup page first.",
                            style={
                                "text-align": "center",
                                "color": "#5c7780",
                                "font-size": "16px",
                            },
                        ),
                        html.Div(
                            dbc.Button(
                                "Go to Setup",
                                href="/setup",
                                color="primary",
                                style={"margin-top": "20px"},
                            ),
                            style={"text-align": "center"},
                        ),
                    ]
                ),
            ],
        ),
        # Main KT content - uses Sktpage layout from skt_layout.py
        # Note: Navbar is added globally in app.py, no need to add here
        html.Div(
            id="kt_main_content",
            style={"display": "none"},
            children=[Sktpage()],
        ),
    ],
)


# ================================
# CALLBACKS FOR KNOWLEDGE TRANSLATION PAGE
# ================================


# Toggle between Standard and Advanced versions
@callback(
    Output("skt_sub_content", "children"),
    Input("toggle_grid_select", "value"),
    prevent_initial_call=True,
)
def toggle_skt_version(toggle_value):
    """Switch between Standard (non-expert) and Advanced (expert) versions."""
    if toggle_value:
        return skt_layout()
    else:
        return skt_nonexpert()


# Transitivity modal toggle
@callback(
    Output("modal_transitivity", "is_open"),
    [Input("trans_button", "n_clicks"), Input("close_trans", "n_clicks")],
    [State("modal_transitivity", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_transitivity(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Transitivity boxplot/scatter update
@callback(
    Output("boxplot_skt", "figure"),
    [Input("ddskt-trans", "value"), Input("box_kt_scatter", "value")],
    prevent_initial_call=True,
)
def update_transitivity_plot(effect_modifier, scatter_toggle):
    """Update the transitivity check boxplot/scatter plot."""
    if scatter_toggle:
        return __show_scatter(effect_modifier)
    else:
        return __show_boxplot(effect_modifier)


# Pairwise forest plot modal toggle
@callback(
    Output("modal_forest", "is_open"),
    [Input("close_forest", "n_clicks")],
    [State("modal_forest", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_forest(n_close, is_open):
    if n_close:
        return False
    return is_open


# Detail comparison modal toggle (Advanced version)
@callback(
    Output("skt_modal_copareinfo", "is_open"),
    [Input("close_compare", "n_clicks")],
    [State("skt_modal_copareinfo", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_compare(n_close, is_open):
    if n_close:
        return False
    return is_open


# Simple comparison modal toggle (Standard version)
@callback(
    Output("skt_modal_compare_simple", "is_open"),
    [
        Input("close_compare_simple", "n_clicks"),
        Input("grid_treat_compare", "cellClicked"),
    ],
    [State("skt_modal_compare_simple", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_compare_simple(n_close, cell_clicked, is_open):
    triggered_id = ctx.triggered_id
    if triggered_id == "close_compare_simple":
        return False
    elif triggered_id == "grid_treat_compare" and cell_clicked:
        # Open modal when clicking on RR or Certainty columns
        col_id = cell_clicked.get("colId", "")
        if col_id in ["RR", "RR_out2", "Certainty_out1", "Certainty_out2"]:
            return True
    return is_open


# Switch treatment and comparator in standard grid
@callback(
    Output("grid_treat_compare", "rowData"),
    Input("grid_treat_compare", "cellClicked"),
    State("grid_treat_compare", "rowData"),
    prevent_initial_call=True,
)
def switch_treatment_comparator(cell_clicked, row_data_current):
    """Switch treatment and comparator when clicking the switch button."""
    if not cell_clicked:
        raise PreventUpdate

    col_id = cell_clicked.get("colId", "")
    if col_id != "switch":
        raise PreventUpdate

    row_index = cell_clicked.get("rowIndex")
    if row_index is None:
        raise PreventUpdate

    # Get original data
    df = pd.DataFrame(row_data_current)

    # Swap Treatment and Reference for the clicked row
    treatment = df.loc[row_index, "Treatment"]
    reference = df.loc[row_index, "Reference"]
    df.loc[row_index, "Treatment"] = reference
    df.loc[row_index, "Reference"] = treatment

    # Invert RR values
    # Parse RR string to get values
    rr_str = df.loc[row_index, "RR"]
    rr_out2_str = df.loc[row_index, "RR_out2"]

    try:
        # Parse "value\n(lower to upper)" format
        import re

        match1 = re.match(r"([\d.]+)\n\(([\d.]+) to ([\d.]+)\)", rr_str)
        if match1:
            rr = float(match1.group(1))
            lower = float(match1.group(2))
            upper = float(match1.group(3))
            inv_rr = round(1 / rr, 2)
            inv_lower = round(1 / upper, 2)
            inv_upper = round(1 / lower, 2)
            df.loc[row_index, "RR"] = f"{inv_rr}\n({inv_lower} to {inv_upper})"

        match2 = re.match(r"([\d.]+)\n\(([\d.]+) to ([\d.]+)\)", rr_out2_str)
        if match2:
            rr2 = float(match2.group(1))
            lower2 = float(match2.group(2))
            upper2 = float(match2.group(3))
            inv_rr2 = round(1 / rr2, 2)
            inv_lower2 = round(1 / upper2, 2)
            inv_upper2 = round(1 / lower2, 2)
            df.loc[row_index, "RR_out2"] = f"{inv_rr2}\n({inv_lower2} to {inv_upper2})"
    except Exception:
        pass

    return df.to_dict("records")


# Cytoscape stylesheet update for Standard version (cytoscape_skt2)
@callback(
    Output("cytoscape_skt2", "stylesheet"),
    [
        Input("cytoscape_skt2", "tapNode"),
        Input("cytoscape_skt2", "selectedNodeData"),
        Input("cytoscape_skt2", "selectedEdgeData"),
    ],
    [State("cytoscape_skt2", "elements")],
    prevent_initial_call=True,
)
def update_stylesheet_skt2(node, slct_nodesdata, slct_edgedata, elements):
    """Update cytoscape stylesheet when nodes/edges are selected."""
    if not elements:
        raise PreventUpdate
    return __generate_skt_stylesheet2(node, slct_nodesdata, elements, slct_edgedata)


# Filter grid based on selected nodes/edges in Standard version
@callback(
    Output("grid_treat_compare", "rowData", allow_duplicate=True),
    [
        Input("cytoscape_skt2", "selectedNodeData"),
        Input("cytoscape_skt2", "selectedEdgeData"),
    ],
    [
        State("grid_treat_compare", "rowData"),
        State("forest_data_STORAGE", "data"),
        State("cinema_net_data_STORAGE", "data"),
        State("outcome_names_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def filter_grid_by_network(
    slct_nodesdata,
    slct_edgedata,
    current_row_data,
    forest_storage,
    cinema_storage,
    outcome_names,
):
    """Filter the treatment comparison grid based on network selection."""
    # Get full data from STORAGE (instead of df_origin which is now empty)
    if not forest_storage:
        raise PreventUpdate

    try:
        df_full = get_skt_two_outcome_data(
            forest_storage, cinema_storage, outcome_names
        )
        if df_full.empty:
            raise PreventUpdate
    except Exception:
        raise PreventUpdate

    df = df_full.copy()

    if slct_nodesdata and len(slct_nodesdata) > 0:
        selected_nodes = [d["id"] for d in slct_nodesdata]
        # Filter rows where Treatment or Reference is in selected nodes
        mask = df["Treatment"].isin(selected_nodes) | df["Reference"].isin(
            selected_nodes
        )
        df = df[mask]

    if slct_edgedata and len(slct_edgedata) > 0:
        # Filter based on selected edges
        filtered_rows = []
        for edge in slct_edgedata:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                mask = ((df["Treatment"] == source) & (df["Reference"] == target)) | (
                    (df["Treatment"] == target) & (df["Reference"] == source)
                )
                filtered_rows.append(df[mask])
        if filtered_rows:
            df = pd.concat(filtered_rows).drop_duplicates()

    if df.empty:
        # Return full data if no filter matches
        return df_full.to_dict("records")

    return df.to_dict("records")


# Advanced version callbacks (when expert toggle is on)


# Update quickstart-grid based on effect options and risk values
@callback(
    Output("quickstart-grid", "rowData", allow_duplicate=True),
    [
        Input("checklist_effects", "value"),
        Input("range_lower", "value"),
        Input("quickstart-grid", "cellValueChanged"),
    ],
    [State("quickstart-grid", "rowData")],
    prevent_initial_call=True,
)
def update_advanced_grid(value_effect, lower, value_change, rowData):
    """Update the advanced grid with forest plots and absolute values."""
    if not rowData:
        raise PreventUpdate

    try:
        lower = float(lower) if lower else 0.2
    except ValueError:
        lower = 0.2

    if not value_effect:
        value_effect = []

    return __Change_Abs(value_effect, value_change, lower, rowData)


# Cytoscape stylesheet update for Advanced version (cytoscape_skt)
@callback(
    Output("cytoscape_skt", "stylesheet"),
    [
        Input("cytoscape_skt", "tapNode"),
        Input("cytoscape_skt", "selectedNodeData"),
        Input("cytoscape_skt", "selectedEdgeData"),
        Input("kt2_nclr", "children"),
        Input("kt2_eclr", "children"),
        Input("kt2_nclr_custom", "value"),
        Input("kt2_eclr_custom", "value"),
        Input("kt2_nds", "children"),
        Input("kt2_egs", "children"),
    ],
    [State("cytoscape_skt", "elements")],
    prevent_initial_call=True,
)
def update_stylesheet_skt(
    node,
    slct_nodesdata,
    slct_edgedata,
    dd_nclr,
    dd_eclr,
    custom_nd_clr,
    custom_edg_clr,
    dd_nds,
    dd_egs,
    elements,
):
    """Update cytoscape stylesheet for advanced version."""
    if not elements:
        raise PreventUpdate

    # Use default values if dropdowns not set
    dd_nclr = dd_nclr or "Default"
    dd_eclr = dd_eclr or "Default"
    dd_nds = dd_nds or "Default"
    dd_egs = dd_egs or "Number of studies"

    return __generate_skt_stylesheet(
        node,
        slct_nodesdata,
        elements,
        slct_edgedata,
        dd_nclr,
        dd_eclr,
        custom_nd_clr,
        custom_edg_clr,
        dd_nds,
        dd_egs,
    )


# Cytoscape layout change for Standard version
@callback(
    Output("cytoscape_skt2", "layout"),
    Input("kt-graph-layout-dropdown", "children"),
    prevent_initial_call=True,
)
def update_cytoscape_layout_skt2(layout_name):
    if not layout_name:
        raise PreventUpdate
    return {"name": layout_name.lower(), "animate": False, "fit": True}


# Cytoscape layout change for Advanced version
@callback(
    Output("cytoscape_skt", "layout"),
    Input("kt2-graph-layout-dropdown", "children"),
    prevent_initial_call=True,
)
def update_cytoscape_layout_skt(layout_name):
    if not layout_name:
        raise PreventUpdate
    return {"name": layout_name.lower(), "animate": False, "fit": True}


# FAQ toggle callbacks
@callback(
    Output("faq_toast", "is_open"),
    [Input("faq_button", "n_clicks"), Input("close_faq", "n_clicks")],
    [State("faq_toast", "is_open")],
    prevent_initial_call=True,
)
def toggle_faq_toast(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# FAQ collapse callbacks
@callback(
    Output("faq_ans1", "is_open"),
    Input("faq_ques1", "n_clicks"),
    State("faq_ans1", "is_open"),
    prevent_initial_call=True,
)
def toggle_faq1(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("faq_ans2", "is_open"),
    Input("faq_ques2", "n_clicks"),
    State("faq_ans2", "is_open"),
    prevent_initial_call=True,
)
def toggle_faq2(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


# Fullname modal toggle
@callback(
    Output("skt_modal_fullname_simple", "is_open"),
    [Input("fullname_button", "n_clicks"), Input("close_fullname_simple", "n_clicks")],
    [State("skt_modal_fullname_simple", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_fullname(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# Ranking modal toggle
@callback(
    Output("modal_ranking", "is_open"),
    [Input("ranking_button", "n_clicks"), Input("close_rank", "n_clicks")],
    [State("modal_ranking", "is_open")],
    prevent_initial_call=True,
)
def toggle_modal_ranking(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open


# ================================
# PAGE VISIBILITY & REDIRECT CALLBACKS
# ================================


@callback(
    [
        Output("kt_not_ready_placeholder", "style"),
        Output("kt_main_content", "style"),
    ],
    Input("results_ready_STORAGE", "data"),
    prevent_initial_call=False,
)
def toggle_kt_page_visibility(results_ready):
    """
    Show/hide the KT page content based on results_ready_STORAGE.
    When results are not ready, show placeholder message.
    When results are ready, show the actual KT page content.
    """
    if results_ready:
        # Results are ready - hide placeholder, show main page
        return {"display": "none"}, {"display": "block"}
    else:
        # Results not ready - show placeholder, hide main page
        return {"display": "block"}, {"display": "none"}


@callback(
    Output("kt_page_location", "pathname"),
    [
        Input("kt_page_location", "pathname"),  # Only trigger on page navigation
    ],
    [
        State("results_ready_STORAGE", "data"),  # Check state, don't trigger on change
    ],
    prevent_initial_call=False,  # IMPORTANT: Must run on initial page load
)
def redirect_kt_on_reset(current_path, results_ready):
    """
    Redirect to setup page when trying to access KT but results are not available.
    This ensures users can't access KT page by directly navigating to /knowledge-translation
    before processing data.

    Triggers ONLY when:
    1. Initial page load (prevent_initial_call=False)
    2. When pathname changes (navigation to KT page)

    Does NOT trigger when results_ready_STORAGE changes (it's a State, not Input)
    """
    # If results are not ready and we're trying to access the KT page, redirect to setup
    if not results_ready and current_path == "/knowledge-translation":
        print(
            f"[DEBUG] Redirecting from /knowledge-translation to /setup (results_ready={results_ready})"
        )
        return "/setup"
    return no_update


# ================================
# DATA LOADING FROM STORAGE CALLBACKS
# ================================


@callback(
    Output("cytoscape_skt2", "elements", allow_duplicate=True),
    [Input("results_ready_STORAGE", "data"), Input("kt_page_location", "pathname")],
    State("net_data_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def update_skt_network_from_storage(results_ready, pathname, net_data_storage):
    """
    Update the Standard KT network graph with data from STORAGE.
    """
    if not results_ready or not net_data_storage:
        raise PreventUpdate

    elements = get_skt_network_elements(net_data_storage, outcome_idx=0)
    if not elements:
        raise PreventUpdate

    return elements


@callback(
    Output("cytoscape_skt", "elements", allow_duplicate=True),
    [Input("results_ready_STORAGE", "data"), Input("kt_page_location", "pathname")],
    State("net_data_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def update_skt_advanced_network_from_storage(results_ready, pathname, net_data_storage):
    """
    Update the Advanced KT network graph with data from STORAGE.
    """
    if not results_ready or not net_data_storage:
        raise PreventUpdate

    elements = get_skt_network_elements(net_data_storage, outcome_idx=0)
    if not elements:
        raise PreventUpdate

    return elements


@callback(
    Output("grid_treat_compare", "rowData", allow_duplicate=True),
    [Input("results_ready_STORAGE", "data"), Input("kt_page_location", "pathname")],
    [
        State("forest_data_STORAGE", "data"),
        State("cinema_net_data_STORAGE", "data"),
        State("outcome_names_STORAGE", "data"),
    ],
    prevent_initial_call="initial_duplicate",
)
def update_skt_standard_grid_from_storage(
    results_ready, pathname, forest_data_storage, cinema_storage, outcome_names
):
    """
    Update the Standard KT comparison grid with data from STORAGE.
    """
    if not results_ready or not forest_data_storage:
        raise PreventUpdate

    try:
        df = get_skt_two_outcome_data(
            forest_data_storage, cinema_storage, outcome_names
        )
        if df.empty:
            print("[DEBUG] update_skt_standard_grid: df is empty")
            raise PreventUpdate

        # Format RR columns for display
        if "RR" in df.columns and "CI_lower" in df.columns and "CI_upper" in df.columns:
            df["RR"] = df.apply(
                lambda row: f"{row['RR']:.2f}\n({row['CI_lower']:.2f} to {row['CI_upper']:.2f})"
                if pd.notna(row["RR"])
                else "",
                axis=1,
            )
        if (
            "RR_out2" in df.columns
            and "CI_lower_out2" in df.columns
            and "CI_upper_out2" in df.columns
        ):
            df["RR_out2"] = df.apply(
                lambda row: f"{row['RR_out2']:.2f}\n({row['CI_lower_out2']:.2f} to {row['CI_upper_out2']:.2f})"
                if pd.notna(row.get("RR_out2"))
                else "",
                axis=1,
            )

        df["index"] = range(len(df))
        df["switch"] = np.nan
        print(f"[DEBUG] update_skt_standard_grid: returning {len(df)} rows")
        return df.to_dict("records")
    except Exception as e:
        print(f"[ERROR] update_skt_standard_grid: {e}")
        import traceback

        traceback.print_exc()
        raise PreventUpdate


@callback(
    Output("quickstart-grid", "rowData", allow_duplicate=True),
    [Input("results_ready_STORAGE", "data"), Input("kt_page_location", "pathname")],
    [
        State("forest_data_STORAGE", "data"),
        State("net_split_data_STORAGE", "data"),
        State("ranking_data_STORAGE", "data"),
        State("cinema_net_data_STORAGE", "data"),
        State("net_data_STORAGE", "data"),
    ],
    prevent_initial_call="initial_duplicate",
)
def update_skt_advanced_grid_from_storage(
    results_ready,
    pathname,
    forest_data_storage,
    net_split_storage,
    ranking_storage,
    cinema_storage,
    net_data_storage,
):
    """
    Update the Advanced KT grid with data from STORAGE.
    """
    if not results_ready or not forest_data_storage:
        raise PreventUpdate

    try:
        row_data_records, _ = build_skt_advanced_row_data(
            forest_data_storage,
            net_split_storage,
            ranking_storage,
            cinema_storage,
            net_data_storage,
            outcome_idx=0,
        )

        if not row_data_records:
            print("[DEBUG] update_skt_advanced_grid: row_data_records is empty")
            raise PreventUpdate

        print(
            f"[DEBUG] update_skt_advanced_grid: returning {len(row_data_records)} rows"
        )
        return row_data_records
    except Exception as e:
        print(f"[ERROR] update_skt_advanced_grid: {e}")
        import traceback

        traceback.print_exc()
        raise PreventUpdate


# ================================
# PROJECT TITLE AND PROTOCOL LINK CALLBACKS
# ================================


@callback(
    [
        Output("skt_protocol_link", "href"),
        Output("skt_protocol_link", "children"),
    ],
    Input("protocol_link_STORAGE", "data"),
    prevent_initial_call=False,
)
def update_skt_protocol_link(protocol_link):
    """
    Update protocol link display in SKT page from STORAGE.
    """
    if protocol_link and isinstance(protocol_link, str) and protocol_link.strip():
        link = protocol_link.strip()
        display_text = link if len(link) <= 60 else link[:57] + "..."
        return link, display_text
    return "#", "Not provided"

@callback(
    Output("title_skt", "value"),
    Input("project_title_STORAGE", "data"),
    prevent_initial_call=False,
)
def update_skt_title_input(project_title):
    """
    Update the editable project title input in SKT page from STORAGE.
    """
    if project_title and isinstance(project_title, str) and project_title.strip():
        return project_title.strip()
    return ""
