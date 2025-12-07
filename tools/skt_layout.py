import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_cytoscape as cyto
from tools.navbar import Navbar
from tools.functions_skt_others import get_skt_elements, skt_stylesheet
import dash_ag_grid as dag
import pandas as pd

# from assets.storage import DEFAULT_DATA  # Not used
import numpy as np
import plotly.express as px, plotly.graph_objects as go
import dash_daq as daq
from tools.functions_skt_forestplot import __skt_options_forstplot, __skt_mix_forstplot
import os
from tools.skt_table import treat_compare_grid, modal_compare_grid

# Get AG Grid license key with fallback for development
AG_GRID_KEY = os.environ.get("AG_GRID_KEY", "")
from dash_yada import YadaAIO


# ============================================================================
# PLACEHOLDER DATA FOR INITIAL LAYOUT
# Real data will be populated from STORAGE via callbacks in knowledge_translation.py
# ============================================================================

# Empty placeholder DataFrames - will be populated from STORAGE
df = pd.DataFrame(
    {
        "Reference": [],
        "Treatment": [],
        "RR": [],
        "CI_lower": [],
        "CI_upper": [],
        "p-value": [],
        "direct": [],
        "indirect": [],
        "direct_low": [],
        "direct_up": [],
        "indirect_low": [],
        "indirect_up": [],
        "Certainty": [],
        "within_study": [],
        "reporting": [],
        "indirectness": [],
        "imprecision": [],
        "heterogeneity": [],
        "incoherence": [],
        "Comments": [],
        "Graph": [],
        "risk": [],
        "Scale_lower": [],
        "Scale_upper": [],
        "ab_difference": [],
    }
)

pw_data = pd.DataFrame()
p_score = pd.DataFrame({"treatment": [], "pscore": []})

# Placeholder lists
out_list = [["Outcome1", "Outcome2"]]  # Will be populated from outcome_names_STORAGE

outcome_list = [
    {"label": "Outcome1", "value": "Outcome1"},
    {"label": "Outcome2", "value": "Outcome2"},
]

treat_list = [[]]  # Will be populated from STORAGE
treatment_list = []

# Default range values (will be recalculated from STORAGE data)
up_rng, low_rng = 10, 0.1


def update_indirect_direct(row):
    if pd.isna(row["direct"]):
        row["indirect"] = pd.NA
    elif pd.isna(row["indirect"]):
        row["direct"] = pd.NA
    return row


# ============================================================================
# EMPTY PLACEHOLDER row_data_default - will be populated from STORAGE via callbacks
# The build_skt_advanced_row_data() function in skt_data_helpers.py handles this
# ============================================================================
row_data = pd.DataFrame(
    {
        "Reference": [],
        "risk": [],
        "Scale_lower": [],
        "Scale_upper": [],
        "Treatments": [],
        "pscore": [],
        "risk_range": [],
    }
)

row_data_default = row_data.copy()


style_certainty = {
    "whiteSpace": "pre",
    "display": "grid",
    "textAlign": "center",
    "alignItems": "center",
    "borderLeft": "solid 0.8px",
}
style_mixed = {
    "borderLeft": "solid 0.8px",
    "backgroud-color": "white",
    #    'lineHeight': '20px',
    "textAlign": "center",
    "whiteSpace": "pre",
    "display": "grid",
    "lineHeight": "normal",
    "alignItems": "center",
}

masterColumnDefs = [
    {
        "headerName": "Reference Treatment",
        "filter": True,
        "field": "Reference",
        "headerTooltip": "Click a treatment to open a nested table",
        "cellRenderer": "agGroupCellRenderer",
        "cellStyle": {"borderLeft": "solid 0.8px", "borderRight": "solid 0.8px"},
        # "cellRendererParams": {
        #     'innerRenderer': "DCC_GraphClickData",
        # },
    },
    {
        "headerName": "P score\n(Ranking)",
        "field": "pscore",
        "editable": True,
        "cellStyle": {"borderRight": "solid 0.8px"},
    },
    {
        "headerName": "Range of the risk\n(in dataset)",
        "field": "risk_range",
        "editable": True,
        "cellStyle": {"borderRight": "solid 0.8px"},
    },
    {
        "headerName": "Risk per 1000",
        "field": "risk",
        "editable": True,
        "cellStyle": {"color": "grey", "borderRight": "solid 0.8px"},
    },
    {
        "headerName": "The rationality of selecting the risk",
        "field": "rationality",
        "editable": True,
        "cellStyle": {"color": "grey", "borderRight": "solid 0.8px"},
    },
    {
        "headerName": "Scale lower\n(forestplots)",
        "field": "Scale_lower",
        "headerTooltip": "This is for the forest plots in the nested table",
        "editable": True,
        "cellStyle": {"color": "grey", "borderRight": "solid 0.8px"},
    },
    {
        "headerName": "Scale upper\n(forestplots)",
        "field": "Scale_upper",
        "headerTooltip": "This is for the forest plots in the nested table",
        "editable": True,
        "cellStyle": {"color": "grey", "borderRight": "solid 0.8px"},
    },
]
detailColumnDefs = [
    {
        "field": "Treatment",
        "headerName": "Treatment",
        #  "checkboxSelection": {"function": "params.data.Treatment !== 'Instruction'"},
        "sortable": False,
        "filter": True,
        "width": 130,
        "headerTooltip": "Click a cell to see the details of the corresponding comparison",
        #  "tooltipField": 'Treatment',
        #  "tooltipComponentParams": { "color": '#d8f0d3'},
        #  "tooltipComponent": "CustomTooltiptreat",
        "resizable": True,
        "cellStyle": {
            "display": "grid",
            "textAlign": "center",
            "whiteSpace": "pre",
            "lineHeight": "normal",
            "alignItems": "center",
        },
    },
    {
        "field": "RR",
        "headerName": "Mixed effect\n95%CI",
        "width": 180,
        "resizable": True,
        "cellStyle": {
            "styleConditions": [
                {"condition": "params.value =='RR'", "style": {**style_mixed}},
                {
                    "condition": "params.data.CI_lower < 1 && params.data.CI_upper < 1",
                    "style": {"color": "red", **style_mixed},
                },
                {
                    "condition": "params.data.CI_lower > 1 && params.data.CI_upper > 1",
                    "style": {"color": "red", **style_mixed},
                },
                {
                    "condition": "!(params.data.CI_lower < 1 && params.data.CI_upper < 1) && !(params.data.CI_lower > 1 && params.data.CI_upper > 1)",
                    "style": {**style_mixed},
                },
            ]
        },
    },
    # {"field": "ab_effect",
    #  "headerName": "Absolute Effect",
    #  'headerTooltip': 'Specify a value for the reference treatment in \'Risk per 1000\'',
    #  "width": 180,
    #  "resizable": True,
    #  'cellStyle': {'borderLeft': 'solid 0.8px',
    #                'backgroud-color':'white',
    #             #    'lineHeight': '20px',
    #                "textAlign":'center',
    #                'whiteSpace': 'pre',
    #                'display': 'grid',
    #                'lineHeight': 'normal',
    #                'alignItems': 'center'
    #                }
    #    },
    {
        "field": "ab_difference",
        "headerName": "Absolute Difference",
        "headerTooltip": "Specify a value for the reference treatment in 'Risk per 1000'",
        "width": 180,
        "resizable": True,
        "cellStyle": {
            "borderLeft": "solid 0.8px",
            "backgroud-color": "white",
            #    'lineHeight': '20px',
            "textAlign": "center",
            "whiteSpace": "pre",
            "display": "grid",
            "lineHeight": "normal",
            "alignItems": "center",
        },
    },
    {
        "field": "Graph",
        "cellRenderer": "DCC_GraphClickData",
        "headerName": "Forest plot",
        "width": 300,
        "resizable": True,
        "cellStyle": {
            "borderLeft": "solid 0.8px",
            "borderRight": "solid 0.8px",
            "backgroud-color": "white",
        },
    },
    {
        "field": "direct",
        "headerName": "Direct effect\n(95%CI)",
        "headerTooltip": "Click a cell with values to open the pairwise forest plot",
        "width": 170,
        "resizable": True,
        "cellStyle": {
            "color": "#707B7C",
            "textAlign": "center",
            "display": "grid",
            "whiteSpace": "pre",
            "lineHeight": "normal",
            "alignItems": "center",
        },
    },
    {
        "field": "indirect",
        "headerName": "Indirect effect\n(95%CI)",
        "width": 170,
        "resizable": True,
        "cellStyle": {
            "color": "#ABB2B9",
            "textAlign": "center",
            "display": "grid",
            "whiteSpace": "pre",
            "lineHeight": "normal",
            "alignItems": "center",
        },
    },
    {
        "field": "p-value",
        "headerName": "p-value\n(Consistency)",
        "width": 140,
        "resizable": True,
        "cellStyle": {
            "textAlign": "center",
            "display": "grid",
            "lineHeight": "normal",
            "whiteSpace": "pre",
            "alignItems": "center",
        },
    },
    {
        "field": "Certainty",
        "headerName": "Certainty",
        #  'headerTooltip': 'Hover the mouse on each cell to see the details',
        "filter": True,
        "width": 110,
        "resizable": True,
        "tooltipField": "Certainty",
        "tooltipComponentParams": {"color": "#d8f0d3"},
        "tooltipComponent": "CustomTooltip",
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value == 'High'",
                    "style": {
                        "backgroundColor": "rgb(90, 164, 105)",
                        **style_certainty,
                    },
                },
                {
                    "condition": "params.value == 'Low'",
                    "style": {"backgroundColor": "#B85042", **style_certainty},
                },
                {
                    "condition": "params.value == 'Moderate'",
                    "style": {
                        "backgroundColor": "rgb(248, 212, 157)",
                        **style_certainty,
                    },
                },
            ]
        },
    },
    {
        "field": "Comments",
        "width": 120,
        "headerTooltip": "Editable for adding comments",
        "resizable": True,
        "editable": True,
        "cellStyle": {
            "borderLeft": "solid 0.5px",
            "textAlign": "center",
            "display": "grid",
            "borderRight": "solid 0.8px",
        },
    },
]


