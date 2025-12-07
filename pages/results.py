import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import Input, Output, State, ALL, callback, ctx, exceptions
from dash.exceptions import PreventUpdate
from dash import ctx, no_update
from assets.dropdowns_values import *
from assets.modal_values import (
    modal,
    modal_edges,
    # modal_checks removed - only needed on setup page
    modal_data_table,
    modal_league_table,
    modal_network,
    modal_info,
)
import dash_cytoscape as cyto
from assets.cytoscape_styleesheeet import get_stylesheet
from tools.navbar import Navbar
from assets.Tabs.tabdata import tab_data, raw_data
from tools.utils import get_network_new
import os
import numpy as np
import pandas as pd

# Define export_selection default
export_selection = "as png"

from assets.Tabs.tabtransitivity import tab_trstvty

from assets.Tabs.tabforests import tab_forests
from assets.Infos.graphInfo import infoGraph

from assets.Tabs.tableaguetable import tab_league, tab_league_both
from assets.Tabs.tabfunnel import tab_funnel
from assets.Tabs.tabranking import tab_ranking
from assets.Tabs.tabconsistency import tab_consistency
from assets.alerts import (
    alert_outcome_type,
    alert_data_type,
    R_errors_data,
    R_errors_nma,
    R_errors_pair,
    R_errors_league,
    R_errors_funnel,
    dataupload_error,
)
from assets.COLORS import *
from assets.storage import STORAGE, STORAGE_SCHEMA

# from dash_extensions import Download
from assets.Tabs.saveload_modal_button import saveload_modal
import dash
import time
import itertools
import json
from dash import clientside_callback
from dash_extensions.snippets import send_file
from dash_extensions import Download
from tools.utils import *
from tools.functions_modal_SUBMIT_data import (
    __modal_SUBMIT_button_new,
    __data_modal,
    __data_trans,
)
from tools.functions_NMA_runs import (
    __modal_submit_checks_DATACHECKS,
    __modal_submit_checks_NMA_new,
    __modal_submit_checks_PAIRWISE_new,
    __modal_submit_checks_LT_new,
    __modal_submit_checks_FUNNEL_new,
)

# from tools.functions_ranking_plots import __ranking_plot  # TODO: requires sklearn
from tools.functions_funnel_plot import __Tap_funnelplot, __Tap_funnelplot_normal
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot, __update_scatter
from tools.functions_project_setup import (
    __update_options,
    __second_options,
    __effect_modifier_options,
    __selectbox1_options,
    __outcomes_type,
    __variable_selection,
    __primaryout_selection,
)
from tools.functions_netsplit import __netsplit
from tools.functions_build_league_data_table import (
    __update_output_new,
    __update_output_bothout,
)
from tools.functions_generate_stylesheet import __generate_stylesheet
from tools.functions_export import (
    __generate_xlsx_netsplit,
    __generate_xlsx_league,
    __generate_csv_consistency,
)
from tools.functions_show_forest_plot import __show_forest_plot
# from tools.functions_skt_boxplot import __show_boxplot
# from tools.functions_skt_others import __generate_skt_stylesheet, __generate_skt_stylesheet2
# --------------------------------------------------------------------------------------------------------------------#

dash.register_page(__name__, path="/results")

# Load extra layouts
cyto.load_extra_layouts()
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)
# OPTIONS_results - All plot types are enabled
# Matches NMAstudio-app-main layout structure
OPTIONS_results = [
    {"label": "Data & Transitivity", "value": 0},
    {"label": "Forest plots", "value": 1},
    {"label": "League tables", "value": 2},
    {"label": "Ranking", "value": 3},
    {"label": "Consistency & Reporting bias", "value": 4},
]

