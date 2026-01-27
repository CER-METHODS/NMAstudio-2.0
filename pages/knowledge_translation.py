# Knowledge Translation Page
# Ported from NMAstudio-app-main/tools/layouts_KT.py

import dash
from dash import html, dcc, callback, Input, Output, State, ctx, no_update, clientside_callback
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.exceptions import PreventUpdate
import base64
import io


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
    Generate_advanced_data,
    Generate_kt_standad_data,
    Generate_kt_standad_columnDefs,
    Generate_advanced_columnDefs,
    Generate_advanced_detailColumnDefs,
    update_kt_plots_scale,
    _change_abs_diff
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
# @callback(
#     Output("skt_sub_content", "children"),
#     Input("toggle_grid_select", "value"),
#     prevent_initial_call=True,
# )
# def toggle_skt_version(toggle_value):
#     """Switch between Standard (non-expert) and Advanced (expert) versions."""
#     if toggle_value:
#         return skt_layout()
#     else:
#         return skt_nonexpert()

@callback(
    Output("skt_nonexpert_page", "style"),
    Output("sky_expert_page", "style"),
    Input("kt_page_location", "pathname"),
    Input("toggle_grid_select", "value"),
    prevent_initial_call=True,
)
def toggle_skt_version(path, toggle_value):
    """Switch between Standard (non-expert) and Advanced (expert) versions."""
    if toggle_value:
        return {"display": "none"}, {"display": "block"}
    else:
        return {"display": "block"}, {"display": "none"}

from tools.functions_skt_abs_forest import __Change_Abs




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


@callback(
    Output("modal_forest", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_forest", "n_clicks"),
)

def display_forestplot2(cell, _):
    if ctx.triggered_id == "close_forest":
        return False
    if cell is not None and len(cell) != 0 and 'colId' in cell and cell['colId'] == "direct" and cell['value'] is not None and cell['value']!= '':
        return True
    return no_update

from tools.functions_show_forest_plot import __show_forest_plot

@callback(
   [ Output('forest-fig-pairwise', 'figure'),
    Output('forest-fig-pairwise', 'style')],
    [Input("quickstart-grid", "cellClicked"),
    State('forest-fig-pairwise', 'style'),
    State('forest_data_prws_STORAGE', 'data'),
    State("quickstart-grid", "rowData"),
    State("net_data_STORAGE", "data"),
    State("sktdropdown-out", "value")
    ]
)

def show_forest_plot(cell, style_pair, forest_data_storage, rowData, net_data, out_idx):
    out_idx = int(out_idx or 0)
    rowdata = pd.DataFrame(rowData)
    forest_df = pd.read_json(
        forest_data_storage[out_idx],
        orient="split"
    )
    from tools.utils import get_net_data_json
    net_df = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
    effect_size = net_df[f"effect_size{out_idx+1}"].iloc[0]

    return __show_forest_plot(cell, style_pair, forest_df, rowdata, effect_size)



@callback(
    Output("treat_comp", "children"),
    Output("num_RCT", "children"), 
    Output("num_sample", "children"),
    Output("mean_modif", "children"),
    Input("quickstart-grid", "cellClicked"),
    State("sktdropdown-out", "value"),
    State("net_data_STORAGE", "data"),
    State("effect_modifiers_STORAGE", "data")
)
def display_sktinfo3(cell, out_idx, net_data, effect_modifiers):
    treat_comp = num_RCT = num_sample = text_info = ''

    if not cell or cell.get('colId') != "Treatment" or not cell.get('value'):
        return treat_comp, num_RCT, num_sample, text_info

    treat = cell['value']
    refer = cell['rowId'].split('_')[1].split(' ')[0]
    treat_comp = f'Treatment: {treat}, Comparator: {refer}'

    from tools.utils import get_net_data_json
    df_net = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

    # Count number of RCTs for this comparison
    n_rct = df_net[
        ((df_net['treat1'] == treat) & (df_net['treat2'] == refer)) |
        ((df_net['treat2'] == treat) & (df_net['treat1'] == refer))
    ]
    num_RCT = f'Randomized controlled trials: {len(n_rct)}'

    # Extract participant numbers
    pair_set = {(treat, refer), (refer, treat)}
    dat_extract = df_net[df_net.apply(lambda row: (row['treat1'], row['treat2']) in pair_set, axis=1)]
    
    idx = out_idx + 1
    n_total = dat_extract.get(f'n1{idx}', pd.Series([0])).sum() + dat_extract.get(f'n2{idx}', pd.Series([0])).sum()
    num_sample = f'Total participants: {n_total}'

    # Median of effect modifiers
    for modif in effect_modifiers or []:
        modif_op = modif + '1'
        if modif or modif_op in dat_extract.columns:
            modif = modif_op if modif_op in dat_extract.columns else modif
            median_val = round(dat_extract[modif].median(), 2)
            text_info += f'{modif}: {median_val}\n'

    return treat_comp, num_RCT, num_sample, text_info




@callback(
    Output("modal_transitivity", "is_open"), 
    Input("trans_button", "n_clicks"),
    Input("close_trans", "n_clicks"),
)

def display_transitivity(cell, _):
    if ctx.triggered_id == "close_trans":
        return False
    if ctx.triggered_id == "trans_button":
        return True
    return no_update


@callback(Output('boxplot_skt', 'figure'),
              Input('box_kt_scatter', 'value'),
              Input('ddskt-trans', 'value'),
              State('net_data_STORAGE', 'data'),
              )
def update_boxplot_scatter(scatter, value, net_data):
    if scatter:
        return __show_scatter(value, net_data)
    return __show_boxplot(value, net_data)



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
    Input('cytoscape_skt', 'selectedEdgeData'),
    State("treat_instruction", "data"),
    State("sktdropdown-out", "value"),
    State("net_data_STORAGE", "data"),
    State("effect_modifiers_STORAGE", "data")
)
def generate_text_info(nodedata, edgedata,  instruct_data, out_idx, net_data, effect_modifiers):
    return __generate_text_info__(nodedata, edgedata, instruct_data, out_idx, net_data, effect_modifiers)