getRowStyle = {
    "styleConditions": [
        {
            "condition": "params.data.RR === 'RR'",
            "style": {"backgroundColor": "#faead7", "fontWeight": "bold"},
        },
    ]
}


# sideBar={
#     "toolPanels": [
#         {
#             "id": "columns",
#             "labelDefault": "Columns",
#             "labelKey": "columns",
#             "iconKey": "columns",
#             "toolPanel": "agColumnsToolPanel",
#         },
#         {
#             "id": "filters",
#             "labelDefault": "Filters",
#             "labelKey": "filters",
#             "iconKey": "menu",
#             "toolPanel": "agFiltersToolPanel",
#         },
#     ],
#     "position": "left",
#     "defaultToolPanel": "filters",
# }

grid = dag.AgGrid(
    id="quickstart-grid",
    className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=AG_GRID_KEY,
    columnDefs=masterColumnDefs,
    rowData=row_data_default.to_dict("records"),
    masterDetail=True,
    # getRowStyle=getRowStyle,
    detailCellRendererParams={
        "detailGridOptions": {
            "columnDefs": detailColumnDefs,
            # "sideBar": sideBar,
            "rowHeight": 80,
            "rowDragManaged": True,
            "rowDragMultiRow": True,
            "rowDragEntireRow": True,
            "rowSelection": "multiple",
            "getRowStyle": getRowStyle,
            "detailCellClass": "ag-details-grid",
        },
        "detailColName": "Treatments",
        "suppressCallback": True,
    },
    dangerously_allow_code=True,
    defaultColDef={
        # "resizable": True,
        #    "sortable": False, "filter": True,
        "wrapText": True,
        "autoHeight": True,
        "enableRowGroup": False,
        "enableValue": False,
        "enablePivot": False,
        "cellStyle": {
            "whiteSpace": "pre",
            "display": "grid",
            "textAlign": "center",
            "alignItems": "center",
            "borderBottom": "solid 0.5px",
            #   'backgroundColor':'#faead7'
        },
        # "tooltipComponent": "CustomTooltip"
    },
    columnSize="sizeToFit",
    dashGridOptions={
        "suppressRowTransform": True,
        #    "domLayout":'print',
        "rowSelection": "multiple",
        #    "tooltipShowDelay": 100,
        "rowDragManaged": True,
        "rowDragMultiRow": True,
        "rowDragEntireRow": True,
        #    "detailRowHeight": 70+83*19,
        "detailRowAutoHeight": True,
    },
    getRowId="params.data.Reference",
    style={"width": "100%", "height": f"{46.5 * 20}px"},
)


