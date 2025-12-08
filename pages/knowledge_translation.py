# Knowledge Translation Page
# Ported from NMAstudio-app-main/tools/layouts_KT.py

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, no_update, clientside_callback
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.exceptions import PreventUpdate

# from tools.skt_layout import (
#     Sktpage,
#     switch_table,
#     skt_layout,
#     skt_nonexpert,
#     model_transitivity,
#     model_skt_stand1,
#     model_skt_stand2,
#     model_skt_compare_simple,
#     model_fullname,
#     model_ranking,
#     grid,
#     row_data,
#     row_data_default,
# )

from tools.layouts_KT import *

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


# # Transitivity modal toggle
# @callback(
#     Output("modal_transitivity", "is_open"),
#     [Input("trans_button", "n_clicks"), Input("close_trans", "n_clicks")],
#     [State("modal_transitivity", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_transitivity(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open


# # Transitivity boxplot/scatter update
# @callback(
#     Output("boxplot_skt", "figure"),
#     [Input("ddskt-trans", "value"), Input("box_kt_scatter", "value")],
#     prevent_initial_call=True,
# )
# def update_transitivity_plot(effect_modifier, scatter_toggle):
#     """Update the transitivity check boxplot/scatter plot."""
#     if scatter_toggle:
#         return __show_scatter(effect_modifier)
#     else:
#         return __show_boxplot(effect_modifier)


# # Pairwise forest plot modal toggle
# @callback(
#     Output("modal_forest", "is_open"),
#     [Input("close_forest", "n_clicks")],
#     [State("modal_forest", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_forest(n_close, is_open):
#     if n_close:
#         return False
#     return is_open


# # Detail comparison modal toggle (Advanced version)
# @callback(
#     Output("skt_modal_copareinfo", "is_open"),
#     [Input("close_compare", "n_clicks")],
#     [State("skt_modal_copareinfo", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_compare(n_close, is_open):
#     if n_close:
#         return False
#     return is_open


# # Simple comparison modal toggle (Standard version)
# @callback(
#     Output("skt_modal_compare_simple", "is_open"),
#     [
#         Input("close_compare_simple", "n_clicks"),
#         Input("grid_treat_compare", "cellClicked"),
#     ],
#     [State("skt_modal_compare_simple", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_compare_simple(n_close, cell_clicked, is_open):
#     triggered_id = ctx.triggered_id
#     if triggered_id == "close_compare_simple":
#         return False
#     elif triggered_id == "grid_treat_compare" and cell_clicked:
#         # Open modal when clicking on RR or Certainty columns
#         col_id = cell_clicked.get("colId", "")
#         if col_id in ["RR", "RR_out2", "Certainty_out1", "Certainty_out2"]:
#             return True
#     return is_open




# # Cytoscape stylesheet update for Standard version (cytoscape_skt2)
# @callback(
#     Output("cytoscape_skt2", "stylesheet"),
#     [
#         Input("cytoscape_skt2", "tapNode"),
#         Input("cytoscape_skt2", "selectedNodeData"),
#         Input("cytoscape_skt2", "selectedEdgeData"),
#     ],
#     [State("cytoscape_skt2", "elements")],
#     prevent_initial_call=True,
# )
# def update_stylesheet_skt2(node, slct_nodesdata, slct_edgedata, elements):
#     """Update cytoscape stylesheet when nodes/edges are selected."""
#     if not elements:
#         raise PreventUpdate
#     return __generate_skt_stylesheet2(node, slct_nodesdata, elements, slct_edgedata)


# # Filter grid based on selected nodes/edges in Standard version
# @callback(
#     Output("grid_treat_compare", "rowData", allow_duplicate=True),
#     [
#         Input("cytoscape_skt2", "selectedNodeData"),
#         Input("cytoscape_skt2", "selectedEdgeData"),
#     ],
#     [
#         State("grid_treat_compare", "rowData"),
#         State("forest_data_STORAGE", "data"),
#         State("cinema_net_data_STORAGE", "data"),
#         State("outcome_names_STORAGE", "data"),
#     ],
#     prevent_initial_call=True,
# )
# def filter_grid_by_network(
#     slct_nodesdata,
#     slct_edgedata,
#     current_row_data,
#     forest_storage,
#     cinema_storage,
#     outcome_names,
# ):
#     """Filter the treatment comparison grid based on network selection."""
#     # Get full data from STORAGE (instead of df_origin which is now empty)
#     if not forest_storage:
#         raise PreventUpdate