layout = html.Div(
    id="result_page",
    className="app__container",
    children=[
        # STORAGE moved to app.py global layout for proper localStorage persistence
        # Hidden location component for redirects when results are reset
        dcc.Location(id="results_page_location", refresh=True),
        # Placeholder shown when results are not ready
        html.Div(
            id="results_not_ready_placeholder",
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
                )
            ],
        ),
        # Error alerts
        html.Div(dataupload_error, style={"vertical-align": "top"}),
        html.Div(R_errors_data, style={"vertical-align": "top"}),
        html.Div(R_errors_nma, style={"vertical-align": "top"}),
        html.Div(R_errors_pair, style={"vertical-align": "top"}),
        html.Div(R_errors_league, style={"vertical-align": "top"}),
        html.Div(R_errors_funnel, style={"vertical-align": "top"}),
        # Project title row
        dbc.Row(
            [
                html.Span(
                    "",
                    style={
                        "justify-self": "center",
                        "align-self": "center",
                        "white-space": "pre",
                        "font-size": "x-large",
                        "color": "chocolate",
                    },
                ),
                html.Span(
                    "Title not provided",
                    style={
                        "justify-self": "center",
                        "align-self": "center",
                        "font-size": "x-large",
                        "color": "#333",
                    },
                    id="link_title",
                ),
            ]
        ),
        # Protocol link row
        dbc.Row(
            [
                html.Span(
                    "Protocol link:   ",
                    style={
                        "justify-self": "center",
                        "align-self": "center",
                        "white-space": "pre",
                        "font-size": "x-large",
                        "color": "chocolate",
                    },
                ),
                dcc.Link(
                    children="Not provided",
                    href="#",
                    target="_blank",
                    style={
                        "justify-self": "center",
                        "align-self": "center",
                        "color": "#0FA0CE",
                        "font-size": "x-large",
                        "padding": "unset",
                    },
                    id="show_protocol_link",
                ),
            ]
        ),
        dbc.Row(id="warning_message"),
        html.Br(),
        # Results selector row
        dbc.Row(
            [
                html.Span(
                    "Select results to display:",
                    style={
                        "justify-self": "center",
                        "align-self": "center",
                        "font-size": "large",
                        "font-weight": "bold",
                    },
                ),
                dcc.Dropdown(
                    placeholder="",
                    options=OPTIONS_results,
                    value=0,
                    style={
                        "display": "grid",
                        "justify-items": "center",
                        "place-self": "center",
                        "font-size": "large",
                        "width": "250px",
                    },
                    id="result_selected",
                ),
            ],
            style={
                "display": "grid",
                "width": "1050px",
                "justify-self": "center",
                "grid-template-columns": "0.7fr 0.7fr 0.2fr 0.4fr 0.4fr 0.4fr",
            },
        ),
        html.Br(),
        # Statistics settings download button
        html.Div(
            [
                html.Button(
                    "Download settings of statistical analysis",
                    id="statsettings",
                    style={"display": "inline-block", "padding": "1px"},
                ),
                Download(id="download-statistic"),
            ]
        ),
        html.Br(),
        html.Br(),
        # Horizontal divider
        html.Hr(
            style={
                "size": "50",
                "borderColor": "orange",
                "borderHeight": "10vh",
                "width": "100%",
                "border-top": "3px solid #E1E1E1",
            }
        ),
        html.Br(),
        html.Br(),
        html.Div(
            id="main_page",
            ### LEFT HALF OF THE PAGE
            children=[
                html.Div(  # NMA Graph
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        html.Div(
                                            Dropdown_graphlayout,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        html.Div(
                                            modal,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        html.Div(
                                            modal_edges,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        #     html.Div(modal_data, style={'display': 'inline-block', 'font-size': '11px'}),
                                        # modal_checks removed - only needed on setup page for data analysis progress
                                        html.Div(
                                            modal_data_table,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        html.Div(
                                            modal_league_table,
                                            id="modal_league_div",
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        html.Div(
                                            modal_network,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        html.A(
                                            html.Img(
                                                src="/assets/icons/NETD.png",
                                                style={"width": "50px"},
                                            ),
                                            id="btn-get-png",
                                            style={"display": "inline-block"},
                                        ),
                                        dbc.Tooltip(
                                            "save graph",
                                            style={
                                                "color": "black",
                                                "font-size": 9,
                                                "margin-left": "10px",
                                                "letter-spacing": "0.3rem",
                                            },
                                            placement="top",
                                            target="btn-get-png",
                                        ),
                                        html.A(
                                            html.Img(
                                                src="/assets/icons/expand.png",
                                                style={
                                                    "width": "40px",
                                                    "margin-top": "4px",
                                                    "padding-left": "-5px",
                                                    "padding-right": "15px",
                                                    "margin-bottom": "2px",
                                                    "border-radius": "1px",
                                                },
                                            ),
                                            id="network-expand",
                                            style={"margin-left": "10px"},
                                        ),
                                        dbc.Tooltip(
                                            "expand plot",
                                            style={
                                                "color": "black",
                                                "font-size": 9,
                                                "margin-left": "10px",
                                                "letter-spacing": "0.3rem",
                                            },
                                            placement="top",
                                            target="network-expand",
                                        ),
                                        html.A(
                                            html.Img(
                                                src="/assets/icons/zoomout.png",
                                                style={
                                                    "width": "40px",
                                                    "margin-top": "4px",
                                                    "padding-left": "-5px",
                                                    "padding-right": "15px",
                                                    "margin-bottom": "2px",
                                                    "border-radius": "1px",
                                                },
                                            ),
                                            id="network-zoomout",
                                            style={"margin-left": "10px"},
                                        ),
                                        dbc.Tooltip(
                                            "zoomout plot",
                                            style={
                                                "color": "black",
                                                "font-size": 9,
                                                "margin-left": "10px",
                                                "letter-spacing": "0.3rem",
                                            },
                                            placement="top",
                                            target="network-zoomout",
                                        ),
                                        dbc.Col(
                                            [
                                                html.H4(
                                                    "Label size:",
                                                    style={
                                                        "font-size": "13px",
                                                        #     'margin-left':'60px',
                                                        "font-family": "system-ui",
                                                        "width": "90px",
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="label_size_input",
                                                    type="text",
                                                    name="Label size",
                                                    style={
                                                        "background-color": "white",
                                                        #      'margin-left':'60px',
                                                        "font-size": "10.5px",
                                                        "color": "gray",
                                                        "margin-top": "-6px",
                                                        "width": "70px",
                                                    },
                                                    placeholder="e.g. 30px",
                                                ),
                                            ],
                                            style={
                                                "padding-left": "20px",
                                                "margin-top": "-40px",
                                            },
                                        ),
                                        dbc.Col(
                                            [
                                                html.H4(
                                                    "Intervention:",
                                                    style={
                                                        "font-size": "13px",
                                                        #      'margin-left':'150px',
                                                        "font-family": "system-ui",
                                                        "width": "90px",
                                                        #      'margin-top':'-62px'
                                                    },
                                                ),
                                                dcc.Input(
                                                    id="treat_name_input",
                                                    type="text",
                                                    name="Label size",
                                                    style={
                                                        "background-color": "white",
                                                        #      'margin-left':'150px',
                                                        "font-size": "10.5px",
                                                        "color": "gray",
                                                        "margin-top": "-6px",
                                                        "width": "70px",
                                                    },
                                                    placeholder="e.g. PBO",
                                                ),
                                            ],
                                            style={
                                                "margin-top": "-40px",
                                                "padding-right": "5px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.A(
                                                    html.Img(
                                                        src="/assets/icons/list.png",
                                                        style={
                                                            "width": "30px",
                                                            "float": "right",
                                                            "margin-top": "-2px",
                                                        },
                                                    ),
                                                    id="img_icon",
                                                ),
                                                # dbc.Toast([html.P("This is the content of the toast", className="mb-0")],
                                                #           id="simple-toast",header="This is the header",
                                                #           icon="primary",
                                                #           dismissable=True,
                                                #           is_open=True,style={"position": "fixed", "top": 66, "right": 10, "width": 350},),
                                            ],
                                            id="info_icon",
                                        ),
                                        html.Div(
                                            modal_info,
                                            style={
                                                "display": "inline-block",
                                                "font-size": "11px",
                                            },
                                        ),
                                        infoGraph,
                                    ]
                                ),
                            ],
                            style={"margin-left": "-20px"},
                        ),
                        cyto.Cytoscape(
                            id="cytoscape",
                            responsive=False,
                            autoRefreshLayout=True,
                            minZoom=0.6,
                            maxZoom=1.2,
                            elements=[],
                            style={
                                "height": "70vh",
                                "width": "100%",
                                "margin-top": "10px",
                                "margin-left": "-10px",
                                "margin-right": "-10px",
                                "z-index": "999",
                                "padding-left": "-10px",
                                "border-right": "3px solid rgb(165 74 97)",
                                # 'max-width': 'calc(52vw)',
                            },
                            layout={"name": "grid", "animate": False, "fit": True},
                            stylesheet=get_stylesheet(),
                        ),
                    ],
                    className="one-half column",
                    id="one-half-1",
                ),
                ### RIGHT HALF OF THE PAGE
                html.Div(
                    id="one-half-2",
                    className="one-half-2 column",
                    children=[
                        html.Div(  # Information box
                            [
                                html.Div(
                                    dbc.Col(
                                        [
                                            html.A(
                                                html.Img(
                                                    src="/assets/icons/expand.png",
                                                    style={
                                                        "width": "34px",
                                                        "margin-top": "15px",
                                                        "border-radius": "1px",
                                                    },
                                                ),
                                                id="data-expand",
                                                style={
                                                    "display": "inline-block",
                                                    "margin-left": "10px",
                                                },
                                            ),
                                            dbc.Tooltip(
                                                "expand window",
                                                style={
                                                    "color": "black",
                                                    "font-size": 9,
                                                    "margin-left": "10px",
                                                    "letter-spacing": "0.3rem",
                                                },
                                                placement="right",
                                                target="data-expand",
                                            ),
                                            html.A(
                                                html.Img(
                                                    src="/assets/icons/zoomout.png",
                                                    style={
                                                        "width": "34px",
                                                        "margin-top": "15px",
                                                        "border-radius": "1px",
                                                    },
                                                ),
                                                id="data-zoomout",
                                                style={
                                                    "display": "none",
                                                    "margin-left": "10px",
                                                },
                                            ),
                                            dbc.Tooltip(
                                                "Zoom out window",
                                                style={
                                                    "color": "black",
                                                    "font-size": 9,
                                                    "margin-left": "10px",
                                                    "letter-spacing": "0.3rem",
                                                },
                                                placement="right",
                                                target="data-zoomout",
                                            ),
                                        ],
                                        style={"display": "inline-block"},
                                    ),
                                ),
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                html.H6(
                                                    "CLICK + SHIFT to select multiple network items",
                                                    className="box__title2",
                                                ),
                                            ]
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            id="cytoscape-mouseTapEdgeData-output",
                                            style={"margin-top": "-20px"},
                                            className="info_box",
                                        )
                                    ],
                                ),
                            ],
                            className="info__container",
                        ),
                        # NOTE: Results Selection Dropdown moved to header section above
                        # Outcome Selection Dropdown
                        html.Div(
                            dbc.Col(
                                [
                                    html.Span(
                                        f"Select outcome",
                                        className="selectbox",
                                        style={
                                            "display": "inline-block",
                                            "text-align": "right",
                                            "margin-left": "0px",
                                            "font-size": "16px",
                                            "white-space": "nowrap",
                                            "color": "#5c7780",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="_outcome_select",
                                        searchable=True,
                                        placeholder="...",
                                        className="box",
                                        clearable=False,
                                        value=0,
                                        style={
                                            "width": "80px",  # 'height': '30px',
                                            "height": "30px",
                                            "vertical-align": "middle",
                                            "font-family": "sans-serif",
                                            "margin-bottom": "2px",
                                            "display": "inline-block",
                                            "color": "black",
                                            "font-size": "10px",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "align-items": "center",
                                    "justify-content": "space-around",
                                    "width": "200px",
                                },
                            ),
                            style={"display": "inline-block", "margin-left": "20px"},
                        ),
                        html.Div(
                            id="all-control-tabs",
                            style={"background-color": "white"},
                            children=[
                                dcc.Tabs(
                                    id="results_tabs",
                                    persistence=True,
                                    children=[
                                        dcc.Tab(
                                            id="data_tab",
                                            value="data_tab",
                                            style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Data",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[
                                                    dcc.Tabs(
                                                        id="",
                                                        value="new_data",
                                                        vertical=False,
                                                        persistence=True,
                                                        children=[
                                                            dcc.Tab(
                                                                label="Converted Data",
                                                                id="new_data",
                                                                value="new_data",
                                                                className="control-tab",
                                                                children=[tab_data()],
                                                                style={
                                                                    "height": "30%",
                                                                    "display": "flex",
                                                                    "justify-content": "center",
                                                                    "align-items": "center",
                                                                    "font-size": "12px",
                                                                    "color": "black",
                                                                    "padding": "0",
                                                                },
                                                                selected_style={
                                                                    "height": "30%",
                                                                    "display": "flex",
                                                                    "justify-content": "center",
                                                                    "align-items": "center",
                                                                    "background-color": "#f5c198",
                                                                    "font-size": "12px",
                                                                    "padding": "0",
                                                                },
                                                            ),
                                                            dcc.Tab(
                                                                label="Imported Data",
                                                                id="raw_data",
                                                                value="raw_data",
                                                                className="control-tab",
                                                                children=[raw_data()],
                                                                style={
                                                                    "height": "30%",
                                                                    "display": "flex",
                                                                    "justify-content": "center",
                                                                    "align-items": "center",
                                                                    "font-size": "12px",
                                                                    "color": "black",
                                                                    "padding": "0",
                                                                },
                                                                selected_style={
                                                                    "height": "30%",
                                                                    "display": "flex",
                                                                    "justify-content": "center",
                                                                    "align-items": "center",
                                                                    "background-color": "#f5c198",
                                                                    "font-size": "12px",
                                                                    "padding": "0",
                                                                },
                                                            ),
                                                        ],
                                                    )
                                                ],
                                                style={
                                                    "overflowX": "auto",
                                                    "overflowY": "auto",
                                                    "height": "99%",
                                                },
                                            ),
                                        ),
                                        # Forest plots tab
                                        dcc.Tab(
                                            id="forest_tab",
                                            value="forest_tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Forest plots",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_forests],
                                                style={
                                                    "overflowX": "auto",
                                                    "overflowY": "auto",
                                                    "height": "99%",
                                                },
                                            ),
                                        ),
                                        dcc.Tab(
                                            id="league_tab",
                                            value="league_tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="League Tables",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_league],
                                                style={
                                                    "overflowX": "unset",
                                                    "overflowY": "unset",
                                                    "height": "99%",
                                                },
                                            ),
                                        ),
                                        # Consistency tab
                                        dcc.Tab(
                                            id="consis_tab",
                                            value="consis_tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "width": "auto",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "font-size": "large",
                                                "width": "auto",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Consistency checks",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_consistency()],
                                                style={
                                                    "overflowX": "auto",
                                                    "overflowY": "auto",
                                                    "height": "99%",
                                                },
                                            ),
                                        ),
                                        # Ranking tab
                                        dcc.Tab(
                                            id="ranking_tab",
                                            value="ranking_tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Ranking plots",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_ranking],
                                            ),
                                        ),
                                    ],
                                    colors={
                                        "border": "grey",
                                        "primary": "grey",
                                        "background": "white",
                                    },
                                )  # change border to CLR_BCKGRND to remove tabs borders
                            ],
                        ),
                    ],
                ),
                html.Br(),
                html.Div(
                    id="one-half-3",
                    className="one-half-3 column",
                    children=[
                        html.Div(
                            id="all-control-tabs2",
                            style={"background-color": "white"},
                            children=[
                                dbc.Col(
                                    [
                                        html.A(
                                            html.Img(
                                                src="/assets/icons/expand.png",
                                                style={
                                                    "width": "34px",
                                                    "margin-top": "15px",
                                                    "border-radius": "1px",
                                                },
                                            ),
                                            id="data-expand1",
                                            style={"display": "none"},
                                        ),
                                        dbc.Tooltip(
                                            "expand window",
                                            style={
                                                "color": "black",
                                                "font-size": 9,
                                                "margin-left": "10px",
                                                "letter-spacing": "0.3rem",
                                            },
                                            placement="right",
                                            target="data-expand1",
                                        ),
                                        html.A(
                                            html.Img(
                                                src="/assets/icons/zoomout.png",
                                                style={
                                                    "width": "34px",
                                                    "margin-top": "15px",
                                                    "border-radius": "1px",
                                                },
                                            ),
                                            id="data-zoomout1",
                                            style={"display": "inline-block"},
                                        ),
                                        dbc.Tooltip(
                                            "Zoom out window",
                                            style={
                                                "color": "black",
                                                "font-size": 9,
                                                "margin-left": "10px",
                                                "letter-spacing": "0.3rem",
                                            },
                                            placement="right",
                                            target="data-zoomout1",
                                        ),
                                    ],
                                    style={"display": "inline-block"},
                                ),
                                dcc.Tabs(
                                    id="results_tabs2",
                                    persistence=True,
                                    children=[
                                        dcc.Tab(
                                            label="Pairwise",
                                            id="tab2",
                                            value="tab2",
                                            className="control-tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            children=[
                                                html.Div(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.P(
                                                                        id="tapEdgeData-info",
                                                                        style={
                                                                            "font-size": "12px",
                                                                            "margin-top": "0.8%",
                                                                        },
                                                                        className="box__title",
                                                                    ),
                                                                    style={
                                                                        "display": "inline-block"
                                                                    },
                                                                ),
                                                                html.Br(),
                                                            ],
                                                            className="tab_row_all",
                                                        )
                                                    ],
                                                    style={"height": "35px"},
                                                ),
                                                dcc.Loading(
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="tapEdgeData-fig-pairwise",
                                                                style={
                                                                    "height": "99%",
                                                                    # 'max-height': 'calc(52vw)',
                                                                    "width": "99%",
                                                                    # 'margin-top': '-2.5%',
                                                                    # 'max-width': 'calc(52vw)'
                                                                },
                                                                config={
                                                                    "editable": True,
                                                                    #  'showEditInChartStudio': True,
                                                                    #  'plotlyServerURL': "https://chart-studio.plotly.com",
                                                                    "edits": dict(
                                                                        annotationPosition=True,
                                                                        annotationTail=True,
                                                                        annotationText=True,
                                                                        axisTitleText=False,
                                                                        colorbarPosition=False,
                                                                        colorbarTitleText=False,
                                                                        titleText=False,
                                                                        legendPosition=True,
                                                                        legendText=True,
                                                                        shapePosition=True,
                                                                    ),
                                                                    "modeBarButtonsToRemove": [
                                                                        "toggleSpikelines",
                                                                        "pan2d",
                                                                        "select2d",
                                                                        "lasso2d",
                                                                        "autoScale2d",
                                                                        "hoverCompareCartesian",
                                                                    ],
                                                                    "toImageButtonOptions": {
                                                                        "format": "png",
                                                                        # one of png, svg,
                                                                        "filename": "custom_image",
                                                                        "scale": 3.5,
                                                                        # Multiply title/legend/axis/canvas sizes by this factor
                                                                    },
                                                                    "displaylogo": False,
                                                                },
                                                            )
                                                        ],
                                                        style={
                                                            "height": "450px",
                                                            "overflow": "scroll",
                                                        },
                                                    )
                                                ),
                                            ],
                                        ),
                                        # TO UNCOMMENT
                                        dcc.Tab(
                                            id="league_tab_both",
                                            value="league_tab_both",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="League Tables for two outcomes",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_league_both],
                                                style={
                                                    "overflowX": "unset",
                                                    "overflowY": "unset",
                                                    "height": "99%",
                                                },
                                            ),
                                        ),
                                        dcc.Tab(
                                            id="trans_tab",
                                            value="trans_tab",
                                            style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Transitivity checks",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_trstvty],
                                            ),
                                        ),
                                        # Funnel tab
                                        dcc.Tab(
                                            id="funnel_tab",
                                            value="funnel_tab",
                                            style={
                                                "color": "grey",
                                                "display": "none",
                                                "width": "auto",
                                                "justify-content": "center",
                                                "align-items": "center",
                                            },
                                            selected_style={
                                                "color": "grey",
                                                "display": "flex",
                                                "justify-content": "center",
                                                "font-size": "large",
                                                "width": "auto",
                                                "background-color": "#f5c198",
                                                "align-items": "center",
                                            },
                                            label="Funnel plots",
                                            children=html.Div(
                                                className="control-tab",
                                                children=[tab_funnel],
                                            ),
                                        ),
                                    ],
                                    colors={
                                        "border": "grey",
                                        "primary": "grey",
                                        "background": "#e8eaeb",
                                    },
                                ),  # change border to CLR_BCKGRND to remove tabs borders
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


### -------------------------- PAGE VISIBILITY CONTROL  ------------------------------- ###


@callback(
    [
        Output("results_not_ready_placeholder", "style"),
        Output("main_page", "style"),
    ],
    Input("results_ready_STORAGE", "data"),
    prevent_initial_call=False,
)
def toggle_results_page_visibility(results_ready):
    """
    Show/hide the results page content based on results_ready_STORAGE.
    When results are not ready, show placeholder message.
    When results are ready, show the actual results page content.
    """
    if results_ready:
        # Results are ready - hide placeholder, show main page
        return {"display": "none"}, {"display": "block"}
    else:
        # Results not ready - show placeholder, hide main page
        return {"display": "block"}, {"display": "none"}


@callback(
    Output("results_page_location", "pathname"),
    [
        Input("results_page_location", "pathname"),  # Only trigger on page navigation
    ],
    [
        State("results_ready_STORAGE", "data"),  # Check state, don't trigger on change
    ],
    prevent_initial_call=False,  # IMPORTANT: Must run on initial page load
)
def redirect_on_reset(current_path, results_ready):
    """
    Redirect to setup page when trying to access results but they're not available.
    This ensures users can't access results page by directly navigating to /results
    before processing data.

    Triggers ONLY when:
    1. Initial page load (prevent_initial_call=False)
    2. When pathname changes (navigation to results page)

    Does NOT trigger when results_ready_STORAGE changes (it's a State, not Input)
    """
    # If results are not ready and we're trying to access the results page, redirect to setup
    if not results_ready and current_path == "/results":
        print(
            f"[DEBUG] Redirecting from /results to /setup (results_ready={results_ready})"
        )
        return "/setup"
    return no_update