####################################################################################################################################################################
####################################################################################################################################################################
OPTIONS = [{"label": "{}".format(col), "value": col} for col in ["age", "male"]]
model_transitivity = dbc.Modal(
    [
        dbc.ModalHeader("Transitivity Check Boxplots"),
        dbc.ModalBody(
            html.Div(
                [
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    html.P(
                                        "Choose effect modifier:",
                                        className="graph__title2",
                                        style={
                                            "display": "inline-block",
                                            "verticalAlign": "top",
                                            "fontSize": "12px",
                                            "marginBottom": "-10px",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="ddskt-trans",
                                        options=OPTIONS,
                                        clearable=True,
                                        placeholder="",
                                        className="tapEdgeData-fig-class",
                                        style={
                                            "width": "150px",
                                            "height": "30px",
                                            "display": "inline-block",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "Box plot",
                                                id="cinemaswitchlabel1_modal",
                                                style={
                                                    "display": "inline-block",
                                                    "fontSize": "large",
                                                    "paddingLeft": "10px",
                                                },
                                            ),
                                            daq.ToggleSwitch(
                                                id="box_kt_scatter",
                                                color="",
                                                size=30,
                                                labelPosition="bottom",
                                                style={
                                                    "display": "inline-block",
                                                    "margin": "auto",
                                                    "paddingLeft": "10px",
                                                    "paddingRight": "10px",
                                                },
                                            ),
                                            html.P(
                                                "Scatter plot",
                                                id="cinemaswitchlabel2_modal",
                                                style={
                                                    "display": "inline-block",
                                                    "margin": "auto",
                                                    "fontSize": "large",
                                                    "paddingRight": "0px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "float": "right",
                                            "padding": "5px 5px 5px 5px",
                                            "display": "inline-block",
                                            "marginTop": "-8px",
                                        },
                                    ),
                                ]
                            )
                        ],
                        style={"marginTop": "4px"},
                    ),
                    html.Div(
                        [
                            dcc.Graph(
                                id="boxplot_skt",
                                style={
                                    "height": "98%",
                                    "width": "-webkit-fill-available",
                                },
                                config={
                                    "editable": True,
                                    "edits": dict(
                                        annotationPosition=True,
                                        annotationTail=True,
                                        annotationText=True,
                                        axisTitleText=True,
                                        colorbarPosition=True,
                                        colorbarTitleText=True,
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
                                        "resetScale2d",
                                        "hoverCompareCartesian",
                                    ],
                                    "toImageButtonOptions": {
                                        "format": "png",  # one of png, svg,
                                        "filename": "custom_image",
                                        "scale": 5,
                                    },
                                    "displaylogo": False,
                                },
                            )
                        ],
                        style={
                            "marginTop": "-30px",
                            "height": "500px",
                        },
                    ),
                ]
            )
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close_trans", className="ms-auto", n_clicks=0)
        ),
    ],
    id="modal_transitivity",
    size="lg",
    is_open=False,
    scrollable=True,
    contentClassName="trans_content",
)