#     try:
#         df_full = get_skt_two_outcome_data(
#             forest_storage, cinema_storage, outcome_names
#         )
#         if df_full.empty:
#             raise PreventUpdate
#     except Exception:
#         raise PreventUpdate

#     df = df_full.copy()

#     if slct_nodesdata and len(slct_nodesdata) > 0:
#         selected_nodes = [d["id"] for d in slct_nodesdata]
#         # Filter rows where Treatment or Reference is in selected nodes
#         mask = df["Treatment"].isin(selected_nodes) | df["Reference"].isin(
#             selected_nodes
#         )
#         df = df[mask]

#     if slct_edgedata and len(slct_edgedata) > 0:
#         # Filter based on selected edges
#         filtered_rows = []
#         for edge in slct_edgedata:
#             source = edge.get("source")
#             target = edge.get("target")
#             if source and target:
#                 mask = ((df["Treatment"] == source) & (df["Reference"] == target)) | (
#                     (df["Treatment"] == target) & (df["Reference"] == source)
#                 )
#                 filtered_rows.append(df[mask])
#         if filtered_rows:
#             df = pd.concat(filtered_rows).drop_duplicates()

#     if df.empty:
#         # Return full data if no filter matches
#         return df_full.to_dict("records")

#     return df.to_dict("records")


# # Advanced version callbacks (when expert toggle is on)


# # Update quickstart-grid based on effect options and risk values
# @callback(
#     Output("quickstart-grid", "rowData", allow_duplicate=True),
#     [
#         Input("checklist_effects", "value"),
#         Input("range_lower", "value"),
#         Input("quickstart-grid", "cellValueChanged"),
#     ],
#     [State("quickstart-grid", "rowData")],
#     prevent_initial_call=True,
# )
# def update_advanced_grid(value_effect, lower, value_change, rowData):
#     """Update the advanced grid with forest plots and absolute values."""
#     if not rowData:
#         raise PreventUpdate

#     try:
#         lower = float(lower) if lower else 0.2
#     except ValueError:
#         lower = 0.2

#     if not value_effect:
#         value_effect = []

#     return __Change_Abs(value_effect, value_change, lower, rowData)


# # Cytoscape stylesheet update for Advanced version (cytoscape_skt)
# @callback(
#     Output("cytoscape_skt", "stylesheet"),
#     [
#         Input("cytoscape_skt", "tapNode"),
#         Input("cytoscape_skt", "selectedNodeData"),
#         Input("cytoscape_skt", "selectedEdgeData"),
#         Input("kt2_nclr", "children"),
#         Input("kt2_eclr", "children"),
#         Input("kt2_nclr_custom", "value"),
#         Input("kt2_eclr_custom", "value"),
#         Input("kt2_nds", "children"),
#         Input("kt2_egs", "children"),
#     ],
#     [State("cytoscape_skt", "elements")],
#     prevent_initial_call=True,
# )
# def update_stylesheet_skt(
#     node,
#     slct_nodesdata,
#     slct_edgedata,
#     dd_nclr,
#     dd_eclr,
#     custom_nd_clr,
#     custom_edg_clr,
#     dd_nds,
#     dd_egs,
#     elements,
# ):
#     """Update cytoscape stylesheet for advanced version."""
#     if not elements:
#         raise PreventUpdate

#     # Use default values if dropdowns not set
#     dd_nclr = dd_nclr or "Default"
#     dd_eclr = dd_eclr or "Default"
#     dd_nds = dd_nds or "Default"
#     dd_egs = dd_egs or "Number of studies"

#     return __generate_skt_stylesheet(
#         node,
#         slct_nodesdata,
#         elements,
#         slct_edgedata,
#         dd_nclr,
#         dd_eclr,
#         custom_nd_clr,
#         custom_edg_clr,
#         dd_nds,
#         dd_egs,
#     )


# # Cytoscape layout change for Standard version
# @callback(
#     Output("cytoscape_skt2", "layout"),
#     Input("kt-graph-layout-dropdown", "children"),
#     prevent_initial_call=True,
# )
# def update_cytoscape_layout_skt2(layout_name):
#     if not layout_name:
#         raise PreventUpdate
#     return {"name": layout_name.lower(), "animate": False, "fit": True}