### -------------------------- PROTOCOL LINK AND PROJECT TITLE  ------------------------------- ###


@callback(
    [
        Output("show_protocol_link", "href"),
        Output("show_protocol_link", "children"),
    ],
    Input("protocol_link_STORAGE", "data"),
    prevent_initial_call=False,
)
def update_protocol_link_display(protocol_link):
    """
    Update protocol link display from STORAGE.
    Shows the link URL as both href and display text.
    """
    if protocol_link and isinstance(protocol_link, str) and protocol_link.strip():
        link = protocol_link.strip()
        # Truncate display text if too long
        display_text = link if len(link) <= 60 else link[:57] + "..."
        return link, display_text
    return "#", "Not provided"


@callback(
    Output("link_title", "children"),
    Input("project_title_STORAGE", "data"),
    prevent_initial_call=False,
)
def update_project_title_display(project_title):
    """
    Update project title in the results page header.
    Shows the project title or "Not provided" if not set.
    """
    if project_title and isinstance(project_title, str) and project_title.strip():
        title = project_title.strip()
        # Truncate if too long
        display_title = title if len(title) <= 80 else title[:77] + "..."
        return display_title
    return "Not provided"


### -------------------------- ALL CYTOSCAPE CALLBACKS  ------------------------------- ###


@callback(
    Output("_outcome_select", "options"),
    [
        Input("number_outcomes_STORAGE", "data"),
        Input("outcome_names_STORAGE", "data"),
    ],
    prevent_initial_call=False,
)
def update_outcome_options(stored_num, stored_names):
    """Update outcome selector dropdowns with outcome names from STORAGE."""
    print(
        f"[DEBUG] update_outcome_options: stored_num={stored_num}, stored_names={stored_names}"
    )

    # If no data in storage, return empty options
    if not stored_num or stored_num == 0:
        print(f"[DEBUG] update_outcome_options: No data in storage, returning empty []")
        return []

    # Convert stored_num to integer
    if isinstance(stored_num, int):
        number_outcomes = stored_num
    else:
        try:
            number_outcomes = int(stored_num)
        except (ValueError, TypeError):
            print(
                f"[DEBUG] update_outcome_options: Invalid stored_num format, returning empty []"
            )
            return []

    # Use stored names (must be a list with proper length)
    if not stored_names or not isinstance(stored_names, list):
        print(
            f"[DEBUG] update_outcome_options: stored_names invalid, returning empty []"
        )
        return []

    if len(stored_names) < number_outcomes:
        print(
            f"[DEBUG] update_outcome_options: stored_names too short ({len(stored_names)} < {number_outcomes}), returning empty []"
        )
        return []

    outcome_names_list = stored_names[:number_outcomes]

    options_var = [
        {"label": outcome_names_list[i], "value": i} for i in range(number_outcomes)
    ]

    print(f"[DEBUG] update_outcome_options: Returning options={options_var}")
    return options_var


@callback(
    Output("biforest_outcome_select2", "options"),
    Output("biforest_outcome_select2", "value"),
    Output("ranking_outcome_select2", "options"),
    Output("ranking_outcome_select2", "value"),
    [
        Input("number_outcomes_STORAGE", "data"),
        Input("outcome_names_STORAGE", "data"),
    ],
)
def update_outcome2_selectors(stored_num, stored_names):
    """Update outcome 2 selector dropdowns (biforest and ranking) with outcome names from STORAGE."""
    print(
        f"[DEBUG] update_outcome2_selectors: stored_num={stored_num}, stored_names={stored_names}"
    )

    # If no data in storage, return empty options
    if not stored_num or stored_num == 0:
        print(
            f"[DEBUG] update_outcome2_selectors: No data in storage, returning empty []"
        )
        return [], None, [], None

    # Use stored number of outcomes
    if isinstance(stored_num, int):
        number_outcomes = stored_num
    else:
        try:
            number_outcomes = int(stored_num)
        except (ValueError, TypeError):
            print(
                f"[DEBUG] update_outcome2_selectors: Invalid stored_num format, returning empty []"
            )
            return [], None, [], None

    # Get outcome names
    if not stored_names or not isinstance(stored_names, list):
        outcome_names_list = [f"Outcome {i + 1}" for i in range(number_outcomes)]
    else:
        # stored_names is a list, use it directly
        if len(stored_names) >= number_outcomes:
            outcome_names_list = stored_names[:number_outcomes]
        else:
            # Fallback if not enough names
            outcome_names_list = [f"Outcome {i + 1}" for i in range(number_outcomes)]

    # Create dropdown options
    options_var = [
        {"label": outcome_names_list[i], "value": i} for i in range(number_outcomes)
    ]

    # Set default value to 1 if there are at least 2 outcomes, otherwise 0
    default_value = 1 if number_outcomes >= 2 else 0

    print(
        f"[DEBUG] update_outcome2_selectors: Returning options={options_var}, value={default_value}"
    )
    return options_var, default_value, options_var, default_value


### --- update graph layout with dropdown: graph layout --- ###
@callback(
    [Output("cytoscape", "layout"), Output("modal-cytoscape", "layout")],
    [
        Input("graph-layout-dropdown", "children"),
    ],
    prevent_initial_call=False,
)
def update_cytoscape_layout(layout):
    ctx = dash.callback_context
    if layout:
        return {"name": layout.lower(), "fit": True}, {
            "name": layout.lower(),
            "fit": True,
        }

    return {"name": "circle", "fit": True}, {"name": "circle", "fit": True}


### ----- update graph layout on node click ------ ###
@callback(
    [
        Output("cytoscape", "stylesheet"),
        Output("modal-cytoscape", "stylesheet"),
    ],
    [
        Input("cytoscape", "tapNode"),
        Input("cytoscape", "selectedNodeData"),
        Input("cytoscape", "elements"),
        Input("cytoscape", "selectedEdgeData"),
        Input("dd_nclr", "children"),
        Input("dd_eclr", "children"),
        Input("node_color_input", "value"),
        Input("edge_color_input", "value"),
        Input("label_size_input", "value"),
        Input("treat_name_input", "value"),
        Input("dd_nds", "children"),
        Input("dd_egs", "children"),
    ],
    prevent_initial_call=True,
    suppress_callback_exceptions=True,
)
def generate_stylesheet(
    node,
    slct_nodesdata,
    elements,
    slct_edgedata,
    dd_nclr,
    dd_eclr,
    custom_nd_clr,
    custom_edg_clr,
    label_size,
    treat_name,
    dd_nds,
    dd_egs,
):
    stylesheet, stylesheet_modal, _ = __generate_stylesheet(
        node,
        slct_nodesdata,
        elements,
        slct_edgedata,
        dd_nclr,
        dd_eclr,
        custom_nd_clr,
        custom_edg_clr,
        label_size,
        treat_name,
        dd_nds,
        dd_egs,
        None,  # dwld_button - not used anymore
        None,  # dwld_button2 - not used anymore
        False,  # net_download_activation - not used anymore
    )
    return stylesheet, stylesheet_modal


### ----- save network plot as png ------ ###
@callback(
    [Output("cytoscape", "generateImage"), Output("modal-cytoscape", "generateImage")],
    [Input("btn-get-png", "n_clicks"), Input("btn-get-png-modal", "n_clicks")],
    State("exp-options", "children"),
    prevent_initial_call=True,
)
def get_image(btn_clicks, btn_modal_clicks, export):
    """Download network graph image only when button is clicked"""
    # Only download if a button was actually clicked
    if not btn_clicks and not btn_modal_clicks:
        return no_update, no_update

    return {
        "type": "jpeg"
        if export_selection == "as jpeg"
        else ("png" if export_selection == "as png" else "svg"),
        "action": "download",
        "options": {"scale": 3},
    }, {
        "type": "jpeg"
        if export_selection == "as jpeg"
        else ("png" if export_selection == "as png" else "svg"),
        "action": "download",
        "options": {"scale": 3},
    }


# ## ----- Update layout with slider ------ ###


@callback(
    [
        Output("cytoscape", "elements"),
        Output("modal-cytoscape", "elements"),
    ],
    [
        Input("net_data_STORAGE", "data"),
        Input("slider-year", "value"),
        Input("_outcome_select", "value"),
        # Reset button removed from results page
        #    Input('node_size_input', 'value'),
    ],
    prevent_initial_call=False,  # Must run on initial load to show network graph
)
def update_layout_year_slider(net_data, slider_year, out_fun):
    # Guard: Don't execute if data is not ready
    if not net_data or slider_year is None:
        return no_update, no_update

    YEARS_DEFAULT = np.array(
        [
            1963,
            1990,
            1997,
            2001,
            2003,
            2004,
            2005,
            2006,
            2007,
            2008,
            2010,
            2011,
            2012,
            2013,
            2014,
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
            2021,
        ]
    )
    # Handle both dict format (from demo) and list format (from upload)
    from tools.utils import get_net_data_json

    net_data_json = get_net_data_json(net_data)

    try:
        net_datajs = pd.read_json(net_data_json, orient="split")
    except:
        net_datajs = pd.read_json(net_data_json, orient="split", encoding="utf-8")

    outcome = out_fun
    if outcome:
        outcome = int(outcome)
        net_data_df = pd.read_json(net_data_json, orient="split")
        net_datajs2 = net_data_df[net_data_df.year <= slider_year]
        elements = get_network_new(df=net_datajs2, i=outcome)
    else:
        net_datajs = net_datajs[net_datajs.year <= slider_year]
        elements = get_network_new(df=net_datajs, i=0)

    return elements, elements


### ---------------------------------- FOREST PLOTS CALLBACKS ---------------------------------- ###


### ----- update node info on NMA forest plot  ------ ###
@callback(
    Output("tapNodeData-info", "children"), [Input("cytoscape", "selectedNodeData")]
)
def TapNodeData_info(data):
    if data:
        return "Reference treatment: ", data[0]["label"]
    else:
        return "Click on a node to choose reference"


### ----- update node info on bidim forest plot  ------ ###
@callback(
    Output("tapNodeData-info-bidim", "children"),
    [Input("cytoscape", "selectedNodeData")],
    # prevent_initial_call=True
)
def TapNodeData_info_bidim(data):
    if data:
        return "Reference treatment selected: ", data[0]["label"]
    else:
        return "Click on a node to choose reference"


### ----- update edge information on pairwise plot ------ ###
# @callback(Output('tapEdgeData-info', 'children'),
# Input('cytoscape', 'selectedEdgeData'))
# def TapEdgeData_info(data):
# if data:
# return 'Selected comparison: ', f"{data[0]['source'].upper()} vs {data[0]['target'].upper()}"
# else:
# return 'Click on an edge to display the associated  plot'


### - display information box - ###
@callback(
    Output("cytoscape-mouseTapEdgeData-output", "children"),
    [Input("cytoscape", "selectedEdgeData")],
    prevent_initial_call=True,
)
def TapEdgeData(edge):
    if edge:
        n_studies = edge[0]["weight_lab"]
        studies_str = f"{n_studies}" + (" studies" if n_studies > 1 else " study")
        return (
            f"{edge[0]['source'].upper()} vs {edge[0]['target'].upper()}: {studies_str}"
        )
    else:
        return "Click on an edge to get information."


### ----- display forest plot on node click ------ ###
@callback(
    Output("tapNodeData-fig", "figure"),
    Output("tapNodeData-fig", "style"),
    [
        Input("cytoscape", "selectedNodeData"),
        Input("_outcome_select", "value"),
        Input("forest_data_STORAGE", "data"),
        Input("forest_data_prws_STORAGE", "data"),
        Input("tapNodeData-fig", "style"),
        Input("add_pi", "value"),
        Input("add_tau2", "value"),
    ],
    State("net_data_STORAGE", "data"),
)
def TapNodeData_fig(
    data, outcome_idx, forest_data, pw_forest_data, style, pi, add_tau, net_storage
):
    return __TapNodeData_fig(
        data, outcome_idx, forest_data, pw_forest_data, style, pi, add_tau, net_storage
    )


### ----- display bidim forest plot on node click ------ ###
@callback(
    Output("tapNodeData-fig-bidim", "figure"),
    [
        Input("cytoscape", "selectedNodeData"),
        Input("forest_data_STORAGE", "data"),
        Input("_outcome_select", "value"),
        Input("biforest_outcome_select2", "value"),
        Input("_outcome_select", "options"),
        Input({"type": "directionselectors", "index": ALL}, "value"),
    ],
)
def TapNodeData_fig_bidim(
    data, forest_data_store, out_idx1, out_idx2, options, directions
):
    return __TapNodeData_fig_bidim(
        data, forest_data_store, out_idx1, out_idx2, options, directions
    )