model_skt_stand1 = dbc.Modal(
    [
        dbc.ModalHeader("Pairwise Forest Plot", className="forest_head"),
        dbc.ModalBody(
            [
                dcc.Loading(
                    html.Div(
                        [
                            dcc.Graph(
                                id="forest-fig-pairwise",
                                style={
                                    "height": "99%",
                                    "max-height": "calc(52vw)",
                                    "width": "99%",
                                    "max-width": "calc(52vw)",
                                },
                                config={
                                    "editable": True,
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
                        style={"height": "450px"},
                    )
                ),
            ],
            className="forest_body",
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close_forest", className="ms-auto", n_clicks=0),
            className="forest_close",
        ),
    ],
    id="modal_forest",
    is_open=False,
    scrollable=True,
    contentClassName="forest_content",
)

model_skt_stand2 = dbc.Modal(
    [
        dbc.ModalHeader("Detail information", className="skt_info_head"),
        dbc.ModalBody(
            [
                html.Span(
                    "Treatment: FUM, Comparator: PBO",
                    className="skt_span_info",
                    id="treat_comp",
                ),
                html.Span(
                    "Randomized controlled trial: 3",
                    className="skt_span_info",
                    id="num_RCT",
                ),
                html.Span(
                    "Total participants: 1929",
                    className="skt_span_info",
                    id="num_sample",
                ),
                html.Span("Mean age: xxx", className="skt_span_info", id="mean_modif"),
            ],
            className="skt_info_body",
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close_compare", className="ms-auto", n_clicks=0),
            className="skt_info_close",
        ),
    ],
    id="skt_modal_copareinfo",
    is_open=False,
    scrollable=True,
    contentClassName="forest_content",
)


# Fullname Modal - shows full treatment names
from tools.skt_table import modal_fullname_grid

model_fullname = dbc.Modal(
    [
        dbc.ModalHeader(
            [html.P("Full names of all interventions")],
            className="skt_info_head_simple",
            id="modal_fullname_head",
        ),
        dbc.ModalBody(
            [
                dbc.Row(
                    [modal_fullname_grid],
                    style={
                        "width": "95%",
                        "justify-self": "center",
                        "justifyContent": "center",
                    },
                ),
            ],
            className="skt_info_body_simple",
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close_fullname_simple", className="ms-auto", n_clicks=0
            ),
            className="skt_info_close_simple",
        ),
    ],
    id="skt_modal_fullname_simple",
    is_open=False,
    scrollable=True,
    contentClassName="skt_modal_fullname",
)


# Ranking Modal - shows P-score heatmap
from tools.functions_skt_ranking import __ranking_plot_skt

model_ranking = dbc.Modal(
    [
        dbc.ModalHeader("P-score heatmap for ranking"),
        dbc.ModalBody(
            html.Div(
                [
                    dcc.Loading(
                        dcc.Graph(
                            id="tab-rank1",
                            figure=__ranking_plot_skt(),
                            style={
                                "height": "99%",
                                "max-height": "calc(51vh)",
                                "width": "100%",
                                "marginTop": "5%",
                            },
                            config={
                                "editable": True,
                                "edits": dict(
                                    annotationPosition=True,
                                    annotationTail=True,
                                    annotationText=True,
                                    axisTitleText=True,
                                    colorbarPosition=True,
                                    colorbarTitleText=False,
                                    titleText=False,
                                    legendPosition=True,
                                    legendText=True,
                                    shapePosition=True,
                                ),
                                "modeBarButtonsToRemove": [
                                    "toggleSpikelines",
                                    "resetScale2d",
                                    "pan2d",
                                    "select2d",
                                    "lasso2d",
                                    "autoScale2d",
                                    "hoverCompareCartesian",
                                ],
                                "toImageButtonOptions": {
                                    "format": "png",
                                    "filename": "custom_image",
                                    "scale": 5,
                                },
                                "displaylogo": False,
                            },
                        ),
                        style={"display": "grid", "justifyContent": "center"},
                    )
                ],
                style={
                    "marginTop": "-30px",
                    "height": "500px",
                },
            )
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close_rank", className="ms-auto", n_clicks=0)
        ),
    ],
    id="modal_ranking",
    size="lg",
    is_open=False,
    scrollable=True,
    contentClassName="trans_content",
)


radio_treattment = dbc.RadioItems(
    id="ref_selected",
    options=treatment_list,
    value="PBO",
    inline=True,
    inputStyle={"width": "30px"},
    style={"display": "contents", "fontSize": "medium"},
    labelCheckedStyle={"color": "red"},
)

display_treatment = [
    html.Span(treat, className="span_treat") for treat in treat_list[0]
]


model_password = dbc.Modal(
    [
        dbc.ModalBody(
            [
                html.Span("Input the password:", style={"fontSize": "large"}),
                dcc.Input(
                    id="password", className="upload_radio", style={"width": "150px"}
                ),
                html.Br(),
                dbc.Button(
                    "OK",
                    id="password_ok",
                    n_clicks=0,
                    style={"backgroundColor": "grey"},
                ),
            ]
        ),
    ],
    id="pass_model",
    is_open=True,
    contentClassName="pass_content",
    style={"display": "block"},
)
####################################################################################################################################################################
####################################################################################################################################################################
# instruct_plot = ('/assets/figure/instruction_skt1.png')

empty = [
    html.Span(
        "Instruction",
        className="skt_span1",
        style={"color": "#B85042", "fontWeight": "bold"},
    ),
    html.Span(
        [
            html.Strong("Ref:"),
            " selected reference treatment\n",
            html.Strong("Treatment:"),
            " click the cell to see the corresponding comparison information\n",
            html.Strong("Direct effect:"),
            " click to see the forestplot for the corresponding comparsion\n",
            html.Strong("Certainty:"),
            " hover your mouse see the details about certainty of evidence\n",
            html.Strong("Comments:"),
            " editable, add comments if necessary",
        ],
        className="empty_class",
    ),
    #  html.Img(src=instruct_plot, height="100px", style={'justify-self': 'center'})
]
options_effects = [
    {"label": "Add prediction interval to forestplots", "value": "PI"},
    {"label": "Add direct effects to forestplots", "value": "direct"},
    {"label": "Add indirect effects to forestplots", "value": "indirect"},
]


# def Sktpage():
#     return html.Div([Navbar(), model_password], id='skt_page_content')
# def Sktpage():
#     return html.Div([Navbar(), skt_home(), skt_layout(), skt_nonexpert()], id='skt_page_content')
def Sktpage():
    # Note: Navbar is added by the page layout in knowledge_translation.py
    # Do not add Navbar here to avoid duplicate navbars
    return html.Div(
        [switch_table(), html.Div([skt_nonexpert()], id="skt_sub_content")],
        id="skt_page_content",
    )


# def Sktpage():
#     return html.Div([Navbar(),skt_nonexpert()], id='skt_page_content')

# def skt_home():
#     return html.Div([
#         html.Div(id='skt_profile',
#                  children=[html.Br(), html.Br(),html.Br(), html.Br(),
#                      dcc.Markdown('Select your profile',
#                                                 className="markdown_style_main",
#                                                 style={
#                                                     "fontSize": '40px',
#                                                     'textAlign': 'center',
#                                                     'color':'#5c7780',
#                                                        }),
#                            html.Br(), html.Br(),
#                            dbc.Row([html.A([html.Img(src="/assets/icons/expert.png",
#                                         style={'width': '200px'}),
#                                     html.Span('Methodologists',className='profile_text'),
#                                         ],
#                                         id="expert_profile"),
#                                     html.A([html.Img(src="/assets/icons/nonexpert.png",
#                                         style={'width': '200px'}),
#                                         html.Span('Others',className='profile_text'),
#                                         ],
#                                         id="nonexpert_profile")
#                                         ], id='profile_row'),
#                                         ])
#     ], id="skt_profile_page")


def switch_table():
    return html.Div(
        [
            html.Br(),
            dcc.Markdown(
                "Knowledge Translation Tool",
                className="markdown_style_main",
                style={
                    "fontWeight": "bold",
                    "fontSize": "30px",
                    "textAlign": "center",
                    "color": "#5c7780",
                },
            ),
            # Project title row
            dbc.Row(
                [
                    html.Span(
                        "Project title:   ",
                        style={
                            "white-space": "pre",
                            "font-size": "large",
                            "color": "chocolate",
                        },
                    ),
                    html.Span(
                        "Not provided",
                        style={
                            "font-size": "large",
                            "color": "#333",
                        },
                        id="skt_project_title",
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "marginBottom": "5px",
                },
            ),
            # Protocol link row
            dbc.Row(
                [
                    html.Span(
                        "Protocol link:   ",
                        style={
                            "white-space": "pre",
                            "font-size": "large",
                            "color": "chocolate",
                        },
                    ),
                    dcc.Link(
                        children="Not provided",
                        href="#",
                        target="_blank",
                        style={
                            "color": "#0FA0CE",
                            "font-size": "large",
                        },
                        id="skt_protocol_link",
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "marginBottom": "10px",
                },
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.P(
                            "Standard Version",
                            id="skttable_1",
                            style={
                                "display": "inline-block",
                                "margin": "auto",
                                "fontSize": "16px",
                                "fontWeight": "bold",
                                "color": "chocolate",
                                "paddingLeft": "0px",
                            },
                        ),
                        daq.ToggleSwitch(
                            id="toggle_grid_select",
                            value=False,
                            color="green",
                            size=50,
                            vertical=False,
                            label={
                                "label": "",
                                "style": dict(color="white", font="0.5em"),
                            },
                            labelPosition="top",
                            style={
                                "display": "inline-block",
                                "margin": "auto",
                                "fontSize": "10px",
                                "paddingLeft": "10px",
                                "paddingRight": "10px",
                            },
                        ),
                        html.P(
                            "Advanced Version",
                            id="skttable_2",
                            style={
                                "display": "inline-block",
                                "margin": "auto",
                                "color": "green",
                                "fontWeight": "bold",
                                "fontSize": "16px",
                                "paddingRight": "0px",
                            },
                        ),
                    ],
                    style={
                        "justifyContent": "center",
                        # 'marginLeft': '70%',
                        "fontSize": "0.8em",
                        "marginTop": "2%",
                    },
                ),
                style={"justifyContent": "center", "width": "100%"},
            ),
        ]
    )


def skt_layout():
    return html.Div(
        [
            html.Div(
                id="skt_all",
                children=[
                    # dcc.Markdown('Scalable Knowledge Translation Tool',
                    #                                 className="markdown_style_main",
                    #                                 style={
                    #                                     "fontSize": '30px',
                    #                                     'textAlign': 'center',
                    #                                     'color':'#5c7780',
                    #                                        }),
                    # html.Button("Export to Excel", id="btn-excel-export"),
                    # html.Button("print", id="grid-printer-layout-btn"),
                    # html.Button("regular", id="grid-regular-layout-btn"),
                    # dbc.Col([
                    #     html.P(
                    #     "Standard skt",
                    #     id='skttable_1',
                    #     style={'display': 'inline-block',
                    #             'margin': 'auto',
                    #             'fontSize': '10px',
                    #             'paddingLeft': '0px'}),
                    #     daq.ToggleSwitch(
                    #         id='toggle_grid_select',
                    #         value = False,
                    #         color='green', size=30, vertical=False,
                    #         label={'label': "",
                    #                 'style': dict(color='white', font='0.5em')},
                    #         labelPosition="top",
                    #         style={'display': 'inline-block',
                    #                 'margin': 'auto', 'fontSize': '10px',
                    #                 'paddingLeft': '2px',
                    #                 'paddingRight': '2px'}),
                    #     html.P('league table',
                    #             id='skttable_2',
                    #             style={'display': 'inline-block',
                    #                 'margin': 'auto',
                    #                 'fontSize': '10px',
                    #                 'paddingRight': '0px'})],
                    #     style={'justifyContent': 'flex-end',
                    #             'marginLeft': '70%',
                    #             'fontSize': '0.8em', 'marginTop': '2%'},
                    #     ),
                    html.Br(),
                    html.Br(),
                    dcc.Markdown(
                        "Instruction: Hover your mouse over the table header to see how you can interact with it.",
                        className="markdown_style_main",
                        style={
                            "fontSize": "25px",
                            "textAlign": "start",
                            "fontFamily": "math",
                            "fontWeight": "bold",
                            "color": "rgb(184 80 66)",
                            "width": "90%",
                        },
                    ),
                    dbc.Row(
                        [
                            html.P(
                                f"Select outcome",
                                className="",
                                style={
                                    "display": "flex",
                                    "textAlign": "right",
                                    "alignItems": "center",
                                    "fontWeight": "bold",
                                    "color": "rgb(184, 80, 66)",
                                    "marginLeft": "10px",
                                    "fontSize": "large",
                                },
                            ),
                            dcc.Dropdown(
                                id="sktdropdown-out",
                                options=[
                                    {"label": "PASI90", "value": 0},
                                    {"label": "SAE", "value": 1},
                                ],
                                clearable=True,
                                placeholder="",
                                className="sktdropdown-out",
                            ),
                        ],
                        id="outselect_row",
                    ),
                    html.Br(),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Span(
                                            "Project Title", className="title_first"
                                        ),
                                        className="title_col1",
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "editable, put your project title here",
                                                id="title-instruction",
                                            ),
                                            html.A(
                                                html.Img(
                                                    src="/assets/icons/query.png",
                                                    style={
                                                        "width": "16px",
                                                        # "float":"right",
                                                    },
                                                )
                                            ),
                                        ],
                                        id="query-title",
                                    ),
                                    dbc.Col(
                                        dcc.Input(
                                            id="title_skt",
                                            value="Systematic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis",
                                            style={"width": "800px"},
                                        ),
                                        className="title_col2",
                                    ),
                                ],
                                className="row_skt",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Toast(
                                                [
                                                    dbc.Row(
                                                        [
                                                            html.Span(
                                                                "PICOS",
                                                                className="study_design",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.P(
                                                                        "editable, add more PICOS information",
                                                                        id="PICOS-instruction",
                                                                    ),
                                                                    html.A(
                                                                        html.Img(
                                                                            src="/assets/icons/query.png",
                                                                            style={
                                                                                "width": "16px",
                                                                                # "float":"right",
                                                                            },
                                                                        )
                                                                    ),
                                                                ],
                                                                id="query-PICOS",
                                                            ),
                                                        ]
                                                    ),
                                                    dcc.Textarea(
                                                        value="Patients: patients with psoriasis\n"
                                                        + "Primary outcome: PASI90\n"
                                                        + "Study design: randomized controlled trial",
                                                        className="skt_span1",
                                                        style={"width": "160%"},
                                                    ),
                                                    #   html.Span('Primary outcome: PASI90',className='skt_span1'),
                                                    #   html.Span('Study design: randomized control study', className='skt_span1'),
                                                ],
                                                className="tab1",
                                                headerClassName="headtab1",
                                                bodyClassName="bodytab1",
                                            )
                                        ],
                                        className="tab1_col",
                                    ),
                                    # dbc.Col([
                                    #          dbc.Row([html.Span('Interventions', className='inter_label'),
                                    #                 #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                    #                  ], style={'paddingTop': 0}),
                                    #          dbc.Toast(
                                    #                 display_treatment,
                                    #                 bodyClassName='skt_interbody',
                                    #                 className='skt_intervention',
                                    #                 headerClassName='headtab1',
                                    #                 id='treatment_toast'
                                    #               )
                                    #               ], className='tab2_col'),
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    html.Span(
                                                        "Interventions Diagram",
                                                        className="inter_label",
                                                    ),
                                                ],
                                                style={"paddingTop": 0},
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        cyto.Cytoscape(
                                                            id="cytoscape_skt",
                                                            responsive=False,
                                                            autoRefreshLayout=True,
                                                            minZoom=0.6,
                                                            maxZoom=1.2,
                                                            panningEnabled=True,
                                                            elements=get_skt_elements(),
                                                            style={
                                                                "height": "40vh",
                                                                "width": "100%",
                                                                "marginTop": "-2%",
                                                                "z-index": "999",
                                                                "paddingLeft": "-10px",
                                                                # 'max-width': 'calc(52vw)',
                                                            },
                                                            layout={
                                                                "name": "circle",
                                                                "animate": False,
                                                                "fit": True,
                                                            },
                                                            stylesheet=skt_stylesheet(),
                                                        ),
                                                        style={
                                                            "borderRight": "3px solid #B85042",
                                                            "width": "50%",
                                                        },
                                                    ),
                                                    dbc.Col(
                                                        html.Span(id="trigger_info"),
                                                        style={
                                                            "width": "50%",
                                                            "alignItems": "center",
                                                            "display": "grid",
                                                        },
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="tab3_col",
                                    ),
                                ],
                                className="row_skt",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Toast(
                                            [
                                                html.Span(
                                                    "Overall Info",
                                                    className="study_design",
                                                ),
                                                html.Span(
                                                    "Number of studies: 96",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of participants: 1020",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of interventions: 20",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of comparisons with direct evidence: 13",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of comparisons without direct evidence: 8 \n",
                                                    className="skt_span1",
                                                    #  style={'borderBottom': 'dashed 1px gray'}
                                                ),
                                            ],
                                            className="skt_studyinfo",
                                            headerClassName="headtab1",
                                        ),
                                        style={"width": "35%"},
                                    ),
                                    dbc.Col(
                                        dbc.Toast(
                                            [
                                                html.Span(
                                                    "Potential effect modifiers Info",
                                                    className="skt_span1",
                                                    style={
                                                        "color": "#B85042",
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                                html.Span(
                                                    "Mean age: 45.3",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Mean male percentage: 43.4%",
                                                    className="skt_span1",
                                                ),
                                                html.Button(
                                                    "Transitivity check",
                                                    id="trans_button",
                                                    className="sub-button",
                                                    style={
                                                        "color": "rgb(118 135 123)",
                                                        "backgroundColor": "#dedecf",
                                                        "display": "inline-block",
                                                        "justify-self": "center",
                                                        "border": "unset",
                                                        "padding": "4px",
                                                    },
                                                ),
                                            ],
                                            className="skt_studyinfo",
                                            headerClassName="headtab1",
                                            bodyClassName="bodytab2",
                                        ),
                                        style={"width": "15%", "marginLeft": "1%"},
                                    ),
                                    model_transitivity,
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                html.Span(
                                                    "Options (For the forest plots in the table)",
                                                    className="option_select",
                                                ),
                                                style={
                                                    "display": "grid",
                                                    "paddingTop": "unset",
                                                },
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Toast(
                                                        [
                                                            html.Span(
                                                                "Enter the minimum clinical difference value:",
                                                                className="select_outcome",
                                                            ),
                                                            dcc.Input(
                                                                id="range_lower",
                                                                type="text",
                                                                name="risk",
                                                                value=0.2,
                                                                placeholder="e.g. 0.2",
                                                                style={"width": "80px"},
                                                            ),
                                                            # html.Span('Enter the range of equvalence upper:',className='select_outcome'),
                                                            # dcc.Input(id="range_upper",
                                                            #             type="text",
                                                            #             name='risk',
                                                            #             value=1.25,
                                                            #             placeholder="e.g. 1.25",style={'width':'80px'})
                                                        ],
                                                        className="skt_studyinfo2",
                                                        bodyClassName="slect_body",
                                                        headerClassName="headtab1",
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Checklist(
                                                                options=options_effects,
                                                                value=[
                                                                    "PI",
                                                                    "direct",
                                                                    "indirect",
                                                                ],
                                                                id="checklist_effects",
                                                                style={
                                                                    "display": "grid",
                                                                    "alignItems": "end",
                                                                },
                                                            ),
                                                            # html.Div([
                                                            #     html.Div([ html.P("The forest plots in the table will be presented on a logarithmic scale.",
                                                            #      id='logscale-instruction'),
                                                            #     html.A(
                                                            #     html.Img(
                                                            #         src="/assets/icons/query.png",
                                                            #         style={
                                                            #             "width": "16px",
                                                            #             # "float":"right",
                                                            #             },
                                                            #     )),],id="query-logscale",),
                                                            #     html.P("log scale", id='',
                                                            #             style={'display': 'inline-block',
                                                            #                     'fontSize': '12px',
                                                            #                     'paddingLeft': '10px'}),
                                                            #         daq.ToggleSwitch(id='nomal_vs_log',
                                                            #                         color='', size=30,
                                                            #                         labelPosition="bottom",
                                                            #                         style={'display': 'inline-block',
                                                            #                                 'margin': 'auto',
                                                            #                                 'paddingLeft': '10px',
                                                            #                                 'paddingRight': '10px'}),
                                                            #         html.P('absolute scale', id='',
                                                            #             style={'display': 'inline-block', 'margin': 'auto',
                                                            #                     'fontSize': '12px',
                                                            #                     'paddingRight': '0px'}),
                                                            #         html.Div([ html.P("The forest plots in the table will be presented on a absolute scale.",
                                                            #                    id='abscale-instruction'),
                                                            #         html.A(
                                                            #         html.Img(
                                                            #             src="/assets/icons/query.png",
                                                            #             style={
                                                            #                 "width": "16px",
                                                            #                 # "float":"right",
                                                            #                 },
                                                            #         )),],id="query-abscale",),
                                                            #         ], style={'display': 'inline-block', 'marginTop': '0px'})
                                                        ]
                                                    ),
                                                ],
                                                style={
                                                    "display": "grid",
                                                    "grid-template-columns": "1fr 1fr",
                                                },
                                            ),
                                        ],
                                        style={
                                            "width": "38%",
                                            "marginLeft": "1%",
                                            "border": "1px dashed rgb(184, 80, 66)",
                                            "display": "grid",
                                        },
                                    ),
                                ],
                                className="row_skt",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [grid, model_skt_stand1, model_skt_stand2],
                                        className="skt_col2",
                                        id="grid_type",
                                    ),
                                ],
                                className="skt_rowtable",
                            ),
                            html.Br(),
                            html.Br(),
                            dbc.Row(),
                        ]
                    ),
                    dbc.Col(
                        [
                            dcc.Markdown(
                                "Expert Committee Members",
                                className="markdown_style_main",
                                style={
                                    "fontSize": "20px",
                                    "textAlign": "center",
                                    "color": "orange",
                                    "borderBottom": "2px solid",
                                    "fontWeight": "bold",
                                    "height": "fit-content",
                                    # 'marginLeft': '20px',
                                    "width": "100%",
                                    "marginTop": "0",
                                },
                            ),
                            dcc.Markdown(
                                "Toshi Furukawa, Isabelle Boutron, Emily Karahalios, Tianjing li, Michael Mccaul, Adriani Nikolakopoulou, Haliton Oliveira, Thodoris Papakonstantinou, Georgia Salanti, Guido Schwarzer, Ian Saldanha, Nicky Welton, Sally Yaacoub",
                                className="markdown_style",
                                style={"color": "black", "fontSize": "large"},
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                        ],
                        style={"width": "95%", "paddingLeft": "5%"},
                    ),
                ],
                style={"display": "block"},
            ),
        ],
        id="sky_expert_page",
    )