# # Cytoscape layout change for Advanced version
# @callback(
#     Output("cytoscape_skt", "layout"),
#     Input("kt2-graph-layout-dropdown", "children"),
#     prevent_initial_call=True,
# )
# def update_cytoscape_layout_skt(layout_name):
#     if not layout_name:
#         raise PreventUpdate
#     return {"name": layout_name.lower(), "animate": False, "fit": True}


# # FAQ toggle callbacks
# @callback(
#     Output("faq_toast", "is_open"),
#     [Input("faq_button", "n_clicks"), Input("close_faq", "n_clicks")],
#     [State("faq_toast", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_faq_toast(n_open, n_close, is_open):
#     if n_open or n_close:
#         return not is_open
#     return is_open


# # FAQ collapse callbacks
# @callback(
#     Output("faq_ans1", "is_open"),
#     Input("faq_ques1", "n_clicks"),
#     State("faq_ans1", "is_open"),
#     prevent_initial_call=True,
# )
# def toggle_faq1(n_clicks, is_open):
#     if n_clicks:
#         return not is_open
#     return is_open


# @callback(
#     Output("faq_ans2", "is_open"),
#     Input("faq_ques2", "n_clicks"),
#     State("faq_ans2", "is_open"),
#     prevent_initial_call=True,
# )
# def toggle_faq2(n_clicks, is_open):
#     if n_clicks:
#         return not is_open
#     return is_open


# # Fullname modal toggle
# @callback(
#     Output("skt_modal_fullname_simple", "is_open"),
#     [Input("fullname_button", "n_clicks"), Input("close_fullname_simple", "n_clicks")],
#     [State("skt_modal_fullname_simple", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_fullname(n_open, n_close, is_open):
#     if n_open or n_close:
#         return not is_open
#     return is_open


# # Ranking modal toggle
# @callback(
#     Output("modal_ranking", "is_open"),
#     [Input("ranking_button", "n_clicks"), Input("close_rank", "n_clicks")],
#     [State("modal_ranking", "is_open")],
#     prevent_initial_call=True,
# )
# def toggle_modal_ranking(n_open, n_close, is_open):
#     if n_open or n_close:
#         return not is_open
#     return is_open



from tools.functions_skt_abs_forest import __Change_Abs

@callback(
    Output("quickstart-grid", "rowData"),
    # Output("quickstart-grid", "style"),
    # Input("nomal_vs_log", "value"),
    Input("checklist_effects", "value"),
    Input("quickstart-grid", "cellValueChanged"),
    Input("range_lower", "value"),
    # Input("range_upper", "value"),
    State("quickstart-grid", "rowData"),
)

def selected(value_effect, value_change,lower,rowData):
    return __Change_Abs(value_effect, value_change,lower,rowData)


clientside_callback(
    """(id) => {
        dash_ag_grid.getApiAsync(id).then((grid) => {
            grid.addEventListener('rowGroupOpened', (em) => {
                if (em.node.detailNode && em.expanded) {
                    gridDetail = em.node.detailNode.detailGridInfo
                    gridDetail.api.addEventListener('cellClicked', 
                    (ed) => {
                    const newChange = {...ed, node: {id:`${gridDetail.id} - ${ed.node.id}`}}
                    em.api.getGridOption('onCellClicked')(newChange)
                    })
                }
            })
        })
        return window.dash_clientside.no_update
    }""",
    Output('forest-fig-pairwise', 'id'),
    Input('quickstart-grid', 'id')
)




from tools.functions_show_forest_plot import __show_forest_plot

@callback(
   [ Output('forest-fig-pairwise', 'figure'),
    Output('forest-fig-pairwise', 'style')],
    [Input("quickstart-grid", "cellClicked"),
    Input('forest-fig-pairwise', 'style')]
)

def show_forest_plot(cell, style_pair):
    # print(cell)
    return __show_forest_plot(cell, style_pair)



@callback(
    Output("treat_comp", "children"),
    Output("num_RCT", "children"), 
    Output("num_sample", "children"),
    Output("mean_modif", "children"), 
    Input("quickstart-grid", "cellClicked"),
)