### - figures on edge click: pairwise forest plots  - ###
@callback(
    [
        Output("tapEdgeData-fig-pairwise", "figure"),
        Output("tapEdgeData-fig-pairwise", "style"),
    ],
    [
        Input("cytoscape", "selectedEdgeData"),
        Input("_outcome_select", "value"),
        Input("forest_data_prws_STORAGE", "data"),
        Input("tapEdgeData-fig-pairwise", "style"),
    ],
    State("net_data_STORAGE", "data"),
)
def update_forest_pairwise(
    edge, outcome_idx, forest_data_prws, style_pair, net_storage
):
    return __update_forest_pairwise(
        edge, outcome_idx, forest_data_prws, style_pair, net_storage
    )


### ----------------------------------  TRANSITIVITY CALLBACK ---------------------------------- ###


@callback(
    Output("tapEdgeData-fig", "figure"),
    [
        Input("box_vs_scatter", "value"),
        Input("dropdown-effectmod", "value"),
        Input("cytoscape", "selectedEdgeData"),
        Input("net_data_STORAGE", "data"),
    ],
    prevent_initial_call=False,  # Run on page load to show instructions
)
def update_boxplot(scatter, value, edges, net_data):
    print(
        f"[DEBUG update_boxplot] Called with scatter={scatter}, value={value}, edges={edges}, net_data type={type(net_data)}"
    )
    if scatter:
        return __update_scatter(value, edges, net_data)
    return __update_boxplot(value, edges, net_data)


### ----------------------------------  DATA TABLE, LEAGUE TABLE CALLBACKS ---------------------------------- ###


@callback(
    [
        Output("datatable-upload-container", "data"),
        Output("datatable-upload-container", "columns"),
        Output("datatable-upload-container-expanded", "data"),
        Output("datatable-upload-container-expanded", "columns"),
        # Output('league_table', 'children'),
        # Output('modal_league_table_data', 'children'),
        # Output('league_table_legend', 'children'),
        # Output('modal_league_table_legend', 'children'),
        # Output('rob_vs_cinema', 'value'),
        # Output('rob_vs_cinema_modal', 'value'),
        Output("slider-year", "min"),
        Output("slider-year", "max"),
        Output("slider-year", "marks"),
        # Output('data_and_league_table_DATA', 'data'),
        Output("datatable-raw-container", "data"),
        Output("datatable-raw-container", "columns"),
    ],
    [
        Input("slider-year", "value"),
        Input("cytoscape", "selectedNodeData"),
        Input("cytoscape", "selectedEdgeData"),
        Input("net_data_STORAGE", "data"),
        Input("raw_data_STORAGE", "data"),
        # Input('rob_vs_cinema', 'value'),
        # Input('rob_vs_cinema_modal', 'value'),
        # Input('league_table_data_STORAGE', 'data'),
        # Input('cinema_net_data_STORAGE', 'data'),
        # Input('data_and_league_table_DATA', 'data'),
        Input("forest_data_STORAGE", "data"),
        # Reset button removed from results page
        Input("ranking_data_STORAGE", "data"),
        Input("_outcome_select", "value"),
    ],
    State("net_data_STORAGE", "data"),
    State("raw_data_STORAGE", "data"),
    prevent_initial_call=False,  # Run on page load to populate tables with stored data
)
def updateput(
    slider_value,
    store_node,
    store_edge,
    net_data,
    raw_data,
    forest_data,
    ranking_data,
    outcome_idx,
    net_storage,
    raw_storage,
):
    # Guard: If no data is loaded yet, return empty tables
    if not net_data or not raw_data:
        return [[], [], [], [], 0, 0, {}, [], []]
    return __update_output_new(
        slider_value,
        store_node,
        store_edge,
        net_data,
        raw_data,
        None,  # toggle_cinema - not used yet
        None,  # toggle_cinema_modal - not used yet
        None,  # league_table_data - not used for data tables
        None,  # cinema_net_data - not used yet
        None,  # data_and_league_table_DATA - not used yet
        forest_data,
        None,  # reset_btn removed, passing None for compatibility
        outcome_idx,
        net_storage,
        raw_storage,
    )


### ---------------------------------- LEAGUE TABLE CALLBACK ---------------------------------- ###


@callback(
    [
        Output("league_table", "children"),
        Output("modal_league_table_data", "children"),
        Output("league_table_legend", "children"),
        Output("modal_league_table_legend", "children"),
    ],
    [
        Input("league_table_data_STORAGE", "data"),
        Input("_outcome_select", "value"),
        Input("cytoscape", "selectedNodeData"),
        Input("net_data_STORAGE", "data"),
        Input("forest_data_STORAGE", "data"),
        Input("rob_vs_cinema", "value"),
        Input("cinema_net_data_STORAGE", "data"),
    ],
)
def update_league_table(
    league_table_data,
    outcome_idx,
    store_node,
    net_data,
    forest_data,
    toggle_cinema,
    cinema_net_data,
):
    """
    Dedicated callback for league table display.
    Reads from league_table_data_STORAGE and renders the league table.
    Supports CINeMA coloring when toggle_cinema is True and CINeMA data is available.
    """
    from tools.functions_build_league_data_table import build_league_table
    from assets.COLORS import (
        CINEMA_g,
        CINEMA_y,
        CINEMA_r,
        CINEMA_lb,
        CX1,
        CLR_BCKGRND2,
        CX2,
    )

    # Guard: If no league table data, return empty
    if not league_table_data or not net_data:
        return [html.Div("No data available"), html.Div(), [], []]

    # Default outcome index
    if outcome_idx is None:
        outcome_idx = 0

    try:
        # Get net_data for treatments list
        net_data_json = get_net_data_json(net_data)
        net_data_df = pd.read_json(net_data_json, orient="split").round(3)

        # Get league table data for selected outcome
        # League table is stored with treatments as index, so we need to add Treatment column
        leaguetable = pd.read_json(league_table_data[outcome_idx], orient="split")
        treatments = np.unique(
            net_data_df[["treat1", "treat2"]].dropna().values.flatten()
        )

        # Handle node selection filtering
        if store_node and any("id" in nd for nd in store_node):
            slctd_trmnts = [nd["id"] for nd in store_node]
            if len(slctd_trmnts) > 0:
                # Filter to selected treatments (before adding Treatment column)
                treatments = slctd_trmnts
                # Filter leaguetable to selected treatments
                leaguetable = leaguetable.loc[slctd_trmnts, slctd_trmnts]

        # Add Treatment column by resetting index (matching main version behavior)
        leaguetable = leaguetable.reset_index().rename(columns={"index": "Treatment"})

        # Get ROB data from net_data
        net_data_df["rob"] = net_data_df["rob"].replace("__none__", "")
        net_data_df["rob"] = net_data_df["rob"].replace(".", np.nan)
        net_data_df["rob"] = net_data_df["rob"].replace("", np.nan)

        robs = (
            net_data_df.groupby(["treat1", "treat2"])
            .rob.mean()
            .reset_index()
            .pivot_table(index="treat2", columns="treat1", values="rob")
            .reindex(index=treatments, columns=treatments, fill_value=np.nan)
        )

        # Initialize CINeMA confidence data
        comprs_conf_lt = None
        comprs_conf_ut = None
        comprs_downgrade = pd.DataFrame()

        # Process CINeMA data if toggle is on and data is available
        # cinema_net_data is a list with one entry per outcome
        if (
            toggle_cinema
            and cinema_net_data
            and isinstance(cinema_net_data, list)
            and len(cinema_net_data) > outcome_idx
            and cinema_net_data[outcome_idx]
        ):
            try:
                cinema_df = pd.read_json(cinema_net_data[outcome_idx], orient="split")
                confidence_map = {
                    k: n for n, k in enumerate(["very low", "low", "moderate", "high"])
                }

                # Parse comparisons from CINeMA data
                comparisons1 = cinema_df.Comparison.str.split(":", expand=True)
                confidence1 = (
                    cinema_df["Confidence rating"].str.lower().map(confidence_map)
                )

                # Set up comparison matrices
                comparisons2 = comparisons1.copy()
                comprs_conf_ut = comparisons2.copy()  # Upper triangle
                comparisons1.columns = [1, 0]  # To get lower triangle
                comprs_conf_lt = comparisons1.copy()  # Lower triangle

                # Process downgrading reasons if available
                if "Reason(s) for downgrading" in cinema_df.columns:
                    downgrading1 = cinema_df["Reason(s) for downgrading"]
                    comprs_downgrade_lt = comprs_conf_lt.copy()
                    comprs_downgrade_ut = comprs_conf_ut.copy()
                    comprs_downgrade_lt["Downgrading"] = downgrading1
                    comprs_downgrade_ut["Downgrading"] = pd.Series(
                        np.array([np.nan] * len(downgrading1)), copy=False
                    )
                    comprs_downgrade = pd.concat(
                        [comprs_downgrade_ut, comprs_downgrade_lt]
                    )
                    comprs_downgrade = comprs_downgrade.pivot(
                        index=0, columns=1, values="Downgrading"
                    )

                # Build confidence pivot table
                comprs_conf_lt["Confidence"] = confidence1
                comprs_conf_ut["Confidence"] = pd.Series(
                    np.array([np.nan] * len(confidence1)), copy=False
                )
                comprs_conf = pd.concat([comprs_conf_ut, comprs_conf_lt])
                comprs_conf = comprs_conf.pivot(index=0, columns=1, values="Confidence")

                # Mask upper triangle
                ut = np.triu(np.ones(comprs_conf.shape), 1).astype(bool)
                comprs_conf = comprs_conf.where(ut == False, np.nan)

                robs = comprs_conf
            except Exception as e:
                print(f"Error processing CINeMA data: {e}")
                # Fall back to ROB if CINeMA processing fails
                toggle_cinema = False
        else:
            # Ensure toggle_cinema is False if no CINeMA data
            if toggle_cinema:
                toggle_cinema = False

        robs = robs.fillna(robs.T) if not toggle_cinema else robs
        robs = robs.apply(pd.to_numeric, errors="coerce")

        # Set up styling
        N_BINS = 3 if not toggle_cinema else 4
        cmap = (
            [CINEMA_g, CINEMA_y, CINEMA_r]
            if not toggle_cinema
            else [CINEMA_r, CINEMA_y, CINEMA_lb, CINEMA_g]
        )

        # Define bounds for color mapping
        if toggle_cinema:
            confidence_map = {
                k: n for n, k in enumerate(["very low", "low", "moderate", "high"])
            }
        else:
            confidence_map = {k: n for n, k in enumerate(["low", "medium", "high"])}

        df_max, df_min = max(confidence_map.values()), min(confidence_map.values())
        bounds = np.arange(N_BINS + 1) / N_BINS
        ranges = (df_max - df_min) * bounds + df_min
        ranges[-1] *= 1.001
        ranges = ranges + 1 if not toggle_cinema else ranges

        # Create legend
        legend_height = "4px"
        legend = [
            html.Div(
                style={"display": "inline-block", "width": "100px"},
                children=[
                    html.Div(),
                    html.Small(
                        "Risk of bias: " if not toggle_cinema else "CINeMA rating: ",
                        style={"color": "black"},
                    ),
                ],
            )
        ]
        legend += [
            html.Div(
                style={"display": "inline-block", "width": "60px"},
                children=[
                    html.Div(
                        style={"backgroundColor": cmap[n], "height": legend_height}
                    ),
                    html.Small(
                        ("Very Low" if toggle_cinema else "Low")
                        if n == 0
                        else "High"
                        if n == N_BINS - 1
                        else None,
                        style={"paddingLeft": "2px", "color": "black"},
                    ),
                ],
            )
            for n in range(N_BINS)
        ]

        # Build league table columns and styling
        leaguetable_cols = [{"name": c, "id": c} for c in leaguetable.columns]

        # Build conditional styling for ROB/CINeMA colors (matching main version format)
        league_table_styles = []
        for treat_c in treatments:
            for treat_r in treatments:
                if treat_r != treat_c:
                    try:
                        rob_val = (
                            robs.loc[treat_r, treat_c]
                            if treat_r in robs.index and treat_c in robs.columns
                            else np.nan
                        )
                        # Check for NaN using the same pattern as main version
                        empty = rob_val != rob_val
                        diag = treat_r == treat_c

                        # Map value to color bin
                        indxs = (
                            np.where(rob_val < ranges)[0] if rob_val == rob_val else [0]
                        )
                        clr_indx = indxs[0] - 1 if len(indxs) > 0 else 0

                        # Use same filter_query format as main version
                        league_table_styles.append(
                            {
                                "if": {
                                    "filter_query": f"{{Treatment}} = {{{treat_r}}}",
                                    "column_id": treat_c,
                                },
                                "backgroundColor": cmap[clr_indx]
                                if not empty
                                else CLR_BCKGRND2,
                                "color": "white"
                                if not empty
                                else CX2
                                if diag
                                else "black",
                            }
                        )
                    except (KeyError, IndexError):
                        pass

        league_table_styles.append(
            {"if": {"column_id": "Treatment"}, "backgroundColor": CX1}
        )

        # Build tooltip values (matching main version format)
        tooltip_values = []
        if toggle_cinema and not comprs_downgrade.empty:
            for rn, (_, tip) in enumerate(comprs_downgrade.iterrows()):
                row_tooltips = {}
                for col in leaguetable_cols:
                    if col["id"] == "Treatment":
                        row_tooltips[col["id"]] = None
                    else:
                        try:
                            reason = tip[col["id"]] if col["id"] in tip.index else ""
                            row_tooltips[col["id"]] = {
                                "value": f"**Reason for Downgrading:** {reason}",
                                "type": "markdown",
                            }
                        except KeyError:
                            row_tooltips[col["id"]] = {
                                "value": "**Reason for Downgrading:**",
                                "type": "markdown",
                            }
                tooltip_values.append(row_tooltips)
        else:
            # ROB tooltips
            for rn, (_, tip) in enumerate(robs.iterrows()):
                row_tooltips = {}
                for col in leaguetable_cols:
                    if col["id"] == "Treatment":
                        row_tooltips[col["id"]] = None
                    else:
                        try:
                            rob_val = tip[col["id"]] if col["id"] in tip.index else None
                            if rob_val is not None and pd.notna(rob_val):
                                row_tooltips[col["id"]] = {
                                    "value": f"**Average ROB:** {rob_val}",
                                    "type": "markdown",
                                }
                            else:
                                row_tooltips[col["id"]] = {
                                    "value": "**Average ROB:** N/A",
                                    "type": "markdown",
                                }
                        except KeyError:
                            row_tooltips[col["id"]] = {
                                "value": "**Average ROB:** N/A",
                                "type": "markdown",
                            }
                tooltip_values.append(row_tooltips)

        # Build league table component
        league_table = build_league_table(
            leaguetable.to_dict("records"),
            leaguetable_cols,
            league_table_styles,
            tooltip_values,
        )
        league_table_modal = build_league_table(
            leaguetable.to_dict("records"),
            leaguetable_cols,
            league_table_styles,
            tooltip_values,
            modal=True,
        )

        return [league_table, league_table_modal, legend, legend]

    except Exception as e:
        import traceback

        error_msg = f"Error loading league table: {str(e)}"
        print(f"League table error: {traceback.format_exc()}")
        return [html.Div(error_msg), html.Div(), [], []]