#############################################SKT Non-experts####################################################################################################
ROUTINE = "/assets/icons/routine.png"
SIDE = "/assets/icons/side_effect.png"
CONT = "/assets/icons/contrain.png"
VISIT = "/assets/icons/visit.png"
COST = "/assets/icons/cost.png"
RANK = "/assets/ranking.png"
# from tools.functions_chatbot import render_chatbot


model_skt_compare_simple = dbc.Modal(
    [
        dbc.ModalHeader(
            [html.P("")], className="skt_info_head_simple", id="modal_info_head"
        ),
        dbc.ModalBody(
            [
                # First row for the risk input
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span(
                                    "Enter the risk for comparator (per 1000):",
                                    className="abvalue_simple",
                                ),
                                dcc.Input(
                                    id="simple_abvalue",
                                    type="text",
                                    name="risk",
                                    placeholder="e.g. 20",
                                    style={"width": "80px", "marginLeft": "15px"},
                                ),
                                html.Span(
                                    [
                                        html.P(
                                            "The risk of comparator ranges from 10 per 1000 to 30 per 1000 in the dataset."
                                        )
                                    ],
                                    className="abvalue_range",
                                    id="risk_range",
                                ),
                                html.Br(),
                            ]
                        ),
                    ]
                ),
                # Second row for displaying other information
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span(
                                    "Outcome: PASI90",
                                    className="skt_span_info2",
                                    id="treat_comp",
                                ),
                                html.Span(
                                    "Treatment: ADA",
                                    className="skt_span_info2",
                                    id="num_RCT",
                                ),
                                html.Span(
                                    "Comparator: PBO",
                                    className="skt_span_info2",
                                    id="num_RCT",
                                ),
                                html.Span(
                                    "Absolute difference: 30 more per 1000",
                                    className="skt_span_info2",
                                    id="num_sample",
                                ),
                                html.Span(
                                    "CI: 10 per 1000 to 40 per 1000",
                                    className="skt_span_info2",
                                    id="mean_modif",
                                ),
                            ],
                            style={"marginRight": "20px"},
                            id="text_info_col",
                        ),
                        dbc.Col(
                            dcc.Loading(
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="barplot_compare",
                                            style={"width": "100%"},
                                            config={
                                                "editable": True,
                                                "displayModeBar": False,
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
                                    style={"width": "100%"},
                                )
                            ),
                        ),  # Empty column for alignment
                    ],
                    style={
                        "display": "grid",
                        "grid-template-columns": "1fr 1fr",
                        "alignItems": "center",
                        "borderBottom": "2px solid green",
                    },
                ),
                dbc.Row(
                    [
                        html.Span("Study Information", className="studyinfo_simple"),
                        modal_compare_grid,
                    ],
                    style={
                        "width": "95%",
                        "justify-self": "center",
                        "justifyContent": "center",
                    },
                ),
            ],
            className="skt_info_body_simple",
        ),
        # Modal footer with close button
        dbc.ModalFooter(
            dbc.Button(
                "Close", id="close_compare_simple", className="ms-auto", n_clicks=0
            ),
            className="skt_info_close_simple",
        ),
    ],
    id="skt_modal_compare_simple",  # Corrected id for typo
    is_open=False,
    scrollable=True,
    contentClassName="skt_modal_simple",
)