@callback(
    Output('treat_instruction', 'data'),
    Output('treat-instruction-filename', 'children'),
    Input("treat-instruction-upload", "contents"),
    State("treat-instruction-upload", "filename"),
    prevent_initial_call=True
)
def display_upload_instructon(contents, filename):

    
    if not contents or not filename:
        raise PreventUpdate

    # only allow csv
    if not filename.lower().endswith(".csv"):
        return  None, None

    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        filename_display = f"Uploaded file: {filename}"
    except Exception:
        return  None, None

    # success → hide toast, store data
    return  df.to_dict("records"), filename_display


@callback(
    Output('treat_fullname', 'data'),
    Output('treat-fullname-filename', 'children'),
    Input("treat-fullname-upload", "contents"),
    State("treat-fullname-upload", "filename"),
    State('modal_fullname', 'rowData'),
    prevent_initial_call=True
)
def display_upload_fullname(contents, filename, rowdata):

    # nothing uploaded
    if not contents or not filename:
        raise PreventUpdate

    # only allow csv
    if not filename.lower().endswith(".csv"):
        return  rowdata, None

    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        filename_display = f"Uploaded file: {filename}"
    except Exception:
        return  rowdata, None


    return  df.to_dict("records"), filename_display




@callback(
    Output('modal_fullname', 'rowData'),
    Input('treat_fullname', 'data'),
    prevent_initial_call=True
)
def display_fullname_data(rowdata):


    if isinstance(rowdata, list) and len(rowdata) > 0:
        rowdata = pd.DataFrame(rowdata)
        return rowdata.to_dict('records')
       
    raise PreventUpdate