def display_sktinfo2(cell):
    treat_comp, num_RCT, num_sample, mean_modif = '','','',''
    if  cell is not None and len(cell) != 0 and 'colId' in cell and cell['colId'] == "Treatment" and cell['value'] is not None and cell['value']!= '':
        df_n_rct = pd.read_csv('db/skt/final_all.csv')
        dic_data =cell
        treat = dic_data['value']
        # idx = dic_data['rowIndex']
        refer = dic_data['rowId'].split('_')[1].split(' ')[0]
        treat_comp = f'Treatment: {treat}, Comparator: {refer}'
        
        n_rct = df_n_rct.loc[(df_n_rct['Treatment'] == treat) & (df_n_rct['Reference'] == refer), 'k']
        # print(n_rct)
        n_rct_value = n_rct.iloc[0] if not n_rct.empty else np.NAN
        num_RCT = f'Randomize controlled trials: {n_rct_value}'

        df_n_total = pd.read_csv('db/psoriasis_wide_complete1.csv')
        set1 = {(treat, refer), (refer, treat)}

        # Extract relevant rows from the DataFrame
        dat_extract = df_n_total[
            df_n_total.apply(lambda row: (row['treat1'], row['treat2']) in set1, axis=1)
        ]
        # Calculate the total
        n_total = dat_extract['n11'].sum() + dat_extract['n21'].sum()
        num_sample = f'Total participants: {n_total}'

        mean_age = round(dat_extract['age'].mean(), 2)
        mean_gender = round((dat_extract['male'] / (dat_extract['n11'] + dat_extract['n21'])).mean(), 2)


        mean_modif = f'Mean age: {mean_age}\nMean male percentage: {mean_gender}'



    return treat_comp, num_RCT, num_sample, mean_modif


@callback(
    Output("modal_transitivity", "is_open"), 
    Input("trans_button", "n_clicks"),
    Input("close_trans", "n_clicks"),
)

def display_forestplot(cell, _):
    if ctx.triggered_id == "close_trans":
        return False
    if ctx.triggered_id == "trans_button":
        return True
    return no_update


@callback(Output('boxplot_skt', 'figure'),
              Input('box_kt_scatter', 'value'),
              Input('ddskt-trans', 'value'),)
def update_boxplot(scatter, value):
    if scatter:
        return __show_scatter(value)
    return __show_boxplot(value)



@callback(Output('cytoscape_skt2', 'stylesheet'),
              [Input('cytoscape_skt2', 'tapNode'),
               Input('cytoscape_skt2', 'selectedNodeData'),
               Input('cytoscape_skt2', 'elements'),
               Input('cytoscape_skt2', 'selectedEdgeData'),
               Input('kt_nclr', 'children'),
               Input('kt_eclr', 'children'),
               Input('node_color_input_kt', 'value'),
               Input('edge_color_input_kt', 'value'),
               Input('kt_nds', 'children'),
               Input('kt_egs', 'children'),
               ]
              )
def generate_stylesheet1(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs):
    return __generate_skt_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs)


@callback(Output('cytoscape_skt2', 'layout'),
              [Input('kt-graph-layout-dropdown', 'children'),],
              prevent_initial_call=False)
def update_cytoscape_layout1(layout):
    ctx = dash.callback_context
    if layout:
       return {'name': layout.lower(),'fit':True }
    
    return {'name': 'circle','fit':True }



@callback(Output('cytoscape_skt', 'stylesheet'),
              [Input('cytoscape_skt', 'tapNode'),
               Input('cytoscape_skt', 'selectedNodeData'),
               Input('cytoscape_skt', 'elements'),
               Input('cytoscape_skt', 'selectedEdgeData'),
               Input('kt2_nclr', 'children'),
               Input('kt2_eclr', 'children'),
               Input('node_color_input_kt2', 'value'),
               Input('edge_color_input_kt2', 'value'),
               Input('kt2_nds', 'children'),
               Input('kt2_egs', 'children'),
               ]
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs):
    return __generate_skt_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, dd_nds, dd_egs)


@callback(Output('cytoscape_skt', 'layout'),
              [Input('kt2-graph-layout-dropdown', 'children'),],
              prevent_initial_call=False)
def update_cytoscape_layout(layout):
    ctx = dash.callback_context
    if layout:
       return {'name': layout.lower(),'fit':True }
    
    return {'name': 'circle','fit':True }



from tools.functions_generate_text_info import __generate_text_info__
@callback(
    Output('trigger_info', 'children'),
    Input('cytoscape_skt', 'selectedNodeData'),
    Input('cytoscape_skt', 'selectedEdgeData')
)
def generate_text_info(nodedata, edgedata):
    return __generate_text_info__(nodedata, edgedata)