from tools.yada import yada_stand


def skt_nonexpert():
    return html.Div(
        [
            yada_stand,
            html.Div(
                id="skt_all",
                children=[
                    # dcc.Markdown('Scalable Knowledge Translation Tool',
                    #                                 className="markdown_style_main",
                    #                                 style={
                    #                                     "fontSize": '30px',
                    #                                     'textAlign': 'center',
                    #                                     'color':'#5c7780',
                    #                                        }),
                    html.Br(id="yoda_stand_start"),
                    html.Br(),
                    dcc.Markdown(
                        "Instruction: Hover your mouse over the table header to see how you can interact with it.",
                        className="markdown_style_main",
                        style={
                            "fontSize": "25px",
                            "textAlign": "start",
                            "fontFamily": "math",
                            "fontWeight": "bold",
                            "color": "rgb(184 80 66)",
                            "width": "90%",
                        },
                    ),
                    html.Div(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Span(
                                            "Project Title", className="title_first"
                                        ),
                                        className="title_col1",
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "editable, put your project title here",
                                                id="title-instruction",
                                            ),
                                            html.A(
                                                html.Img(
                                                    src="/assets/icons/query.png",
                                                    style={
                                                        "width": "16px",
                                                        # "float":"right",
                                                    },
                                                )
                                            ),
                                        ],
                                        id="query-title",
                                    ),
                                    dbc.Col(
                                        dcc.Input(
                                            id="title_skt",
                                            value="Systematic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis",
                                            style={"width": "800px"},
                                        ),
                                        className="title_col2",
                                    ),
                                ],
                                className="row_skt",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Toast(
                                                [
                                                    dbc.Row(
                                                        [
                                                            html.Span(
                                                                "PICOS",
                                                                className="study_design",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.P(
                                                                        "editable, add more PICOS information",
                                                                        id="PICOS-instruction",
                                                                    ),
                                                                    html.A(
                                                                        html.Img(
                                                                            src="/assets/icons/query.png",
                                                                            style={
                                                                                "width": "16px",
                                                                                # "float":"right",
                                                                            },
                                                                        )
                                                                    ),
                                                                ],
                                                                id="query-PICOS",
                                                            ),
                                                        ]
                                                    ),
                                                    dcc.Textarea(
                                                        value="Patients: patients with psoriasis\n"
                                                        + "Primary outcome: PASI90, SAE\n"
                                                        + "Study design: randomized control trial",
                                                        className="skt_span1",
                                                        style={"width": "200%"},
                                                    ),
                                                    #   html.Span('Primary outcome: PASI90',className='skt_span1'),
                                                    #   html.Span('Study design: randomized control study', className='skt_span1'),
                                                ],
                                                className="tab1",
                                                headerClassName="headtab1",
                                                bodyClassName="bodytab1",
                                            )
                                        ],
                                        className="tab1_col2",
                                    ),
                                    dbc.Col(
                                        dbc.Toast(
                                            [
                                                html.Span(
                                                    "Overall Info",
                                                    className="study_design",
                                                ),
                                                html.Span(
                                                    "Number of studies: 96",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of interventions: 20",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of participants: 1020",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Number of comparisons: 190",
                                                    className="skt_span1",
                                                ),
                                            ],
                                            className="skt_studyinfo",
                                            headerClassName="headtab1",
                                        ),
                                        style={"width": "25%"},
                                    ),
                                    dbc.Col(
                                        dbc.Toast(
                                            [
                                                html.Span(
                                                    "Potential effect modifiers Info",
                                                    className="skt_span1",
                                                    style={
                                                        "color": "#B85042",
                                                        "fontWeight": "bold",
                                                    },
                                                ),
                                                html.Span(
                                                    "Mean age: 45.3",
                                                    className="skt_span1",
                                                ),
                                                html.Span(
                                                    "Mean male percentage: 43.4%",
                                                    className="skt_span1",
                                                ),
                                                html.Button(
                                                    "Distribution of modifiers",
                                                    id="trans_button",
                                                    className="sub-button",
                                                    style={
                                                        "color": "rgb(118 135 123)",
                                                        "backgroundColor": "#dedecf",
                                                        "display": "inline-block",
                                                        "justify-self": "center",
                                                        "border": "unset",
                                                        "padding": "4px",
                                                    },
                                                ),
                                            ],
                                            className="skt_studyinfo",
                                            headerClassName="headtab1",
                                            bodyClassName="bodytab2",
                                        ),
                                        style={"width": "25%", "marginLeft": "1%"},
                                    ),
                                    model_transitivity,
                                ],
                                className="row_skt",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Row(
                                                        [
                                                            html.Span(
                                                                "Interventions Diagram",
                                                                className="inter_label",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.P(
                                                                        "Select nodes/edges to display results for specific interventions or comparisons in the table below.",
                                                                        id="diagram-instruction",
                                                                    ),
                                                                    html.A(
                                                                        html.Img(
                                                                            src="/assets/icons/query.png",
                                                                            style={
                                                                                "width": "16px",
                                                                                # "float":"right",
                                                                            },
                                                                        )
                                                                    ),
                                                                ],
                                                                id="query-diagram",
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            html.Span(
                                                                "Ask Dr.Bot",
                                                                className="skt_span1",
                                                                style={
                                                                    "color": "#B85042",
                                                                    "fontWeight": "bold",
                                                                },
                                                            ),
                                                            html.Img(
                                                                src="/assets/icons/chatbot.png",
                                                                style={
                                                                    "height": 30,
                                                                    "marginLeft": "7px",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "justifyContent": "center",
                                                            "alignItems": "center",
                                                        },
                                                    ),
                                                    #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                                ],
                                                style={
                                                    "paddingTop": 0,
                                                    "display": "grid",
                                                    "grid-template-columns": "1fr 1fr",
                                                },
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        cyto.Cytoscape(
                                                            id="cytoscape_skt2",
                                                            responsive=False,
                                                            autoRefreshLayout=True,
                                                            minZoom=0.6,
                                                            maxZoom=1.5,
                                                            panningEnabled=True,
                                                            elements=get_skt_elements(),
                                                            style={
                                                                "height": "100%",
                                                                "width": "100%",
                                                                "marginTop": "-2%",
                                                                "z-index": "999",
                                                                "paddingLeft": "-10px",
                                                                # 'max-width': 'calc(52vw)',
                                                            },
                                                            layout={
                                                                "name": "circle",
                                                                "animate": False,
                                                                "fit": True,
                                                            },
                                                            stylesheet=skt_stylesheet(),
                                                        ),
                                                        style={
                                                            "borderRight": "3px solid #B85042",
                                                            "width": "50%",
                                                        },
                                                    ),
                                                    # dbc.Col(render_chatbot(), style={'width':'50%','justify-items': 'center',"height": "500px"})
                                                    # dbc.Col([
                                                    #     # html.Span('Interventions practical issues',className='skt_span1',
                                                    #     #               style={'color': '#B85042', 'fontWeight': 'bold'}),
                                                    #         dbc.Row([
                                                    #                 dbc.Col([html.Img(src=ROUTINE,
                                                    #                 width="45px", style={'justify-self':'center'},
                                                    #                 className='medpractice', id='routine'),
                                                    #                 html.Span('Medical routine',className= 'main_results1')],
                                                    #                 className='col_results1'),
                                                    #                 dbc.Col([html.Img(src=CONT,
                                                    #                 width="45px", style={'justify-self':'center'},
                                                    #                 className='medpractice', id='cont'),
                                                    #                 html.Span('Contraindications', className= 'main_results1')],
                                                    #                 className='col_results1'),
                                                    #                 dbc.Col([html.Img(src=SIDE,
                                                    #                 width="45px", style={'justify-self':'center'},
                                                    #                 className='medpractice', id='side'),
                                                    #                 html.Span('Side effects', className= 'main_results1')],
                                                    #                 className='col_results1'),
                                                    #                 dbc.Col([html.Img(src=VISIT, n_clicks=0,
                                                    #                 width="45px", style={'justify-self':'center'},
                                                    #                 className='medpractice', id='visit'),
                                                    #                 html.Span('Visit and test', className= 'main_results1')],
                                                    #                 className='col_results1'),
                                                    #                 dbc.Col([html.Img(src=COST,
                                                    #                 width="45px", style={'justify-self':'center'},
                                                    #                 className='medpractice', id='cost'),
                                                    #                 html.Span('Cost', className= 'main_results1')],
                                                    #                 className='col_results1'),
                                                    #                 ],
                                                    #                 style={'width' : '-webkit-fill-available',
                                                    #                             'justifyContent': 'center',}
                                                    #                             ),
                                                    #         dbc.Row(html.Span(id='trigger_info2'),
                                                    #             style={'alignItems': 'center','marginBottom': '50%',
                                                    #                    'display': 'grid','backgroundColor':'burlywood', 'height': '95%'})
                                                    #                             ],style={'width':'50%', 'justifyContent': 'center','display': 'grid'})
                                                ]
                                            ),
                                        ],
                                        className="tab3_col2",
                                    )
                                ],
                                className="row_skt",
                            ),
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            model_skt_compare_simple,
                                            # dbc.Row([dbc.Col([
                                            # html.Span('Absolute Values for Comparators (per 1000)',className='skt_span1',
                                            #         style={'color': '#B85042', 'fontWeight': 'bold'}),
                                            #         outcome_absolute],className='out_abs_col'),
                                            #         # dbc.Col([html.Img(src=RANK, style={'justify-self':'center','width':'300px'}, id='rank_img')],className='out_rank_col')
                                            #         ], style={'justifyContent':'space-around'}),
                                            dbc.Row(
                                                treat_compare_grid,
                                                style={
                                                    "width": "95%",
                                                    "justify-self": "center",
                                                },
                                            ),
                                        ],
                                        className="tab3_col2",
                                        id="col_nonexpert",
                                    )
                                ],
                                className="row_skt",
                            ),
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    dbc.Col(
                        [
                            dcc.Markdown(
                                "Expert Committee Members",
                                className="markdown_style_main",
                                style={
                                    "fontSize": "20px",
                                    "textAlign": "center",
                                    "color": "orange",
                                    "borderBottom": "2px solid",
                                    "fontWeight": "bold",
                                    "height": "fit-content",
                                    # 'marginLeft': '20px',
                                    "width": "100%",
                                    "marginTop": "0",
                                },
                            ),
                            dcc.Markdown(
                                "Toshi Furukawa, Isabelle Boutron, Emily Karahalios, Tianjing li, Michael Mccaul, Adriani Nikolakopoulou, Haliton Oliveira, Thodoris Papakonstantinou, Georgia Salanti, Guido Schwarzer, Ian Saldanha, Nicky Welton, Sally Yaacoub",
                                className="markdown_style",
                                style={"color": "black", "fontSize": "large"},
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                        ],
                        style={"width": "95%", "paddingLeft": "5%"},
                    ),
                ],
                style={"display": "block"},
            ),
        ],
        id="skt_nonexpert_page",
        style={"display": "block"},
    )