### ---------------------------------- LEAGUE TABLE FOR BOTH OUTCOMES ---------------------------------- ###
@callback(
    [
        Output("league_table_both", "children"),
        Output("league_table_legend_both", "children"),
        Output("rob_vs_cinema-both", "value"),
    ],
    [
        Input("cytoscape", "selectedNodeData"),
        Input("cytoscape", "selectedEdgeData"),
        Input("rob_vs_cinema-both", "value"),
        Input("league_table_data_STORAGE", "data"),
        Input("cinema_net_data_STORAGE2", "data"),
        Input("forest_data_STORAGE", "data"),
        Input({"type": "outcomeprimary", "index": ALL}, "value"),
    ],
    [
        State("net_data_STORAGE", "data"),
        State("datatable-secondfile-upload-2", "filename"),
    ],
    prevent_initial_call=True,
)
def update_league_table_both(
    store_node,
    store_edge,
    toggle_cinema,
    league_table_data,
    cinema_net_data,
    forest_data,
    outcome_idx,
    net_storage,
    filename_cinema2,
):
    """Update the league table for both outcomes."""
    return __update_output_bothout(
        store_node,
        store_edge,
        toggle_cinema,
        league_table_data,
        cinema_net_data,
        forest_data,
        None,  # reset_btn - not used
        outcome_idx,
        net_storage,
        filename_cinema2,
    )


### ---------------------------------- FUNNEL, CONSISTENCY, RANKING  CALLBACKS ---------------------------------- ###


#### ----- consistency table and netsplit table ----- ####


@callback(
    [
        Output("netsplit_table-container", "data"),
        Output("netsplit_table-container", "columns"),
        Output("consistency-table", "data"),
        Output("consistency-table", "columns"),
    ],
    [
        Input("cytoscape", "selectedEdgeData"),
        Input("_outcome_select", "value"),
        Input("net_split_data_STORAGE", "data"),
        Input("consistency_data_STORAGE", "data"),
    ],
)
def netsplit(edges, outcome_idx, net_split_data, consistency_data):
    return __netsplit(edges, outcome_idx, net_split_data, consistency_data)


### ----- upload CINeMA data file 1 ------ ###
# @callback([Output("cinema_net_data_STORAGE", "data"),
#                Output("file2-list", "children"),
#                ],
#               [Input('datatable-secondfile-upload', 'contents'),
#                Input('cinema_net_data_STORAGE', 'data')],
#               [State('datatable-secondfile-upload', 'filename')])
# def get_new_data_cinema1(contents, cinema_net_data, filename):
#     if contents is None:
#         # print(cinema_net_data[0])
#         cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
#         cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')

#         # print(cinema_net_data)
#     else:
#         cinema_net_data = parse_contents(contents, filename)
#     if filename is not None:
#         return [cinema_net_data.to_json(orient='split')], 'loaded'
#     else:
#         return [cinema_net_data1.to_json(orient='split'),cinema_net_data2.to_json(orient='split')], ''


# TO UNCOMMENT
# @callback(
# [
# Output("cinema_net_data_STORAGE", "data"),
# Output("file2-list", "children"),
# ],
# [
# Input('datatable-secondfile-upload', 'contents'),
# Input('cinema_net_data_STORAGE', 'data')
# ],
# [State('datatable-secondfile-upload', 'filename')]
# )
# def get_new_data_cinema1(contents, cinema_net_data, filename):
# # Case 1: If no file is uploaded, use existing cinema_net_data
# if contents is None:
# try:
# # Ensure cinema_net_data exists and contains valid JSON
# if isinstance(cinema_net_data, list) and len(cinema_net_data) >= 2:
# cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
# cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')
# return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], ''
# else:
# return [], 'No valid data found in storage.'
# except Exception as e:
# return [], f"Error loading stored data: {str(e)}"

# # Case 2: If a file is uploaded, parse the contents
# else:
# try:
# cinema_net_data = parse_contents(contents, filename)
# return [cinema_net_data.to_json(orient='split')], 'File successfully loaded'
# except Exception as e:
# return [], f"Error processing uploaded file: {str(e)}"


# @callback(
# [
# Output("cinema_net_data_STORAGE2", "data"),
# Output("file-list-out2", "children"),
# ],
# [
# Input('datatable-secondfile-upload-1', 'contents'),
# Input('datatable-secondfile-upload-2', 'contents'),
# Input('cinema_net_data_STORAGE2', 'data')
# ],
# [
# State('datatable-secondfile-upload-1', 'filename'),
# State('datatable-secondfile-upload-2', 'filename')
# ]
# )
# def get_new_data_cinema1(contents1, contents2, cinema_net_data, filename1, filename2):
# # Case 1: If no file is uploaded, use existing cinema_net_data
# if contents1 is None and contents2 is None:
# try:
# # Ensure cinema_net_data exists and contains valid JSON
# if isinstance(cinema_net_data, list) and len(cinema_net_data) >= 2:
# cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
# cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')
# return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], ''
# else:
# return [], 'No valid data found in storage.'
# except Exception as e:
# return [], f"Error loading stored data: {str(e)}"

# # Case 2: If one file is uploaded and the other is not
# elif contents1 is not None and contents2 is None:
# try:
# cinema_net_data = parse_contents(contents1, filename1)
# return [cinema_net_data.to_json(orient='split')], 'File1 successfully loaded'
# except Exception as e:
# return [], f"Error processing uploaded file: {str(e)}"
# elif contents2 is not None and contents1 is None:
# try:
# cinema_net_data = parse_contents(contents2, filename2)
# return [cinema_net_data.to_json(orient='split')], 'File2 successfully loaded'
# except Exception as e:
# return [], f"Error processing uploaded file: {str(e)}"

# # Case 3: If both files are uploaded
# else:
# try:
# cinema_net_data1 = parse_contents(contents1, filename1)
# cinema_net_data2 = parse_contents(contents2, filename2)
# return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], 'Files successfully loaded'
# except Exception as e:
# return [], f"Error processing uploaded files: {str(e)}"


# ### ----- update node info on funnel plot  ------ ###
# @callback(Output('tapNodeData-info-funnel', 'children'),
# [Input('cytoscape', 'tapNodeData')],
# # prevent_initial_call=True
# )
# def TapNodeData_info(data):
# if data: return 'Reference treatment selected: ', data['label']
# else:    return 'Click on a node to choose reference treatment'


# ############ - Funnel plot  - ###############


# Node-based funnel plot (click a treatment node)
@callback(
    Output("funnel-fig", "figure"),
    [
        Input("cytoscape", "selectedNodeData"),
        Input("_outcome_select", "value"),
        Input("funnel_data_STORAGE", "data"),
    ],
)
def Tap_funnelplot(node, outcome_idx, funnel_data):
    return __Tap_funnelplot(node, outcome_idx, funnel_data)


# Edge-based funnel plot (click an edge/connection between treatments)
@callback(
    Output("funnel-fig-normal", "figure"),
    [
        Input("cytoscape", "selectedEdgeData"),
        Input("_outcome_select", "value"),
        Input("net_data_STORAGE", "data"),
        Input("forest_data_prws_STORAGE", "data"),
    ],
)
def Tap_funnelplot_normal(edge, outcome_idx, net_data, pw_data):
    return __Tap_funnelplot_normal(edge, outcome_idx, net_data, pw_data)


# ############ - Ranking plots  - ###############
@callback(
    [Output("graph-rank1", "figure"), Output("graph-rank2", "figure")],
    Input("ranking_data_STORAGE", "data"),
    Input("number_outcomes_STORAGE", "data"),
    Input("_outcome_select", "value"),
    Input("_outcome_select", "options"),
    Input("ranking_outcome_select2", "value"),
    State("net_data_STORAGE", "data"),
)
def ranking_plot(ranking_data, out_number, out_idx1, options, out_idx2, net_data):
    """Generate ranking heatmap and scatter plots based on outcome selection."""
    print("[DEBUG ranking_plot] >>> CALLBACK ENTERED <<<")
    import plotly.express as px
    import traceback

    # Debug prints
    print(
        f"[DEBUG ranking_plot] ranking_data type: {type(ranking_data)}, len: {len(ranking_data) if ranking_data else 'None'}"
    )
    print(
        f"[DEBUG ranking_plot] out_number: {out_number}, out_idx1: {out_idx1}, out_idx2: {out_idx2}"
    )
    print(f"[DEBUG ranking_plot] options: {options}")
    print(f"[DEBUG ranking_plot] net_data type: {type(net_data)}")

    # Guard against missing data
    if not ranking_data or not net_data:
        print("[DEBUG ranking_plot] Missing data - returning empty figures")
        empty_fig = px.scatter()
        empty_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return empty_fig, empty_fig

    # Default indices
    if out_idx1 is None:
        out_idx1 = 0
    if out_idx2 is None:
        out_idx2 = 1 if out_number and out_number >= 2 else 0

    try:
        from tools.functions_ranking_plots import __ranking_plot

        result = __ranking_plot(
            ranking_data, out_number, out_idx1, options, out_idx2, net_data
        )
        print(f"[DEBUG ranking_plot] SUCCESS - returning figures")
        return result
    except Exception as e:
        print(f"[ERROR ranking_plot] Exception: {e}")
        traceback.print_exc()
        empty_fig = px.scatter()
        empty_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return empty_fig, empty_fig


# ############ - Ranking subtabs visibility  - ###############
@callback(
    [
        Output("ranking-heatmap-container", "style"),
        Output("ranking-scatter-container", "style"),
    ],
    Input("subtabs-rank1", "value"),
)
def toggle_ranking_subtabs(selected_tab):
    """Toggle visibility of ranking subtab content based on selected tab."""
    if selected_tab == "Tab-rank1":
        return {"display": "block"}, {"display": "none"}
    else:  # Tab-rank2
        return {"display": "none"}, {"display": "block"}


###############################################################################
################### Bootstrap Dropdowns callbacks #############################
###############################################################################


@callback(
    [Output("dd_nds", "children")],
    [
        Input("dd_nds_default", "n_clicks_timestamp"),
        Input("dd_nds_default", "children"),
        Input("dd_nds_tot_rnd", "n_clicks_timestamp"),
        Input("dd_nds_tot_rnd", "children"),
    ],
    prevent_initial_call=True,
)
def which_dd_nds_size(default_t, default_v, tot_rnd_t, tot_rnd_v):
    values = [default_v, tot_rnd_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]