@callback(
    Output("skt_modal_copareinfo", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_compare", "n_clicks"),
)
def display_sktinfo1(cell, _):
    print(cell)
    if ctx.triggered_id == "close_compare":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if ('colId' in cell and cell['colId'] == "Treatment" and cell['value']is not None):
            return True
    return no_update


from tools.kt_table_standard import df_origin

@callback(Output("grid_treat_compare", "rowData"),
              [Input('cytoscape_skt2', 'selectedNodeData'),
              Input('cytoscape_skt2', 'selectedEdgeData')
               ],
            #   State("grid_treat_compare", "rowData")
              )
def filter_data(node_data, edge_data):
    rowdata = df_origin

    if node_data or edge_data:
        slctd_nods = {n['id'] for n in node_data} if node_data else set()
        slctd_edgs = [e['source'] + e['target'] for e in edge_data] if edge_data else []
        rowdata = rowdata[(rowdata.Treatment.isin(slctd_nods) & rowdata.Reference.isin(slctd_nods))
                    | ((rowdata.Treatment + rowdata.Reference).isin(slctd_edgs) | (rowdata.Reference + rowdata.Treatment).isin(slctd_edgs))]

    return rowdata.to_dict("records")



@callback(
    Output("skt_modal_compare_simple", "is_open"), 
    Input("grid_treat_compare", "cellClicked"),
    Input("close_compare_simple", "n_clicks"),
)

def display_sktinfo(cell, _):
    if ctx.triggered_id == "close_compare_simple":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if ('colId' in cell and (cell['colId'] == "RR"or cell['colId'] == "RR_out2") and cell['value']is not None):
            return True
    return no_update


@callback(
    Output("skt_modal_fullname_simple", "is_open"), 
    Input("fullname_button", "n_clicks"),
    Input("close_fullname_simple", "n_clicks"),
)

def display_forestplot1(cell, _):
    if ctx.triggered_id == "close_fullname_simple":
        return False
    if ctx.triggered_id == "fullname_button":
        return True
    return no_update


@callback(
    Output("modal_ranking", "is_open"), 
    Input("ranking_button", "n_clicks"),
    Input("close_rank", "n_clicks"),
)

def display_forestplot2(cell, _):
    if ctx.triggered_id == "close_rank":
        return False
    if ctx.triggered_id == "ranking_button":
        return True
    return no_update


# --- Helper to pick the latest clicked button ---
def pick_latest(values, timestamps):
    timestamps = [t or 0 for t in timestamps]
    return values[timestamps.index(max(timestamps))]


# ---------------------- MAIN CALLBACKS ----------------------

# 1. kt_nds and kt2_nds
for prefix in ["kt", "kt2"]:
    @callback(
        Output(f"{prefix}_nds", "children"),
        [Input(f"{prefix}_nds_default", "n_clicks_timestamp"),
         Input(f"{prefix}_nds_default", "children"),
         Input(f"{prefix}_nds_tot_rnd", "n_clicks_timestamp"),
         Input(f"{prefix}_nds_tot_rnd", "children")],
        prevent_initial_call=True
    )
    def update_nds(default_t, default_v, tot_rnd_t, tot_rnd_v):
        return pick_latest([default_v, tot_rnd_v], [default_t, tot_rnd_t])


# 2. kt_egs and kt2_egs
for prefix in ["kt", "kt2"]:
    @callback(
        Output(f"{prefix}_egs", "children"),
        [Input(f"{prefix}_egs_default", "n_clicks_timestamp"),
         Input(f"{prefix}_egs_default", "children"),
         Input(f"{prefix}_egs_tot_rnd", "n_clicks_timestamp"),
         Input(f"{prefix}_egs_tot_rnd", "children")],
        prevent_initial_call=True
    )
    def update_egs(default_t, default_v, tot_rnd_t, tot_rnd_v):
        return pick_latest([default_v, tot_rnd_v], [default_t, tot_rnd_t])


# 3. kt_nclr and kt2_nclr
for prefix in ["kt", "kt2"]:
    @callback(
        [Output(f"{prefix}_nclr", "children"),
         Output(f"close_modal_{prefix}_nclr_input", "n_clicks"),
         Output(f"open_modal_{prefix}_nclr_input", "n_clicks")],
        [Input(f"{prefix}_nclr_default", "n_clicks_timestamp"),
         Input(f"{prefix}_nclr_default", "children"),
         Input(f"{prefix}_nclr_rob", "n_clicks_timestamp"),
         Input(f"{prefix}_nclr_rob", "children"),
         Input(f"{prefix}_nclr_class", "n_clicks_timestamp"),
         Input(f"{prefix}_nclr_class", "children"),
         Input(f"close_modal_{prefix}_nclr_input", "n_clicks")],
        prevent_initial_call=True
    )
    def update_nclr(default_t, default_v, rob_t, rob_v, class_t, class_v, closing_modal):
        if closing_modal:
            return None, None, None
        return pick_latest([default_v, rob_v, class_v], [default_t, rob_t, class_t]), None, None


# 4. kt_eclr and kt2_eclr
for prefix in ["kt", "kt2"]:
    @callback(
        [Output(f"{prefix}_eclr", "children"),
         Output(f"close_modal_{prefix}_eclr_input", "n_clicks"),
         Output(f"open_modal_{prefix}_eclr_input", "n_clicks")],
        [Input(f"{prefix}_edge_default", "n_clicks_timestamp"),
         Input(f"{prefix}_edge_default", "children"),
         Input(f"{prefix}_edge_label", "n_clicks_timestamp"),
         Input(f"{prefix}_edge_label", "children"),
         Input(f"close_modal_{prefix}_eclr_input", "n_clicks")],
        prevent_initial_call=True
    )
    def update_eclr(default_t, default_v, label_t, label_v, closing_modal):
        if closing_modal:
            return None, None, None
        return pick_latest([default_v, label_v], [default_t, label_t]), None, None


flatten = lambda t: [item for sublist in t for item in sublist]

@callback([Output('kt-graph-layout-dropdown', 'children')],
              flatten([[Input(f'kt_ngl_{item.lower()}', 'n_clicks_timestamp'),
                        Input(f'kt_ngl_{item.lower()}', 'children')]
                       for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                                    'Dagre', 'Klay']
                       ]), prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, dagre_t, dagre_v, klay_t, klay_v):
    values =  [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, dagre_v, klay_v]
    times  =  [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, dagre_t, klay_t]
    dd_ngl =  [t or 0 for t in times]
    which  =  dd_ngl.index(max(dd_ngl))
    return [values[which]]