####################################################################################################################################################################
####################################################################################################################################################################

# ============================================================================
# PLACEHOLDER df_league - will be populated from STORAGE via callbacks
# The module-level processing has been removed. League table data is now
# derived from league_STORAGE in the knowledge_translation.py callbacks.
# ============================================================================

df_league = pd.DataFrame({"Treatment": []})
n_row = 0
treatnames = []

# NOTE: The following large section of module-level code that processed df_league
# has been removed. This included:
# - Loading db/skt/league_table.csv
# - Building forest plot figures for each cell
# - Complex data transformations
# All of this is now handled dynamically through STORAGE callbacks.

# Placeholder for column definitions (will be built dynamically from STORAGE data)

default_style = {
    "whiteSpace": "pre",
    "display": "grid",
    "textAlign": "center",
    # 'alignItems': 'center',
    "border": "solid 0.5px gray",
    # 'lineHeight': 'initial'
    "height": "163px",
    "lineHeight": "normal",
}

columnDefs2 = [
    {
        "field": "Treatment",
        "headerName": "Treatment",
        "tooltipField": "ticker",
        "tooltipComponentParams": {"color": "#d8f0d3"},
        "sortable": False,
        "filter": True,
        "cellStyle": {
            "fontWeight": "bold",
            "backgroundColor": "#B85042",
            "color": "white",
            "fontSize": "12px",
            **default_style,
        },
    }
] + [
    {
        "field": i,
        "cellRenderer": "DCC_GraphClickData",
        "maxWidth": 500,
        "minWidth": 300,
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": f"params.value === '{i}'",
                    "style": {"backgroundColor": "antiquewhite", **default_style},
                },
                {"condition": f"params.value !== '{i}'", "style": {**default_style}},
            ]
        },
    }
    for i in treatnames
]
############################League Table######################################################