@callback(
    Output("skt_modal_copareinfo", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_compare", "n_clicks"),
)
def display_sktinfo1(cell, _):
    if ctx.triggered_id == "close_compare":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if ('colId' in cell and cell['colId'] == "Treatment" and cell['value']is not None):
            return True
    return no_update


# from tools.kt_table_standard import df_origin

@callback(
        Output("grid_treat_compare", "rowData", allow_duplicate=True),
        [Input('cytoscape_skt2', 'selectedNodeData'), 
         Input('cytoscape_skt2', 'selectedEdgeData')],
        State("grid_treat_compare", "rowData"),
        State("KT_standard_data_STORAGE", "data"),
        prevent_initial_call=True
)
def filter_data(node_data, edge_data, rowdata, kt_data):
    rowdata = pd.DataFrame(kt_data)

    if node_data or edge_data:
        slctd_nods = {n['id'] for n in node_data} if node_data else set()
        slctd_edgs = [e['source'] + e['target'] for e in edge_data] if edge_data else []
        rowdata = rowdata[(rowdata.Treatment.isin(slctd_nods) & rowdata.Reference.isin(slctd_nods))
                    | ((rowdata.Treatment + rowdata.Reference).isin(slctd_edgs) | (rowdata.Reference + rowdata.Treatment).isin(slctd_edgs))]

    return rowdata.to_dict('records')


import re
@callback(
    Output("skt_modal_compare_simple", "is_open"), 
    Input("grid_treat_compare", "cellClicked"),
    Input("close_compare_simple", "n_clicks"),
)

def display_sktinfo2(cell, _):
    if ctx.triggered_id == "close_compare_simple":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if (
            'colId' in cell
            and re.fullmatch(r"(RR|OR|MD|SMD)_out\d+(?:_label)?", str(cell['colId']))
            and cell.get('value') is not None
        ):
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

def display_ranking(cell, _):
    if ctx.triggered_id == "close_rank":
        return False
    if ctx.triggered_id == "ranking_button":
        return True
    return no_update


from tools.functions_ranking_plots import __ranking_plot_skt
@callback(Output('tab-rank1', 'figure'),
              Input("ranking_button", "n_clicks"),
              State('ranking_data_STORAGE', 'data'),
              State('net_data_STORAGE', 'data'),
              State('outcome_names_STORAGE', 'data'),
              )
def update_boxplot(cell, ranking_data, net_data, outcome_names):
    return __ranking_plot_skt(ranking_data, net_data, outcome_names)


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
    Output("barchart-col", "style"),
    Output("risk_input_row", "style"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData'),
    prevent_initial_call=True
)

def display_sktinfo(cell,value,rowdata):
    
    return display_modal_barplot(cell,value,rowdata)



from tools.functions_modal_info import display_modal_text
@callback(
    # Output("risk_range", "children"),
    Output("text_info_col", "children"),
    Output("enter_label", "children"),
    Output("risk_range", "children"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData'),
    State("outcome_names_STORAGE", "data"),
    State("net_data_STORAGE", "data"),
    prevent_initial_call=True
)

def display_textinfo(cell,value,rowdata, outcome_names, net_data):
    return display_modal_text(cell,value,rowdata, outcome_names, net_data)

from tools.functions_modal_info import display_modal_data, display_modal_column

@callback(
    Output("modal_treat_compare", "rowData"),
    Output("modal_treat_compare", "columnDefs"),
    Input("grid_treat_compare", "cellClicked"), 
    # Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData'),
    State("net_data_STORAGE", "data"),
    State("effect_modifiers_STORAGE", "data"),
    prevent_initial_call=True
)

def display_modaldata(cell,rowdata, net_data, effect_modifiers):
    if not cell or len(cell) == 0:
        raise PreventUpdate
    
    from tools.utils import get_net_data_json
    # Load modal data
    df_modal = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

    # Accept outcome-specific metric columns, e.g. 'RR_out1_label', 'OR_out2_label', 'MD_out1_label', 'SMD_out1_label'
    colid = str(cell.get("colId"))
    m = re.fullmatch(r"(RR|OR|MD|SMD)_out(\d+)(?:_label)?", colid)
    if not m:
        # not an outcome metric column we handle
        raise PreventUpdate
    
    data = display_modal_data(cell, rowdata, df_modal, m)
    colunmdef = display_modal_column( m, effect_modifiers, df_modal)

    return data, colunmdef

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


def make_sub_callback(i):
    @callback(
        Output(f"faq_block{i}", "is_open"),
        Input(f"faq_sub{i}", "n_clicks"),
        State(f"faq_block{i}", "is_open"),
    )
    def toggle_sub(n, is_open):
        if n:
            return not is_open
        return is_open


for i in range(1, 8):
    make_sub_callback(i)


def make_ques_callback(i):
    @callback(
        Output(f"faq_ans{i}", "is_open"),
        Input(f"faq_ques{i}", "n_clicks"),
        State(f"faq_ans{i}", "is_open"),
    )
    def toggle_ans(n, is_open):
        if n:
            return not is_open
        return is_open


for i in range(1, 13):
    make_ques_callback(i)



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
    Output("popover-container-master", "children"),
    Input("KT_advanced_data_STORAGE", "data"),
    prevent_initial_call=True
)
def show_popover_master(data):
    if data:
        children = [
            dbc.Popover(
                        "Clicking a cell will open a nested table, where the corresponding treatment will be a reference treatment.",
                        target="info-icon-Reference",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-ref",
                        className= 'popover-grid'
                    ),
                dbc.Popover(
                        "This is the range of risk per 1000 in your original dataset. This can be a reference when you enter the number in 'Risk per 1000' column.",
                        target="info-icon-risk_range",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-range",
                        className= 'popover-grid'
                    ),
                
                dbc.Popover(
                        "You can enter a risk for the reference treatment, then the corresponding nested table will include effects in absolute scale.",
                        target="info-icon-risk",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-risk",
                        className= 'popover-grid'
                    ),
                dbc.Popover(
                        "Please explain why you specified this particular risk for the reference treatment.",
                        target="info-icon-rationality",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-rationality",
                        className= 'popover-grid'
                    ),
                dbc.Popover(
                        "Here you can specify the lower limit of the x-axis range for the forest plot in the nested table.",
                        target="info-icon-Scale_lower",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-Scale_lower",
                        className= 'popover-grid'
                    ),
                dbc.Popover(
                        "Here you can specify the upper limit of the x-axis range for the forest plot in the nested table.",
                        target="info-icon-Scale_upper",  # this must match the icon's ID
                        trigger="click",
                        placement="top",
                        id="popover-advance-Scale_upper",
                        className= 'popover-grid'
                    )
        ]
        # Still uses the same target, so may not work if multiple icons exist
        return children
    return None



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


#####################chatbot#######################################################

# from tools.functions_chatbot import *

# @callback(
#     Output(component_id="display-conversation", component_property="children"), 
#     Input(component_id="store-conversation", component_property="data")
# )
# def update_display(chat_history):
#     return [
#         render_textbox(x, box="human") if i % 2 == 0 else render_textbox(x, box="AI")
#         for i, x in enumerate(chat_history.split("<split>")[:-1])
#     ]

# @callback(
#     Output(component_id="user-input", component_property="value"),
#     Input(component_id="submit", component_property="n_clicks"), 
#     Input(component_id="user-input", component_property="n_submit"),
# )
# def clear_input(n_clicks, n_submit):
#     return ""

# @callback(
#     Output(component_id="store-conversation", component_property="data"), 
#     Output(component_id="loading-component", component_property="children"),
#     Input(component_id="submit", component_property="n_clicks"), 
#     Input(component_id="user-input", component_property="n_submit"),
#     State(component_id="user-input", component_property="value"), 
#     State(component_id="store-conversation", component_property="data"),
# )
# def run_chatbot(n_clicks, n_submit, user_input, chat_history):
#     if n_clicks == 0 and n_submit is None:
#         return "", None

#     if user_input is None or user_input == "":
#         return chat_history, None
    
#     chat_history += f"Human: {user_input}<split>ChatBot: "
#     # result_ai = conversation.predict(input=user_input)
#     # model_output = result_ai.strip()
#     result_ai = chain.invoke({"text": f"base on {chat_history},{user_input}. Please generate less than 100 words (20-50 wloud be good) and be concise and clear. avoiding the use of bullet points, asterisks (*), or any special formatting."})
#     model_output = result_ai.content
#     chat_history += f"{model_output}<split>"
#     return chat_history, None



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
# @callback(
#     Output("KT_standard_data_STORAGE", "data"),
#     Output("grid_treat_compare", "rowData"),
#     Output("grid_treat_compare", "columnDefs"),
#     Input("kt_page_location", "pathname"),
#     State("results_ready_STORAGE", "data"),
#     State("net_data_STORAGE", "data"),
#     State("forest_data_STORAGE", "data"),
#     State("number_outcomes_STORAGE", "data"),
#     State("outcome_names_STORAGE", "data"),
#     State("KT_standard_data_STORAGE", "data"),
#     State("cinema_net_data_STORAGE", "data"),
#     prevent_initial_call="initial_duplicate",
# )
# def generate_kt_standad_data(curr_path, results_ready, net_data, 
#                              forest_data_STORAGE, num_outcomes, 
#                              outcome_names, kt_standard_data, cinema_data):
#     if not results_ready or not net_data or not forest_data_STORAGE:
#         raise PreventUpdate
    
#     from tools.utils import get_net_data_json

#     net_df = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

#     num_outcomes = int(num_outcomes or 0)
#     effect_sizes = [
#         net_df[f"effect_size{i+1}"].iloc[0]
#         for i in range(num_outcomes)
#         if f"effect_size{i+1}" in net_df.columns
#     ]
    
#     data = Generate_kt_standad_data(forest_data_STORAGE, num_outcomes, effect_sizes)
#     data["index"] = data.index
    
#     # data.to_csv('db/test_kt_standard_data.csv', index=False)

#     ColumnDefs_treat_compare = Generate_kt_standad_columnDefs(num_outcomes, outcome_names, effect_sizes)
#     return (
#         data.to_dict("records"),
#         data.to_dict("records"),
#         ColumnDefs_treat_compare
#     )

@callback(
    Output("KT_standard_data_STORAGE", "data"),
    Output("grid_treat_compare", "rowData"),
    Output("grid_treat_compare", "columnDefs"),
    Input("kt_page_location", "pathname"),
    State("results_ready_STORAGE", "data"),
    State("net_data_STORAGE", "data"),
    State("forest_data_STORAGE", "data"),
    State("number_outcomes_STORAGE", "data"),
    State("outcome_names_STORAGE", "data"),
    State("KT_standard_data_STORAGE", "data"),
    State("cinema_net_data_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def generate_kt_standad_data(
    curr_path,
    results_ready,
    net_data,
    forest_data_STORAGE,
    num_outcomes,
    outcome_names,
    kt_standard_data,
    cinema_data,
):
    if not results_ready or not net_data or not forest_data_STORAGE:
        raise PreventUpdate

    from tools.utils import get_net_data_json

    net_df = pd.read_json(
        get_net_data_json(net_data),
        orient="split"
    ).round(3)

    num_outcomes = int(num_outcomes or 0)

    effect_sizes = [
        net_df[f"effect_size{i+1}"].iloc[0]
        for i in range(num_outcomes)
        if f"effect_size{i+1}" in net_df.columns
    ]

    data = Generate_kt_standad_data(
        forest_data_STORAGE,
        num_outcomes,
        effect_sizes,
        cinema_data,
    )

    data["index"] = data.index

    ColumnDefs_treat_compare = Generate_kt_standad_columnDefs(
        num_outcomes,
        outcome_names,
        effect_sizes,
    )

    return (
        data.to_dict("records"),
        data.to_dict("records"),
        ColumnDefs_treat_compare,
    )


@callback(
    Output("popover-container-standard", "children"),
    Input("KT_standard_data_STORAGE", "data"),
    State("net_data_STORAGE", "data"),
    State("number_outcomes_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def generate_kt_standad_popover(data, net_data, num_outcomes):
    if data:
        from tools.utils import get_net_data_json

        net_df = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

        num_outcomes = int(num_outcomes or 0)
        effect_sizes = [
            net_df[f"effect_size{i+1}"].iloc[0]
            for i in range(num_outcomes)
            if f"effect_size{i+1}" in net_df.columns
        ]

        children = [
            dbc.Popover(
                "Click switch button to switch treatment and comparator.",
                target="info-icon-switch",
                trigger="click",
                placement="top",
                id="popover-switch",
                className="popover-grid",
            )
        ]

        for i, effect_size in enumerate(effect_sizes):
            children.extend([
                dbc.Popover(
                    "Click a cell to open a popup for detailed and study-level information for the corresponding comparison.",
                    target=f"info-icon-{effect_size}_out{i+1}_label",
                    trigger="click",
                    placement="top",
                    id=f"popover-{effect_size}_out{i+1}_label",
                    className="popover-grid",
                ),
                dbc.Popover(
                    "Hover your mouse over a cell to view detailed information for each field.",
                    target=f"info-icon-Certainty_out{i+1}",
                    trigger="click",
                    placement="top",
                    id=f"popover-certainty{i+1}",
                    className="popover-grid",
                ),
            ])
        
        return children

    return None

    



@callback(
    Output('cytoscape_skt2', 'elements'),
    Input("kt_page_location", "pathname"),
    Input("stand-sktdropdown-out", "value"), 
    State("results_ready_STORAGE", "data"),
    State("net_data_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def generate_kt_diagram_data(curr_path, out_idx,results_ready, net_data):
    if not results_ready or not net_data:
        raise PreventUpdate
    
    from tools.utils import get_net_data_json

    net_df = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

   
    element = get_skt_elements(net_df, out_idx)
    return element



@callback(
    Output("KT_advanced_data_STORAGE", "data"),
    Output("quickstart-grid", "rowData", allow_duplicate=True),
    Output("quickstart-grid", "columnDefs"),
    Output("quickstart-grid", "detailCellRendererParams"),
    Input("kt_page_location", "pathname"),
    Input("sktdropdown-out", "value"),
    State("range_lower", "value"),
    State("results_ready_STORAGE", "data"),
    State("net_data_STORAGE", "data"),
    State("consistency_data_STORAGE", "data"),
    State("net_split_ALL_data_STORAGE", "data"),
    State("ranking_data_STORAGE", "data"),
    State("forest_data_STORAGE", "data"),
    State("cinema_net_data_STORAGE", "data"),
    prevent_initial_call=True,
)
def generate_kt_advanced_data(
    curr_path,
    out_idx,
    lower,
    results_ready,
    net_data,
    consistency_data,
    net_split_data,
    ranking_data,
    forest_data_storage,
    cinema_data,
):
    if not results_ready or not net_data or not forest_data_storage:
        raise PreventUpdate

    from tools.utils import get_net_data_json

    out_idx = int(out_idx or 0)
    lower = float(lower or 0)

    net_df = pd.read_json(
        get_net_data_json(net_data),
        orient="split"
    ).round(3)

    effect_size = net_df[f"effect_size{out_idx+1}"].iloc[0]
    consistency_data = pd.read_json(
        consistency_data[out_idx],
        orient="split"
    )
    
    forest_df = pd.read_json(
        forest_data_storage[out_idx],
        orient="split"
    )

    ranking_df = pd.read_json(
        ranking_data[out_idx],
        orient="split"
    )

    data = Generate_advanced_data(
        forest_df,
        ranking_df,
        net_df,
        effect_size,
        out_idx,
        consistency_data,
        net_split_data [out_idx] if net_split_data and len(net_split_data) > out_idx else None,
        lower,
        cinema_data[out_idx] if cinema_data and len(cinema_data) > out_idx else None
    )

    data["index"] = data.index

    records = data.to_dict("records")

    columnDefs = Generate_advanced_columnDefs(effect_size)
    detailColumnDefs = Generate_advanced_detailColumnDefs(effect_size)
    getRowStyle = {
        "styleConditions": [
            {
                "condition": "params.data.RR === 'RR'",
                "style": {"backgroundColor": "#faead7",'font-weight': 'bold'},
            },
        ]
    }

    detailCellRendererParams={
                "detailGridOptions": {
                "columnDefs": detailColumnDefs,
                "rowHeight": 80,
                "rowDragManaged": True,
                "rowDragMultiRow": True,
                "rowDragEntireRow": True,
                "rowSelection": "multiple",
                'getRowStyle': getRowStyle,
                "detailCellClass": "ag-details-grid",
                },
                "detailColName": "Treatments",
                "suppressCallback": True,
            }

    return records, records, columnDefs, detailCellRendererParams



@callback(
    Output("quickstart-grid", "rowData", allow_duplicate=True),
    Input("quickstart-grid", "cellValueChanged"),
    State("sktdropdown-out", "value"),
    State("quickstart-grid", "rowData"),
    State("net_data_STORAGE", "data"),
    prevent_initial_call=True,
)
def change_abs(value_change, out_idx, rowData, net_data):
    from tools.utils import get_net_data_json

    if not value_change or not rowData:
        return rowData

    change = value_change[0]
    if change.get("colId") != "risk" or not change.get("value") or change["value"] == "Enter a number":
        return rowData

    out_idx = int(out_idx or 0)

    net_df = pd.read_json(
        get_net_data_json(net_data), orient="split"
    ).round(3)

    effect_size = net_df[f"effect_size{out_idx+1}"].iloc[0]
    return _change_abs_diff(change, rowData, effect_size)



@callback(
    Output("quickstart-grid", "rowData", allow_duplicate=True),
    Input("checklist_effects", "value"),
    Input("quickstart-grid", "cellValueChanged"),
    Input("range_lower", "value"),
    State("quickstart-grid", "rowData"),
    State("sktdropdown-out", "value"),
    State("net_data_STORAGE", "data"),
    prevent_initial_call=True,
)
def update_kt_plots(value_effect, value_change, lower, rowData, out_idx, net_data):
    triggered = ctx.triggered_id
    lower = float(lower or 0)
    if (
        triggered == "quickstart-grid"
        and value_change
        and value_change[0].get("colId") == "risk"
    ):
        raise PreventUpdate
    
    from tools.utils import get_net_data_json

    out_idx = int(out_idx or 0)
    net_df = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
    effect_size = net_df[f"effect_size{out_idx+1}"].iloc[0]

    return update_kt_plots_scale(
        value_effect,
        value_change,
        lower,
        rowData,
        effect_size
    )



@callback(
    [
        Output("kt_numstudies", "children"),
        Output("kt_int", "children"),
        Output("kt_par", "children"),
        Output("kt_com", "children"),
        Output("kt_numstudies2", "children"),
        Output("kt_int2", "children"),
        Output("kt_par2", "children"),
        Output("kt_com_direct", "children"),
        Output("kt_com_indirect", "children"),
    ],
    Input("kt_page_location", "pathname"),
    State("net_data_STORAGE", "data"),
    prevent_initial_call= True,
)
def infor_overall(curr_path, net_data):
    if not net_data:
        raise PreventUpdate
    
    from tools.utils import get_net_data_json
    import itertools
    net_data = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
    n_studies = len(net_data.studlab.unique())
    num_study = f"Number of studies: {n_studies}"

    combined_treats = pd.concat([net_data["treat1"], net_data["treat2"]])
    n_treat = combined_treats.nunique()
    num_treat = f"Number of interventions: {n_treat}"
    
    unique_combinations = list(itertools.combinations(combined_treats.unique(), 2))
    num_unique_combinations = len(unique_combinations)

    num_com = f"Number of comparisons: {num_unique_combinations}"
    if "sample_size" in net_data.columns:
        # Drop duplicate study labels so each study counts once
        unique_studies =  net_data[["studlab", "sample_size"]].drop_duplicates("studlab")
        # Sum sample sizes (ignore NaN)
        total_sample_size = unique_studies["sample_size"].dropna().sum()
        # Only show if > 0
        num_par = f"Number of participants: {int(total_sample_size)}" if total_sample_size > 0 else ""
    else:
        num_par = ""
    
    net_data["treat_combine"] = list(zip(net_data["treat1"], net_data["treat2"]))
    direct_combinations = set(net_data["treat_combine"])
    n_com = len(direct_combinations)

    num_com_direct = f"Number of comparisons with direct evidence: {n_com}"

    n_com_without = num_unique_combinations - n_com
    num_com_without = f"Number of comparisons without direct evidence: {n_com_without}"

    return [num_study], [num_treat], [num_par],[num_com],[num_study],[num_treat], [num_par], [num_com_direct], [num_com_without]


@callback(
    Output("kt_modifiers_info", "children"),
    Output("ddskt-trans", "options"),
    Output("stand-sktdropdown-out", "options"),
    Output("sktdropdown-out", "options"),
    Input("kt_page_location", "pathname"),
    State("net_data_STORAGE", "data"),
    State("effect_modifiers_STORAGE", "data"),
    State("outcome_names_STORAGE", "data"),
    prevent_initial_call= True,
)
def infor_effectmodifier(curr_path, net_data, effect_modifiers, out_names):

    if not net_data:
        raise PreventUpdate
    from tools.utils import get_net_data_json
    net_data = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
    n_effect_modifiers = len(effect_modifiers) if effect_modifiers else 0
    children = []
    for i in range(n_effect_modifiers):
        modifier_name = effect_modifiers[i]
        modifier_name_op = modifier_name + "1"
        if modifier_name or modifier_name_op in net_data.columns:
            modifier_name = modifier_name if modifier_name in net_data.columns else modifier_name_op
            unique_studies =  net_data[["studlab", f"{modifier_name}"]].drop_duplicates("studlab")
            # Sum sample sizes (ignore NaN)
            median_modifier = unique_studies[f"{modifier_name}"].dropna().median()
            children.append(html.Span(f"Median {modifier_name}: {median_modifier}",className='skt_span1'))
    options = [{'label': '{}'.format(col), 'value': col} for col in effect_modifiers]
    options_out = [{'label': '{}'.format(col), 'value': i} for i, col in enumerate(out_names)]

    return children, options, options_out, options_out



@callback(
    Output("kt_modifiers_info2", "children"),
    Input("kt_page_location", "pathname"),
    State("net_data_STORAGE", "data"),
    State("effect_modifiers_STORAGE", "data"),
    prevent_initial_call= True,
)
def infor_effectmodifier2(curr_path, net_data, effect_modifiers):

    if not net_data:
        raise PreventUpdate
    from tools.utils import get_net_data_json
    net_data = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
    n_effect_modifiers = len(effect_modifiers) if effect_modifiers else 0
    children = []
    for i in range(n_effect_modifiers):
        modifier_name = effect_modifiers[i]
        modifier_name_op = modifier_name + "1"
        if modifier_name or modifier_name_op in net_data.columns:
            modifier_name = modifier_name if modifier_name in net_data.columns else modifier_name_op
            unique_studies =  net_data[["studlab", f"{modifier_name}"]].drop_duplicates("studlab")
            # Sum sample sizes (ignore NaN)
            median_modifier = unique_studies[f"{modifier_name}"].dropna().median()
            children.append(html.Span(f"Median {modifier_name}: {median_modifier}",className='skt_span1'))
   
    return children




@callback(
    Output("cytoscape_skt", "elements", allow_duplicate=True),
    [Input("results_ready_STORAGE", "data"), 
     Input("kt_page_location", "pathname"),
     Input("sktdropdown-out", "value"),],
    State("net_data_STORAGE", "data"),
    prevent_initial_call="initial_duplicate",
)
def update_skt_advanced_network_from_storage(results_ready, pathname, out_idx, net_data_storage):
    """
    Update the Advanced KT network graph with data from STORAGE.
    """
    if not results_ready or not net_data_storage:
        raise PreventUpdate
    
    from tools.utils import get_net_data_json
    net_data = pd.read_json(get_net_data_json(net_data_storage), orient="split").round(3)
    outcome_idx = out_idx if out_idx is not None else 0
    elements = get_skt_elements(net_data, outcome_idx)
    if not elements:
        raise PreventUpdate

    return elements





# @callback(
#     Output("quickstart-grid", "rowData", allow_duplicate=True),
#     [Input("results_ready_STORAGE", "data"), 
#      Input("kt_page_location", "pathname")],
#     [
#         State("forest_data_STORAGE", "data"),
#         State("net_split_data_STORAGE", "data"),
#         State("ranking_data_STORAGE", "data"),
#         State("cinema_net_data_STORAGE", "data"),
#         State("net_data_STORAGE", "data"),
#     ],
#     prevent_initial_call="initial_duplicate",
# )
# def generate_skt_advanced_grid_from_storage(
#     results_ready,
#     pathname,
#     forest_data_storage,
#     net_split_storage,
#     ranking_storage,
#     cinema_storage,
#     net_data_storage,
# ):
#     """
#     Update the Advanced KT grid with data from STORAGE.
#     """
#     if not results_ready or not forest_data_storage:
#         raise PreventUpdate

#     try:
#         finall_all = Generate_finall_data(
#             forest_data_storage, 
#             net_split_data_storage, 
#             outcome_idx=0)
        
#         row_data_records, _ = Generate_advanced_data(
#             forest_data_storage,
#             net_split_storage,
#             ranking_storage,
#             cinema_storage,
#             net_data_storage,
#             outcome_idx=0,
#         )

#         if not row_data_records:
#             print("[DEBUG] update_skt_advanced_grid: row_data_records is empty")
#             raise PreventUpdate

#         print(
#             f"[DEBUG] update_skt_advanced_grid: returning {len(row_data_records)} rows"
#         )
#         return row_data_records
#     except Exception as e:
#         print(f"[ERROR] update_skt_advanced_grid: {e}")
#         import traceback

#         traceback.print_exc()
#         raise PreventUpdate


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
    Output("title_skt", "children"),
    Output("title_skt_advacned", "children"),
    Input("project_title_STORAGE", "data"),
    prevent_initial_call=False,
)
def update_skt_title_input(project_title):
    """
    Update the editable project title input in SKT page from STORAGE.
    """
    if project_title and isinstance(project_title, str) and project_title.strip():
        return project_title.strip(), project_title.strip()
    return "", ""