@callback(
    [Output("exp-options", "children")],
    [
        Input("jpeg-option", "n_clicks_timestamp"),
        Input("jpeg-option", "children"),
        Input("png-option", "n_clicks_timestamp"),
        Input("png-option", "children"),
        Input("svg-option", "n_clicks_timestamp"),
        Input("svg-option", "children"),
    ],
    prevent_initial_call=True,
)
def which_dd_export(default_t, default_v, png_t, png_v, svg_t, svg_v):
    values = [default_v, png_v, svg_v]
    dd_nds = [default_t or 0, png_t or 0, svg_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]


@callback(
    [Output("dd_egs", "children")],
    [
        Input("dd_egs_default", "n_clicks_timestamp"),
        Input("dd_egs_default", "children"),
        Input("dd_egs_tot_rnd", "n_clicks_timestamp"),
        Input("dd_egs_tot_rnd", "children"),
    ],
    prevent_initial_call=True,
)
def which_dd_egs(default_t, default_v, nstud_t, nstud_v):
    values = [default_v, nstud_v]
    dd_egs = [default_t or 0, nstud_t or 0]
    which = dd_egs.index(max(dd_egs))
    return [values[which]]


@callback(
    [
        Output("dd_nclr", "children"),
        Output("close_modal_dd_nclr_input", "n_clicks"),
        Output("open_modal_dd_nclr_input", "n_clicks"),
    ],
    [
        Input("dd_nclr_default", "n_clicks_timestamp"),
        Input("dd_nclr_default", "children"),
        Input("dd_nclr_rob", "n_clicks_timestamp"),
        Input("dd_nclr_rob", "children"),
        Input("dd_nclr_class", "n_clicks_timestamp"),
        Input("dd_nclr_class", "children"),
        Input("close_modal_dd_nclr_input", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def which_dd_nds_color(
    default_t, default_v, rob_t, rob_v, class_t, class_v, closing_modal
):
    values = [default_v, rob_v, class_v]
    dd_nclr = [default_t or 0, rob_t or 0, class_t or 0]
    which = dd_nclr.index(max(dd_nclr))
    return values[which] if not closing_modal else None, None, None


@callback(
    [
        Output("dd_eclr", "children"),
        Output("close_modal_dd_eclr_input", "n_clicks"),
        Output("open_modal_dd_eclr_input", "n_clicks"),
    ],
    [
        Input("dd_edge_default", "n_clicks_timestamp"),
        Input("dd_edge_default", "children"),
        Input("dd_edge_label", "n_clicks_timestamp"),
        Input("dd_edge_label", "children"),
        Input("close_modal_dd_eclr_input", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def which_dd_edges(default_t, default_v, eclr_t, eclr_v, closing_modal):
    values = [default_v, eclr_v]
    dd_eclr = [default_t or 0, eclr_t or 0]
    which = dd_eclr.index(max(dd_eclr))
    return values[which] if not closing_modal else None, None, None


flatten = lambda t: [item for sublist in t for item in sublist]


@callback(
    [Output("graph-layout-dropdown", "children")],
    flatten(
        [
            [
                Input(f"dd_ngl_{item.lower()}", "n_clicks_timestamp"),
                Input(f"dd_ngl_{item.lower()}", "children"),
            ]
            for item in [
                "Circle",
                "Breadthfirst",
                "Grid",
                "Spread",
                "Cose",
                "Cola",
                "Dagre",
                "Klay",
            ]
        ]
    ),
    prevent_initial_call=True,
)
def which_dd_nds_layout(
    circle_t,
    circle_v,
    breadthfirst_t,
    breadthfirst_v,
    grid_t,
    grid_v,
    spread_t,
    spread_v,
    cose_t,
    cose_v,
    cola_t,
    cola_v,
    dagre_t,
    dagre_v,
    klay_t,
    klay_v,
):
    values = [
        circle_v,
        breadthfirst_v,
        grid_v,
        spread_v,
        cose_v,
        cola_v,
        dagre_v,
        klay_v,
    ]
    times = [
        circle_t,
        breadthfirst_t,
        grid_t,
        spread_t,
        cose_t,
        cola_t,
        dagre_t,
        klay_t,
    ]
    dd_ngl = [t or 0 for t in times]
    which = dd_ngl.index(max(dd_ngl))
    return [values[which]]


#################################################################
############### Bootstrap MODALS callbacks ######################
#################################################################


# ----- node color modal -----#
@callback(
    Output("modal", "is_open"),
    [
        Input("open_modal_dd_nclr_input", "n_clicks"),
        Input("close_modal_dd_nclr_input", "n_clicks"),
    ],
)
def toggle_modal_node_color(open_t, close):
    if open_t:
        return True
    if close:
        return False
    return False


# ----- edge color modal -----#
@callback(
    Output("modal_edge", "is_open"),
    [
        Input("open_modal_dd_eclr_input", "n_clicks"),
        Input("close_modal_dd_eclr_input", "n_clicks"),
    ],
)
def toggle_modal_edge(open_t, close):
    if open_t:
        return True
    if close:
        return False
    return False


# ---------------------------------- INITIAL DATA SELECTION and ALL NMA RUNS (in MODALS) ---------------------------------------#


# REMOVED: These setup-specific callbacks belong in setup.py only
# Results page should only read from STORAGE and display plots
# @callback(
#     [
#         Output("modal_data_checks", "is_open"),
#         Output("TEMP_raw_data_STORAGE", "data"),
#         Output("TEMP_net_data_STORAGE", "data"),
#         Output("uploaded_datafile_to_disable_cinema", "data"),
#         Output("Rconsole-error-data", "children"),
#         Output("R-alert-data", "is_open"),
#         Output("dropdown-intervention", "options"),
#     ],
#     [
#         Input("upload_modal_data2", "n_clicks_timestamp"),
#         Input("uploaded_datafile_to_disable_cinema", "data"),
#         Input("submit_modal_data", "n_clicks_timestamp"),
#     ],
#     [
#         State("radio-format", "value"),
#         State({"type": "dataselectors_1", "index": ALL}, "value"),
#         State("number-outcomes", "value"),
#         State({"type": "outcometype", "index": ALL}, "value"),
#         State({"type": "effectselectors", "index": ALL}, "value"),
#         State({"type": "directionselectors", "index": ALL}, "value"),
#         State({"type": "variableselectors", "index": ALL}, "value"),
#         State("modal_data_checks", "is_open"),
#         State("datatable-upload2", "contents"),
#         State("datatable-upload2", "filename"),
#         State("TEMP_net_data_STORAGE", "data"),
#         State("TEMP_raw_data_STORAGE", "data"),
#     ],
#     prevent_initial_call=True,
# )
# def data_trans(...):
#     return __data_trans(...)

# @callback(
#     [
#         Output("select_effect_modifier", "style"),
#         Output("arrow_step3", "style"),
#         Output("effect_modifier_select", "style"),
#     ],
#     Input({"type": "variableselectors", "index": ALL}, "value"),
# )
# def modal_ENABLE_UPLOAD_button(variableselectors):
#     ...

# @callback(
#     [
#         Output("upload_modal_data2", "disabled"),
#         Output("run_button", "style"),
#         Output("arrow_step4", "style"),
#     ],
#     [Input("effect_modifier_checkbox", "value"), Input("no_effect_modifier", "value")],
# )
# def modal_ENABLE_UPLOAD_button(effect_mod, no_effect_mod):
#     ...


OUTPUTS_STORAGE_IDS = list(STORAGE_SCHEMA.keys())
# TO UNCOMMENT
# @callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS] + [Output('token-not-found-alert','children'),
# Output("output_username", "children"),
# Output("output_token", "children"),
# Output('button-token','disabled')],
# [Input("submit_modal_data", "n_clicks"),
# Input('reset_project','n_clicks'),
# #    Input("username-token-upload", "data"),
# Input("button-token", "n_clicks"),
# Input("input-token-load", "value"),
# Input("load-project", "n_clicks"),
# Input("datatable-filename-upload", "data"),
# ],
# [ State("input-username", "value")]+[State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS]+[State('number-outcomes', 'value')],
# prevent_initial_call=True
# )
# def modal_SUBMIT_button(submit, reset_btn,
# # token_data,
# token_btn,
# token_data_load, token_load_btn,
# filename,
# input_token,
# TEMP_raw_data_STORAGE,
# TEMP_net_data_STORAGE,
# TEMP_consistency_data_STORAGE,
# # TEMP_user_elements_STORAGE,
# TEMP_forest_data_STORAGE,
# TEMP_forest_data_prws_STORAGE,
# TEMP_ranking_data_STORAGE,
# TEMP_funnel_data_STORAGE,
# TEMP_league_table_data_STORAGE,
# TEMP_net_split_data_STORAGE,
# TEMP_net_split_ALL_data_STORAGE,
# num_out
# ):
# return __modal_SUBMIT_button_new(submit, reset_btn,
# # token_data,
# token_btn,
# token_data_load, token_load_btn,
# filename,
# input_token,
# TEMP_raw_data_STORAGE,
# TEMP_net_data_STORAGE,
# TEMP_consistency_data_STORAGE,
# # TEMP_user_elements_STORAGE,
# TEMP_forest_data_STORAGE,
# TEMP_forest_data_prws_STORAGE,
# TEMP_ranking_data_STORAGE,
# TEMP_funnel_data_STORAGE,
# TEMP_league_table_data_STORAGE,
# TEMP_net_split_data_STORAGE,
# TEMP_net_split_ALL_data_STORAGE,
# num_out
# )


@callback(
    Output("dropdown-effectmod", "options"),
    [Input("effect_modifiers_STORAGE", "data"), Input("results_tabs", "value")],
)
def update_dropdown_effect_mod(stored_modifiers, tab_value):
    """Populate effect modifier dropdown from stored data"""
    print(
        f"[DEBUG] update_dropdown_effect_mod called with: {stored_modifiers}, tab: {tab_value}"
    )
    print(f"[DEBUG] Type: {type(stored_modifiers)}")

    # Use stored effect modifiers (list format is standard)
    if stored_modifiers:
        # Handle list structure (standard format)
        if isinstance(stored_modifiers, list):
            modifier_list = stored_modifiers
        # Handle dict structure for backward compatibility: {"modifiers": ["age", "bmi", ...]}
        elif isinstance(stored_modifiers, dict) and "modifiers" in stored_modifiers:
            modifier_list = stored_modifiers["modifiers"]
        else:
            modifier_list = []

        if modifier_list:
            result = [
                {"label": "{}".format(modifier), "value": modifier}
                for modifier in modifier_list
            ]
            print(f"[DEBUG] Returning options: {result}")
            return result

    # Default: return empty list
    print("[DEBUG] Returning empty list")
    return []


### -------------------------------------------- EXPAND CALLBACKS ----------------------------------------------- ###

# ----- data expand modal -----#


@callback(
    Output("one-half-1", "style"),
    Output("one-half-2", "style"),
    Output("data-expand", "style"),
    Output("data-zoomout", "style"),
    Output("data-expand1", "style"),
    Output("data-zoomout1", "style"),
    Output("network-expand", "style"),
    Output("network-zoomout", "style"),
    Output("one-half-3", "style"),
    Output("cytoscape", "style"),
    Input("data-expand", "n_clicks_timestamp"),
    Input("data-zoomout", "n_clicks_timestamp"),
    Input("data-expand1", "n_clicks_timestamp"),
    Input("data-zoomout1", "n_clicks_timestamp"),
    Input("network-expand", "n_clicks_timestamp"),
    Input("network-zoomout", "n_clicks_timestamp"),
)
def toggle_expand_views(expand, zoomout, expand1, zoomout1, expand_plot, zoomout_plot):
    style_display = {"display": "block"}
    style_no_display = {"display": "none"}
    style_expand_width = {"width": "93.4%", "margin-left": "3.3%"}
    style_width = {"width": "50.6%"}
    style = {"display": "inline-block"}
    style_no = {"display": "none"}
    style_height = {"display": "block", "height": "100%"}
    style_neplot = {
        "height": "75vh",
        "width": "100%",
        "margin-top": "10px",
        "margin-left": "-10px",
        "margin-right": "-10px",
        "z-index": "999",
        "padding-left": "-10px",
        "border-right": "3px solid rgb(165 74 97)",
    }
    style_neplot_expand = {
        "height": "75vh",
        "width": "100%",
        "margin-top": "10px",
        "margin-left": "-10px",
        "margin-right": "-10px",
        "z-index": "999",
        "padding-left": "-10px",
        "border-right": "3px solid rgb(165 74 97)",
    }
    style_neplot_down = {
        "height": "95%",
        "width": "100%",
        "margin-top": "10px",
        "margin-left": "-10px",
        "margin-right": "-10px",
        "z-index": "999",
        "padding-left": "-10px",
        "border-right": "3px solid rgb(165 74 97)",
    }

    if not ctx.triggered_id:
        return (
            style_display,
            style_width,
            style,
            style_no,
            style_no,
            style,
            style,
            style_no,
            style_expand_width,
            style_neplot,
        )

    triggered_button_id = ctx.triggered_id.split(".")[0]
    if triggered_button_id == "network-expand":
        return (
            style_expand_width,
            style_no_display,
            style,
            style_no,
            style_no,
            style,
            style_no,
            style,
            style_expand_width,
            style_neplot_expand,
        )

    if triggered_button_id == "network-zoomout":
        return (
            style_display,
            style_width,
            style,
            style_no,
            style_no,
            style,
            style,
            style_no,
            style_expand_width,
            style_neplot,
        )

    if triggered_button_id == "data-expand":
        return (
            style_no_display,
            style_expand_width,
            style_no,
            style,
            style_no,
            style_no,
            style,
            style_no,
            style_expand_width,
            style_neplot,
        )

    elif triggered_button_id == "data-zoomout":
        return (
            style_display,
            style_width,
            style,
            style_no,
            style_no,
            style,
            style,
            style_no,
            style_expand_width,
            style_neplot,
        )

    elif triggered_button_id == "data-zoomout1":
        return (
            style_height,
            style_width,
            style,
            style_no,
            style,
            style_no,
            style,
            style_no,
            style_width,
            style_neplot_down,
        )
    elif triggered_button_id == "data-expand1":
        return (
            style_display,
            style_width,
            style,
            style_no,
            style_no,
            style,
            style,
            style_no,
            style_expand_width,
            style_neplot,
        )


@callback(
    Output("modal_info", "is_open"),
    [Input("info_icon", "n_clicks"), Input("close_modal_info", "n_clicks")],
    [State("modal_info", "is_open")],
)
def toggle_modal_info(open, close, is_open):
    if open or close:
        return not is_open
    return is_open


###############################################################################
################### EXPORT TO CSV ON CLICK BUTTON ############################
###############################################################################


@callback(
    Output("download_datatable", "data"),
    [Input("data-export", "n_clicks"), State("datatable-upload-container", "data")],
    prevent_initial_call=True,
)
def generate_csv(n_nlicks, data):
    df = pd.DataFrame(data)
    return dash.dcc.send_data_frame(df.to_csv, filename="data_wide.csv")


# Export all consistency/netsplit data
@callback(
    Output("download_consistency_all", "data"),
    [
        Input("btn-netsplit-all", "n_clicks"),
        State("net_split_ALL_data_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def generate_csv_consistency(n_clicks, consistencydata_all):
    return __generate_csv_consistency(n_clicks, 0, consistencydata_all)


# Export netsplit table (xlsx with colors)
@callback(
    Output("download_consistency", "data"),
    [
        Input("consistency-export", "n_clicks"),
        State("netsplit_table-container", "data"),
    ],
    prevent_initial_call=True,
)
def generate_xlsx_netsplit(n_clicks, consistencydata):
    return __generate_xlsx_netsplit(n_clicks, consistencydata)


#### xlsx colors league table
@callback(
    Output("download_leaguetable", "data"),
    [Input("league-export", "n_clicks"), State("league_table", "children")],
    prevent_initial_call=True,
)
def generate_xlsx_league(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)


@callback(
    Output("download_leaguetable_both", "data"),
    [Input("league-export-both", "n_clicks"), State("league_table_both", "children")],
    prevent_initial_call=True,
)
def generate_xlsx_league_both(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)


@callback(
    Output("download_leaguetable_modal", "data"),
    [
        Input("league-export-modal", "n_clicks"),
        State("modal_league_table_data", "children"),
    ],
    prevent_initial_call=True,
)
def generate_xlsx_league_modal(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)


#############################################################################
############################# TOGGLE SECTION ################################
#############################################################################


# UNCOMMENT
# ### -------------- toggle switch league table ---------------- ###
# @callback([Output("cinemaswitchlabel1", "style"),
# Output("cinemaswitchlabel2", "style")],
# [Input("rob_vs_cinema", "value")])
# def color_leaguetable_toggle(toggle_value):
# style1 = {'color': '#808484' if toggle_value else '#5a87c4', 'font-size': '12px',
# 'display': 'inline-block', 'margin': 'auto', 'padding-left': '10px'}
# style2 = {'color': '#5a87c4' if toggle_value else '#808484', 'font-size': '12px',
# 'display': 'inline-block', 'margin': 'auto', 'padding-right': '0px', }
# return style1, style2

# ### -------------- toggle switch funnel plot ---------------- ###
# @callback([Output("funnelswitchlabel1", "style"),
# Output("funnelswitchlabel2", "style")],
# [Input("toggle_funnel_direction", "value")])
# def color_funnel_toggle(toggle_value):
# style1 = {'color': 'gray' if toggle_value else '#5a87c4',
# 'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
# style2 = {'color': '#5a87c4' if toggle_value else 'gray',
# 'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
# return style1, style2

# ### -------------- toggle switch consistency ---------------- ###
# @callback([Output("consistencyswitchlabel1", "style"),
# Output("consistencyswitchlabel2", "style")],
# [Input("toggle_consistency_direction", "value")])
# def color_funnel_toggle(toggle_value):
# style1 = {'color': 'gray' if toggle_value else '#5a87c4',
# 'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
# style2 = {'color': '#5a87c4' if toggle_value else 'gray',
# 'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
# return style1, style2


#############################################################################
######################### DISABLE TOGGLE SWITCHES ###########################
#############################################################################
# UNCOMMENT
# ## disable cinema coloring toggle if no cinema files are passed
# @callback([Output('rob_vs_cinema', 'disabled'),
# Output('rob_vs_cinema_modal', 'disabled')],
# [Input('datatable-secondfile-upload', 'filename'),
# Input("uploaded_datafile_to_disable_cinema", "data"),
# ]
# )
# def disable_cinema_toggle(filename_cinema1, filename_data):

# if filename_cinema1 is None and filename_data: return True, True
# else: return False, False

# @callback(Output('rob_vs_cinema-both', 'disabled'),
# [Input('datatable-secondfile-upload-1', 'filename'),
# Input('datatable-secondfile-upload-2', 'filename'),
# Input("uploaded_datafile_to_disable_cinema", "data"),
# ]
# )
# def disable_cinema_toggle(filename_cinema1, filename_cinema2,file_data):

# if (filename_cinema1 is None or filename_cinema2 is None) and file_data: return True
# else: return False


###############overall information##################


@callback(
    [
        Output("numstudies", "children"),
        Output("numtreat", "children"),
        Output("numcompar", "children"),
        Output("numcom_without", "children"),
    ],
    Input("net_data_STORAGE", "data"),
)
def infor_overall(data):
    from tools.utils import get_net_data_json

    net_data = pd.read_json(get_net_data_json(data), orient="split").round(3)
    n_studies = len(net_data.studlab.unique())
    num_study = f"Number of studies: {n_studies}"

    combined_treats = pd.concat([net_data["treat1"], net_data["treat2"]])
    n_treat = combined_treats.nunique()
    num_treat = f"Number of treatments: {n_treat}"

    unique_combinations = list(itertools.combinations(combined_treats.unique(), 2))
    num_unique_combinations = len(unique_combinations)

    net_data["treat_combine"] = list(zip(net_data["treat1"], net_data["treat2"]))
    unique_combinations = set(net_data["treat_combine"])
    n_com = len(unique_combinations)

    num_com = f"Number of comparisons with direct evidence: {n_com}"

    n_com_without = num_unique_combinations - n_com
    num_com_without = f"Number of comparisons without direct evidence: {n_com_without}"

    return [num_study], [num_treat], [num_com], [num_com_without]


###########################results selection###########################################
@callback(
    [
        Output("data_tab", "style"),
        Output("trans_tab", "style"),
        Output("forest_tab", "style"),
        Output("tab2", "style"),  # Pairwise tab in results_tabs2
        Output("league_tab", "style"),
        Output("league_tab_both", "style"),
        Output("consis_tab", "style"),
        Output("funnel_tab", "style"),
        Output("ranking_tab", "style"),
        Output("results_tabs", "value"),
        Output("results_tabs2", "value"),
    ],
    Input("result_selected", "value"),
)
def results_display(selected):
    """Display tabs based on result selection dropdown.

    Options:
        0 - Data & Transitivity: show data_tab and trans_tab
        1 - Forest plots: show forest_tab and tab2 (pairwise)
        2 - League tables: show league_tab and league_tab_both
        3 - Ranking: show ranking_tab only
        4 - Consistency & Reporting bias: show consis_tab and funnel_tab
    """
    style_display = {
        "color": "grey",
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
    }
    style_no_display = {
        "color": "grey",
        "display": "none",
        "justify-content": "center",
        "align-items": "center",
    }

    # Option 0: Data & Transitivity
    if selected == 0:
        return (
            style_display,  # data_tab
            style_display,  # trans_tab
            style_no_display,  # forest_tab
            style_no_display,  # tab2 (pairwise)
            style_no_display,  # league_tab
            style_no_display,  # league_tab_both
            style_no_display,  # consis_tab
            style_no_display,  # funnel_tab
            style_no_display,  # ranking_tab
            "data_tab",  # results_tabs value
            "trans_tab",  # results_tabs2 value
        )

    # Option 1: Forest plots
    elif selected == 1:
        return (
            style_no_display,  # data_tab
            style_no_display,  # trans_tab
            style_display,  # forest_tab
            style_display,  # tab2 (pairwise)
            style_no_display,  # league_tab
            style_no_display,  # league_tab_both
            style_no_display,  # consis_tab
            style_no_display,  # funnel_tab
            style_no_display,  # ranking_tab
            "forest_tab",  # results_tabs value
            "tab2",  # results_tabs2 value
        )

    # Option 2: League tables
    elif selected == 2:
        return (
            style_no_display,  # data_tab
            style_no_display,  # trans_tab
            style_no_display,  # forest_tab
            style_no_display,  # tab2 (pairwise)
            style_display,  # league_tab
            style_display,  # league_tab_both
            style_no_display,  # consis_tab
            style_no_display,  # funnel_tab
            style_no_display,  # ranking_tab
            "league_tab",  # results_tabs value
            "league_tab_both",  # results_tabs2 value
        )

    # Option 3: Ranking
    elif selected == 3:
        return (
            style_no_display,  # data_tab
            style_no_display,  # trans_tab
            style_no_display,  # forest_tab
            style_no_display,  # tab2 (pairwise)
            style_no_display,  # league_tab
            style_no_display,  # league_tab_both
            style_no_display,  # consis_tab
            style_no_display,  # funnel_tab
            style_display,  # ranking_tab
            "ranking_tab",  # results_tabs value
            "",  # results_tabs2 value (empty to hide)
        )

    # Option 4: Consistency & Reporting bias
    elif selected == 4:
        return (
            style_no_display,  # data_tab
            style_no_display,  # trans_tab
            style_no_display,  # forest_tab
            style_no_display,  # tab2 (pairwise)
            style_no_display,  # league_tab
            style_no_display,  # league_tab_both
            style_display,  # consis_tab
            style_display,  # funnel_tab
            style_no_display,  # ranking_tab
            "consis_tab",  # results_tabs value
            "funnel_tab",  # results_tabs2 value
        )

    # Default: show Data & Transitivity
    return (
        style_display,
        style_display,
        style_no_display,
        style_no_display,
        style_no_display,
        style_no_display,
        style_no_display,
        style_no_display,
        style_no_display,
        "data_tab",
        "trans_tab",
    )


## -------------------------------------------- INFOBOXES CALLBACKS ----------------------------------------------- ##


# Year info modal callback
@callback(
    Output("modal-body-year", "is_open"),
    [
        Input("open-body-year", "n_clicks"),
        Input("close-body-year", "n_clicks"),
    ],
    [State("modal-body-year", "is_open")],
)
def toggle_modal_year(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


### -------------------------------------------- FUNNEL CALLBACKS ----------------------------------------------- ###


# Funnel info modal callback for comparison-adjusted funnel plot
@callback(
    Output("modal-body-funnel", "is_open"),
    [
        Input("open-body-funnel", "n_clicks"),
        Input("close-body-funnel", "n_clicks"),
    ],
    [State("modal-body-funnel", "is_open")],
)
def toggle_modal_funnel(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Funnel info modal callback for standard funnel plot
@callback(
    Output("modal-body-funnel2", "is_open"),
    [
        Input("open-body-funnel2", "n_clicks"),
        Input("close-body-funnel2", "n_clicks"),
    ],
    [State("modal-body-funnel2", "is_open")],
)
def toggle_modal_funnel2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Inconsistency info modal callback for consistency checks
@callback(
    Output("modal-body-incons", "is_open"),
    [
        Input("open-body-incons", "n_clicks"),
        Input("close-body-incons", "n_clicks"),
    ],
    [State("modal-body-incons", "is_open")],
)
def toggle_modal_incons(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Scatter info modal callback for transitivity checks
@callback(
    Output("modal-body-scatter", "is_open"),
    [
        Input("open-body-scatter", "n_clicks"),
        Input("close-body-scatter", "n_clicks"),
    ],
    [State("modal-body-scatter", "is_open")],
)
def toggle_modal_scatter(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Graph info modal callback for network graph
@callback(
    Output("modal-body-graph", "is_open"),
    [
        Input("open-body-graph", "n_clicks"),
        Input("close-body-graph", "n_clicks"),
    ],
    [State("modal-body-graph", "is_open")],
)
def toggle_modal_graph(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Forest info modal callback
@callback(
    Output("modal-body-forest", "is_open"),
    [
        Input("open-body-forest", "n_clicks"),
        Input("close-body-forest", "n_clicks"),
    ],
    [State("modal-body-forest", "is_open")],
)
def toggle_modal_forest(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Forest2 info modal callback for bi-dimensional forest plot
@callback(
    Output("modal-body-forest2", "is_open"),
    [
        Input("open-body-forest2", "n_clicks"),
        Input("close-body-forest2", "n_clicks"),
    ],
    [State("modal-body-forest2", "is_open")],
)
def toggle_modal_forest2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


### -------------------------------------------- LEAGUE TABLE INFO CALLBACKS ----------------------------------------------- ###


# League table info modal callback
@callback(
    Output("modal-body-league1", "is_open"),
    [
        Input("open-body-league1", "n_clicks"),
        Input("close-body-league1", "n_clicks"),
    ],
    [State("modal-body-league1", "is_open")],
)
def toggle_modal_league1(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Risk of Bias info modal callback
@callback(
    Output("modal-body-RoB", "is_open"),
    [
        Input("open-body-RoB", "n_clicks"),
        Input("close-body-RoB", "n_clicks"),
    ],
    [State("modal-body-RoB", "is_open")],
)
def toggle_modal_rob(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# CINeMA info modal callback
@callback(
    Output("modal-body-cinema", "is_open"),
    [
        Input("open-body-cinema", "n_clicks"),
        Input("close-body-cinema", "n_clicks"),
    ],
    [State("modal-body-cinema", "is_open")],
)
def toggle_modal_cinema(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# League table 2 (both outcomes) info modal callback
@callback(
    Output("modal-body-league2", "is_open"),
    [
        Input("open-body-league2", "n_clicks"),
        Input("close-body-league2", "n_clicks"),
    ],
    [State("modal-body-league2", "is_open")],
)
def toggle_modal_league2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("modal-body-rank", "is_open"),
    [
        Input("open-body-rank", "n_clicks"),
        Input("close-body-rank", "n_clicks"),
    ],
    [State("modal-body-rank", "is_open")],
)
def toggle_modal_rank(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


## -------------------------------------------- END INFOBOXES CALLBACKS ----------------------------------------------- ##


## -------------------------------------------- CINEMA UPLOAD CALLBACKS ----------------------------------------------- ##


### ----- upload CINeMA data file (single outcome league table) ------ ###
@callback(
    [
        Output("cinema_net_data_STORAGE", "data"),
        Output("file2-list", "children"),
    ],
    [
        Input("datatable-secondfile-upload", "contents"),
    ],
    [
        State("datatable-secondfile-upload", "filename"),
        State("cinema_net_data_STORAGE", "data"),
        State("_outcome_select", "value"),
        State("number_outcomes_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def upload_cinema_single_outcome(
    contents, filename, cinema_net_data, outcome_idx, number_outcomes
):
    """
    Upload CINeMA report for single outcome league table.
    Stores the CINeMA data in cinema_net_data_STORAGE as a list (one entry per outcome).
    Only stores valid CINeMA files (with required columns).
    Data is persisted to localStorage.
    """
    from tools.utils import parse_contents
    from tools.functions_cinema import validate_cinema_csv

    if contents is None:
        raise PreventUpdate

    # Default outcome index
    if outcome_idx is None:
        outcome_idx = 0

    # Get number of outcomes
    if number_outcomes is None or number_outcomes < 1:
        number_outcomes = 1

    try:
        # Parse uploaded file
        cinema_df = parse_contents(contents, filename)

        # Validate CINeMA CSV format
        is_valid, error_msg = validate_cinema_csv(cinema_df)
        if not is_valid:
            print(f"CINeMA validation failed for {filename}: {error_msg}")
            # Return existing data unchanged, show error message
            return cinema_net_data if cinema_net_data else [], html.Span(
                f"Invalid file: {error_msg}", style={"color": "red", "fontSize": "12px"}
            )

        # Initialize storage list if empty
        if cinema_net_data is None or not isinstance(cinema_net_data, list):
            cinema_net_data = [None] * number_outcomes
        else:
            # Make a copy to avoid mutating the original
            cinema_net_data = list(cinema_net_data)

        # Ensure list is long enough
        while len(cinema_net_data) <= outcome_idx:
            cinema_net_data.append(None)

        # Store at correct outcome index
        cinema_net_data[outcome_idx] = cinema_df.to_json(orient="split")

        return cinema_net_data, html.Span(
            f"Loaded: {filename}",
            style={"color": "green", "fontSize": "12px"},
        )

    except Exception as e:
        print(f"Error uploading CINeMA file: {e}")
        return cinema_net_data if cinema_net_data else [], html.Span(
            f"Error: {str(e)}", style={"color": "red", "fontSize": "12px"}
        )


### ----- upload CINeMA data files (both outcomes league table) ------ ###
@callback(
    [
        Output("cinema_net_data_STORAGE2", "data"),
        Output("file-list-out1", "children"),
        Output("file-list-out2", "children"),
    ],
    [
        Input("datatable-secondfile-upload-1", "contents"),
        Input("datatable-secondfile-upload-2", "contents"),
    ],
    [
        State("datatable-secondfile-upload-1", "filename"),
        State("datatable-secondfile-upload-2", "filename"),
        State("cinema_net_data_STORAGE2", "data"),
    ],
    prevent_initial_call=True,
)
def upload_cinema_both_outcomes(
    contents1, contents2, filename1, filename2, cinema_net_data2
):
    """
    Upload CINeMA reports for both outcomes league table.
    Stores CINeMA data in cinema_net_data_STORAGE2 as a list [outcome1_json, outcome2_json].
    Only stores valid CINeMA files (with required columns).
    Data is persisted to localStorage.
    """
    from tools.utils import parse_contents
    from tools.functions_cinema import validate_cinema_csv

    # Determine which input triggered the callback
    triggered = [tr["prop_id"] for tr in dash.callback_context.triggered]

    # Initialize storage list if empty [outcome1, outcome2]
    if cinema_net_data2 is None or not isinstance(cinema_net_data2, list):
        cinema_net_data2 = [None, None]
    else:
        # Make a copy to avoid mutating the original
        cinema_net_data2 = list(cinema_net_data2)

    # Ensure list has at least 2 elements
    while len(cinema_net_data2) < 2:
        cinema_net_data2.append(None)

    file1_msg = ""
    file2_msg = ""

    try:
        # Process file 1 if uploaded (for outcome 1)
        if (
            "datatable-secondfile-upload-1.contents" in triggered
            and contents1 is not None
        ):
            cinema_df1 = parse_contents(contents1, filename1)
            # Validate CINeMA CSV format
            is_valid, error_msg = validate_cinema_csv(cinema_df1)
            if is_valid:
                cinema_net_data2[0] = cinema_df1.to_json(orient="split")
                file1_msg = html.Span(
                    f"Loaded: {filename1}",
                    style={"color": "green", "fontSize": "12px"},
                )
            else:
                file1_msg = html.Span(
                    f"Invalid: {error_msg}", style={"color": "red", "fontSize": "12px"}
                )

        # Process file 2 if uploaded (for outcome 2)
        if (
            "datatable-secondfile-upload-2.contents" in triggered
            and contents2 is not None
        ):
            cinema_df2 = parse_contents(contents2, filename2)
            # Validate CINeMA CSV format
            is_valid, error_msg = validate_cinema_csv(cinema_df2)
            if is_valid:
                cinema_net_data2[1] = cinema_df2.to_json(orient="split")
                file2_msg = html.Span(
                    f"Loaded: {filename2}",
                    style={"color": "green", "fontSize": "12px"},
                )
            else:
                file2_msg = html.Span(
                    f"Invalid: {error_msg}", style={"color": "red", "fontSize": "12px"}
                )

        return cinema_net_data2, file1_msg, file2_msg

    except Exception as e:
        print(f"Error uploading CINeMA files: {e}")
        return (
            cinema_net_data2,
            html.Span(f"Error: {str(e)}", style={"color": "red", "fontSize": "12px"}),
            html.Span(f"Error: {str(e)}", style={"color": "red", "fontSize": "12px"}),
        )


### ----- disable CINeMA toggle when no CINeMA file uploaded or invalid ------ ###
@callback(
    Output("rob_vs_cinema", "disabled"),
    [
        Input("cinema_net_data_STORAGE", "data"),
        Input("_outcome_select", "value"),
    ],
)
def disable_cinema_toggle(cinema_net_data, outcome_idx):
    """
    Disable CINeMA toggle switch when no valid CINeMA data is available for current outcome.
    cinema_net_data is a list with one entry per outcome.
    """
    from tools.functions_cinema import validate_cinema_csv

    if outcome_idx is None:
        outcome_idx = 0

    # Check if cinema data exists for current outcome (list format)
    if cinema_net_data is None or not isinstance(cinema_net_data, list):
        return True

    if len(cinema_net_data) <= outcome_idx or cinema_net_data[outcome_idx] is None:
        return True

    # Validate the stored CINeMA data has required columns
    try:
        cinema_df = pd.read_json(cinema_net_data[outcome_idx], orient="split")
        is_valid, _ = validate_cinema_csv(cinema_df)
        if not is_valid:
            return True
    except Exception:
        return True

    return False


@callback(
    Output("rob_vs_cinema-both", "disabled"),
    [
        Input("cinema_net_data_STORAGE2", "data"),
    ],
)
def disable_cinema_toggle_both(cinema_net_data2):
    """
    Disable CINeMA toggle switch for both outcomes table when no valid CINeMA data.
    cinema_net_data2 is a list [outcome1_json, outcome2_json].
    """
    from tools.functions_cinema import validate_cinema_csv

    # Check if cinema data exists for both outcomes (list format)
    if cinema_net_data2 is None or not isinstance(cinema_net_data2, list):
        return True

    if len(cinema_net_data2) < 2:
        return True

    if cinema_net_data2[0] is None or cinema_net_data2[1] is None:
        return True

    # Validate both CINeMA datasets have required columns
    try:
        cinema_df1 = pd.read_json(cinema_net_data2[0], orient="split")
        cinema_df2 = pd.read_json(cinema_net_data2[1], orient="split")
        is_valid1, _ = validate_cinema_csv(cinema_df1)
        is_valid2, _ = validate_cinema_csv(cinema_df2)
        if not is_valid1 or not is_valid2:
            return True
    except Exception:
        return True

    return False


## -------------------------------------------- END CINEMA UPLOAD CALLBACKS ----------------------------------------------- ##


## -------------------------------------------- DOWNLOAD CALLBACKS ----------------------------------------------- ##


@callback(
    Output("download-statistic", "data"),
    Input("statsettings", "n_clicks"),
    prevent_initial_call=True,
)
def download_statsettings(n_clicks):
    return send_file("Documentation/statistical_settings.pdf")


## -------------------------------------------- WARNING MESSAGE CALLBACKS ----------------------------------------------- ##


@callback(
    Output("warning_message", "children"),
    [
        Input("results_ready_STORAGE", "data"),
    ],
    [
        State("R_errors_STORAGE", "data"),
        State("protocol_link_STORAGE", "data"),
        State("effect_modifiers_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def display_warnings_on_results(
    results_ready,
    r_errors,
    protocol_value,
    effect_modifiers,
):
    """Display warnings on results page for missing data and R errors."""
    if not results_ready:
        return ""

    style = {
        "justify-self": "center",
        "align-self": "center",
        "white-space": "pre-wrap",
        "font-size": "medium",
        "color": "red",
        "padding": "10px",
        "background-color": "#fff3cd",
        "border": "1px solid #ffc107",
        "border-radius": "5px",
        "margin": "10px 0",
    }

    messages = []

    # Check for missing protocol link
    if not protocol_value:
        messages.append("⚠️ Protocol link is not provided.")

    # Check for missing effect modifiers
    if not effect_modifiers or len(effect_modifiers) == 0:
        messages.append(
            "⚠️ Effect modifiers are not provided. Boxplots cannot be generated for transitivity check."
        )

    # Check for R errors from analysis
    if r_errors:
        if r_errors.get("nma"):
            messages.append(f"❌ NMA Error: {r_errors['nma']}")
        if r_errors.get("pairwise"):
            messages.append(f"❌ Pairwise Error: {r_errors['pairwise']}")
        if r_errors.get("league"):
            messages.append(f"❌ League Table Error: {r_errors['league']}")
        if r_errors.get("funnel"):
            messages.append(f"❌ Funnel Plot Error: {r_errors['funnel']}")

    if messages:
        return html.Div(
            [html.Span("Warnings:\n" + "\n".join(messages), style=style)],
            style={"display": "flex", "justify-content": "center", "width": "100%"},
        )

    return ""