# grid2 = dag.AgGrid(
#     id="grid2",
#     rowData=df_league.to_dict("records"),
#     columnDefs= columnDefs2,
#     defaultColDef={"resizable": False,
#                    "filter": True, "minWidth":125,
#                    "wrapText": True,
#                    'autoHeight': True,
#                     'cellStyle': {'whiteSpace': 'pre',
#                                   'display': 'grid2',
#                                   'textAlign': 'center',
#                                 #   'alignItems': 'center',
#                                   'backgroundColor':'#E7E8D1',
#                                   'border': 'solid 0.5px gray',
#                                 #   "styleConditions":styleConditions
#                                     # "styleConditions": [
#                                     #   {"condition": "params.value === 'ADA'",
#                                     #    "style": {"backgroundColor": "green"}}]
#                                 },
#                    },
#     columnSize="sizeToFit",
#     # dashGridOptions = {'suppressRowTransform': True,
#     #                    "rowSelection": "multiple",
#     #                    "tooltipShowDelay": 100},
#     style={'width': '1200px','height': f'{48 + 163 * n_row}px'},
# )

# checklist = dcc.Checklist(options= df_league.columns[1:], value= df_league.columns[1:3].values,
#                           id='checklist_treat', style={'display': 'contents'})
# button_clear=html.Button('select all', id='clear-val', n_clicks=0)