@callback([Output('kt2-graph-layout-dropdown', 'children')],
              flatten([[Input(f'kt2_ngl_{item.lower()}', 'n_clicks_timestamp'),
                        Input(f'kt2_ngl_{item.lower()}', 'children')]
                       for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                                    'Dagre', 'Klay']
                       ]), prevent_initial_call=True)
def which_dd_nds2(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, dagre_t, dagre_v, klay_t, klay_v):
    values =  [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, dagre_v, klay_v]
    times  =  [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, dagre_t, klay_t]
    dd_ngl =  [t or 0 for t in times]
    which  =  dd_ngl.index(max(dd_ngl))
    return [values[which]]

#################################################################
############### Bootstrap MODALS callbacks for KT ###############
#################################################################

# ----- node color modal -----#
for prefix in ["kt", "kt2"]:
    @callback(Output(f"modal_{prefix}", "is_open"),
                [Input(f"open_modal_{prefix}_nclr_input", "n_clicks"),
                Input(f"close_modal_{prefix}_nclr_input", "n_clicks")],
                )
    def toggle_modal(open_t, close):
        if open_t: return True
        if close: return False
        return False

# ----- edge color modal -----#
for prefix in ["kt", "kt2"]:
    @callback(Output(f"modal_edge_{prefix}", "is_open"),
                [Input(f"open_modal_{prefix}_eclr_input", "n_clicks"),
                Input(f"close_modal_{prefix}_eclr_input", "n_clicks")],
                )
    def toggle_modal_edge(open_t, close):
        if open_t: return True
        if close: return False
        return False



######################################################################



from tools.functions_modal_info import display_modal_barplot

@callback(
    Output("barplot_compare", "figure"),
    Output("modal_info_head", "children"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData')
)

def display_sktinfo(cell,value,rowdata):
    return display_modal_barplot(cell,value,rowdata)



from tools.functions_modal_info import display_modal_text
@callback(
    # Output("risk_range", "children"),
    Output("text_info_col", "children"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData')
)

def display_textinfo(cell,value,rowdata):
    return display_modal_text(cell,value,rowdata)

from tools.functions_modal_info import display_modal_data

@callback(
    Output("modal_treat_compare", "rowData"),
    Input("grid_treat_compare", "cellClicked"), 
    # Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData'),
    State('modal_treat_compare','rowData')
)

def display_modaldata(cell,rowdata,rowdata_modal):
    return display_modal_data(cell,rowdata,rowdata_modal)

# @callback(
#     Output("quickstart-grid", "dashGridOptions"),
#     Input("grid-printer-layout-btn", "n_clicks"),
#     Input("grid-regular-layout-btn", "n_clicks"),
#     State("quickstart-grid", "dashGridOptions")
# )
# def toggle_layout(print, regular, options): 
#     if ctx.triggered_id == "grid-printer-layout-btn":
#         options['domLayout']="print"
#         return  options
#     options['domLayout']=None
#     return  options

################################FAQ#######################################

@callback(
    Output("faq_toast", "is_open"),
    Input("faq_button", "n_clicks"),
    Input("close_faq", "n_clicks")
)
def open_toast(cell, _):
    if ctx.triggered_id == "close_faq":
        return False
    if ctx.triggered_id == "faq_button":
        return True
    return no_update

for ans in range(1, 3):
    @callback(
        Output(f"faq_ans{ans}", "is_open"),
        [Input(f"faq_ques{ans}", "n_clicks")],
        [State(f"faq_ans{ans}", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


# Unified clientside callback to manage AG Grid events
clientside_callback(
    """
    function(gridId) {
        dash_ag_grid.getApiAsync(gridId).then((gridApi) => {
            // Make the API available globally for debugging
            window.gridApi = gridApi;

            // Handle row group expansion
            gridApi.addEventListener('rowGroupOpened', (event) => {
                if (event.node && event.expanded && event.node.detailNode) {
                    // Trigger Dash clientside data update
                    if (window.dash_clientside?.set_props) {
                        window.dash_clientside.set_props("detail-status", { data: "test" });
                    }
                }
            });
        }).catch((error) => {
            console.error("Error initializing grid API:", error);
        });

        return window.dash_clientside.no_update;
    }
    """,
    Output("quickstart-grid", "selectedRows"),
    Input("quickstart-grid", "id")
)



import time

@callback(
    Output("popover-container", "children"),
    Input("detail-status", "data"),
    prevent_initial_call=True
)
def show_popover(data):
    if data:
        children = [
            dbc.Popover(
            "Click a cell to see details of the Treatment column.",
            target="info-icon-Treatment",
            trigger="click",
            placement="top",
            className="popover-grid",
            id=f"popover-advance-Treatment-{int(time.time()*1000)}"
        ),
            dbc.Popover(
                        "Specify a value for the reference treatment in \'Risk per 1000\'.",
                        target="info-icon-ab_difference",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id=f"popover-advance-ab_difference-{int(time.time()*1000)}",
                        className= 'popover-grid'
                    ),
            dbc.Popover(
                    "By default, the forest plots include mixed effect, direct effect and indirect effect. There are several options in the 'Options' box for you to customize the forestplots.",
                    target="info-icon-Graph",  # this must match the icon's ID
                    trigger="click",
                    placement="top",
                    id=f"popover-advance-Graph-{int(time.time()*1000)}",
                    className= 'popover-grid'
                ),
            dbc.Popover(
                    "Click a cell with values to open the pairwise forest plot",
                    target="info-icon-direct",  # this must match the icon's ID
                    trigger="click",
                    placement="top",
                    id=f"popover-advance-direct-{int(time.time()*1000)}",
                    className= 'popover-grid'
                ),
            dbc.Popover(
                    "Hover the mouse on each cell to see the details in each field",
                    target="info-icon-Certainty",  # this must match the icon's ID
                    trigger="click",
                    placement="top",
                    id=f"popover-advance-Certainty-{int(time.time()*1000)}",
                    className= 'popover-grid'
                ),
            dbc.Popover(
                    "The whole column is editable for adding comments",
                    target="info-icon-Comments",  # this must match the icon's ID
                    trigger="click",
                    placement="top",
                    id=f"popover-advance-Comments-{int(time.time()*1000)}",
                    className= 'popover-grid'
                )

        ]
        # Still uses the same target, so may not work if multiple icons exist
        return children
    return None


######################################################################


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
