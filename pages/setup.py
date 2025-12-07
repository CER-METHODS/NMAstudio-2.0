###############################SETUP page###########################

import dash
import json
import os
import re
from urllib.parse import urlparse
from dash import Input, Output, State, callback, html, dcc, ALL
import dash_bootstrap_components as dbc

from assets.alerts import (  # type: ignore
    R_errors_data,
    R_errors_nma,
    R_errors_pair,
    R_errors_league,
    R_errors_funnel,
    dataupload_error,
)
from assets.storage import (  # type: ignore
    STORAGE,
    STORAGEOUTPUT,
    STORAGESTATE,
    EMPTY_STORAGE,
    __load_project,
    __get_state_of,
)
from assets.psoriasisDemo3outcomes import PSORIASIS_3OUTCOMES_DATA  # type: ignore
from assets.Tabs.saveload_modal_button import saveload_modal  # type: ignore
from assets.modal_values import file_upload_controls2  # type: ignore

# modal_checks moved to app.py global layout (dbc.Modal doesn't render in page layouts)
from tools.functions_project_setup import (
    __selectbox1_options,
    __update_options,
    __primaryout_selection,
    __outcomes_type,
    __variable_selection,
    __effect_modifier_options,
)  # type: ignore
from tools.functions_modal_SUBMIT_data import (
    __data_trans,
)  # type: ignore
from tools.functions_NMA_runs import (
    __modal_submit_checks_DATACHECKS,
    __modal_submit_checks_NMA_new,
    __modal_submit_checks_PAIRWISE_new,
    __modal_submit_checks_LT_new,
    __modal_submit_checks_FUNNEL_new,
)  # type: ignore


dash.register_page(__name__, path="/setup")

layout = html.Div(
    id="upload_page",
    style={"display": "grid"},
    children=[
        dcc.Location(id="setup_page_location", refresh=True),
        # STORAGE moved to app.py global layout for proper localStorage persistence
        # Alert modals moved to app.py global layout (available on all pages)
        # Hidden placeholder components for dynamic callbacks (prevent "nonexistent object" errors)
        html.Div(
            [
                dcc.Checklist(id="effect_modifier_checkbox", options=[], value=[]),
                dcc.Checklist(id="no_effect_modifier", options=[], value=[]),
            ],
            style={"display": "none"},
        ),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                html.Div(
                    [
                        html.A(
                            html.Img(
                                src="/assets/icons/reset.png",
                                style={"width": "40px", "filter": "invert()"},
                            ),  ##DIV RESET  BUTTON
                            id="reset_project",
                            href="#",
                            style={"display": "grid", "justifyItems": "center"},
                            className="reset-button",
                        ),
                        dbc.Tooltip(
                            "Reset project - uploaded data will be lost",
                            style={
                                "color": "black",
                                "fontSize": 9,
                                "letterSpacing": "0.2rem",
                            },
                            placement="top",
                            target="reset_project",
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                    },
                ),
                dcc.ConfirmDialog(
                    id="confirm-reset",
                    message="All changes will be lost! Are you sure you want to continue?",
                ),
                dbc.Button(
                    "Load Psoriasis Demo Project",
                    id="load_psor",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#00ab9c",
                        "height": "40px",
                    },
                ),
                dcc.ConfirmDialog(
                    id="confirm-psor",
                    message="All changes will be lost! Are you sure you want to load demo?",
                ),
                dcc.ConfirmDialog(
                    id="confirm-project-title",
                    message="Project title saved successfully!",
                ),
                dcc.ConfirmDialog(
                    id="error-project-title",
                    message="Invalid project title. Please enter a valid title (3-200 characters, no special characters).",
                ),
                dcc.ConfirmDialog(
                    id="confirm-protocol-link",
                    message="Protocol link saved successfully!",
                ),
                dcc.ConfirmDialog(
                    id="error-protocol-link",
                    message="Invalid URL. Please enter a valid protocol link (e.g., https://example.com/protocol).",
                ),
                saveload_modal,  # saveload_modal_button.py
            ],
            style={
                "display": "flex",
                "gap": "15px",
                "justifyContent": "center",
                "alignItems": "center",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            "Project title:",
                            id="project-title-label",
                            className="selcect_title",
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="project-title",
                                    className="upload_radio",
                                    style={"width": "500px"},
                                    placeholder="Enter your project title",
                                ),
                                dbc.Button(
                                    "OK",
                                    n_clicks=0,
                                    id="project_title_button",
                                    disabled=True,
                                    style={
                                        "color": "white",
                                        "backgroundColor": "orange",
                                        "display": "inline-block",
                                        "justifySelf": "center",
                                        "border": "unset",
                                        "padding": "4px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "justifySelf": "center",
                            },
                        ),
                    ],
                    style={
                        "display": "grid",
                        "backgroundColor": "beige",
                        "width": "600px",
                        "justifyContent": "center",
                        "padding": "15px 20px 20px 20px",
                        "alignItems": "center",
                    },
                ),
                dbc.Col(
                    html.Div(
                        html.Span(
                            "*Enter a descriptive title for your network meta-analysis project.",
                            className="upload_instuspan",
                        )
                    ),
                    className="upload_instrucol",
                ),
            ],
            id="project-title-input",
            className="upload_row",
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            "Protocol link:",
                            id="protocol-link-label",
                            className="selcect_title",
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id="protocol-link",
                                    className="upload_radio",
                                    style={"width": "500px"},
                                    placeholder="Enter protocol URL or DOI",
                                ),
                                dbc.Button(
                                    "OK",
                                    n_clicks=0,
                                    id="protocol_link_button",
                                    disabled=True,
                                    style={
                                        "color": "white",
                                        "backgroundColor": "orange",
                                        "display": "inline-block",
                                        "justifySelf": "center",
                                        "border": "unset",
                                        "padding": "4px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "justifySelf": "center",
                            },
                        ),
                    ],
                    style={
                        "display": "grid",
                        "backgroundColor": "beige",
                        "width": "600px",
                        "justifyContent": "center",
                        "padding": "15px 20px 20px 20px",
                        "alignItems": "center",
                    },
                ),
                dbc.Col(
                    html.Div(
                        html.Span(
                            "*NMAStudio requires users to provide protocol links or DOI.",
                            className="upload_instuspan",
                        )
                    ),
                    className="upload_instrucol",
                ),
            ],
            id="protocol-link-input",
            className="upload_row",
        ),
        html.Br(),
        dbc.Row(
            html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
            style={"display": "none", "justifyContent": "center"},
            id="arrow_protocol",
        ),
        html.Br(),
        dbc.Row(
            id="uploader",
            style={
                "display": "grid",
                "justifyContent": "center",
                "width": "1000px",
                "justifySelf": "center",
                "margin": "0 auto",
            },
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    dcc.Upload(
                                        [
                                            "Drag and Drop or ",
                                            html.A(
                                                "Select a File",
                                                style={"color": "#1EAEDB"},
                                            ),
                                        ],
                                        id="datatable-upload2",
                                        multiple=False,
                                        className="control-upload",
                                        style={
                                            "width": "100%",
                                            "height": "60px",
                                            "lineHeight": "60px",
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "5px",
                                            "textAlign": "center",
                                            "margin": "10px",
                                            "color": "black",
                                        },
                                    ),
                                    style={"display": "inline-block"},
                                ),
                                html.Div(
                                    [
                                        html.P("", style={"paddingLeft": "10px"}),
                                        html.P(
                                            "",
                                            id="uploaded_datafile2",
                                            style={
                                                "color": "violet",
                                                "paddingLeft": "20px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "fontFamily": "italic",
                                        "display": "inline-block",
                                    },
                                ),
                            ],
                            style={"display": "inline-block", "justifySelf": "center"},
                        ),
                        # dbc.Col([html.Br(),html.Ul(id="file-list2", style={'marginLeft': '15px', 'color':'white','opacity':'60%'})],
                        #         style={'display': 'inline-block'}),
                        dbc.Col(
                            html.Div(
                                html.Span(
                                    "* The dataset should be uploaded as the csv format",
                                    className="upload_instuspan",
                                )
                            ),
                            className="upload_instrucol",
                        ),
                    ],
                    className="upload_row",
                    id="upload_original_data",
                ),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step1",
                ),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(file_upload_controls2),
                            dbc.Col(
                                html.Div(
                                    [
                                        html.Span(
                                            "*You can click the link the see the differences between the formats:",
                                            className="upload_instuspan",
                                        ),
                                        dbc.NavLink(
                                            "Link",
                                            active=True,
                                            external_link=True,
                                            href="assets/data format.pdf",
                                            style={"color": "blue"},
                                        ),
                                    ]
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),
                    style={"display": "none", "justifyContent": "center"},
                    id="dropdowns-DIV2",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step_2",
                ),
                html.Br(),
                html.Div(
                    [
                        dbc.Row(
                            [
                                dbc.Col(id="select-box-1"),
                                dbc.Col(
                                    html.Div(
                                        html.Span(
                                            "*studlab: study ID or study name \n*rob: risk of bias should be encoded in your data file as either {1,2,3}, {l,m,h} or {L,M,H}, the arms in the same study should have the same rob value. \n*year: year of publication",
                                            className="upload_instuspan",
                                        )
                                    ),
                                    className="upload_instrucol",
                                ),
                            ],
                            className="upload_row",
                        )
                    ],
                    style={"display": "none", "justifyContent": "center"},
                    id="select-overall",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step_3",
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "Enter the number of outcomes:",
                                    className="selcect_title",
                                ),
                                html.Div(
                                    [
                                        dcc.Input(
                                            id="number-outcomes",
                                            className="upload_radio",
                                            style={"width": "100px"},
                                            type="number",
                                            min=1,
                                        ),
                                        dbc.Button(
                                            "OK",
                                            n_clicks=0,
                                            id="num_outcomes_button",
                                            disabled=True,
                                            style={
                                                "color": "white",
                                                "backgroundColor": "orange",
                                                "display": "inline-block",
                                                "justifySelf": "center",
                                                "border": "unset",
                                                "padding": "4px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "justifyContent": "space-evenly",
                                        "width": "150px",
                                        "justifySelf": "center",
                                    },
                                ),
                            ],
                            style={
                                "display": "grid",
                                "backgroundColor": "beige",
                                "width": "500px",
                                "justifyContent": "center",
                                "height": "100px",
                                "alignItems": "center",
                            },
                        ),
                        dbc.Col(
                            html.Div(
                                html.Span(
                                    "*NMAStudio now supports any number of outcomes.",
                                    className="upload_instuspan",
                                )
                            ),
                            className="upload_instrucol",
                        ),
                    ],
                    id="number-outcomes-input",
                    className="upload_row",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step_4",
                ),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(id="outcomes_primary"),
                            dbc.Col(
                                html.Div(
                                    html.Span(
                                        '*Select two primary outcomes for league table. Select "skip" if not applicable',
                                        className="upload_instuspan",
                                    )
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),
                    style={"display": "none", "justifyContent": "center"},
                    id="select-out-primary",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step_primary",
                ),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(id="outcomes_type"),
                            dbc.Col(
                                html.Div(
                                    html.Span(
                                        "*Select binary or continuous and enter the corresponding name for each outcome",
                                        className="upload_instuspan",
                                    )
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),
                    style={"display": "none", "justifyContent": "center"},
                    id="select-out-type",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step_5",
                ),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(id="variable_selection"),
                            dbc.Col(
                                html.Div(
                                    html.Span(
                                        '* In this box, each variable should refer to a unique coulum in your dataset. For example, if you have two outcomes and the number of participants are the same in each study for two outcomes. The number of participants refer to column "N" in your dataset. Do not select "N" for both outcome 1 and 2. In this case, you need to create another column "N2" for outcome 2. ',
                                        className="upload_instuspan",
                                    )
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),
                    style={"display": "none", "justifyContent": "center"},
                    id="select_variables",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step3",
                ),
                html.Br(),
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(id="select_effect_modifier"),
                            dbc.Col(
                                html.Div(
                                    html.Span(
                                        '*Select potential effect modifiers you want to check. If you do not want to check, please tick "skip".\n*When you upload long format dataset, the arms in the same study should have the same effect modifier value',
                                        className="upload_instuspan",
                                    )
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),
                    style={"display": "none", "justifyContent": "center"},
                    id="effect_modifier_select",
                ),
                html.Br(),
                dbc.Row(
                    html.Img(src="/assets/icons/arrow.png", style={"width": "60px"}),
                    style={"display": "none", "justifyContent": "center"},
                    id="arrow_step4",
                ),
                html.Br(),
                dbc.Row(
                    dbc.Button(
                        "Run Analysis",
                        id="upload_modal_data2",
                        className="",
                        disabled=True,
                        style={
                            "color": "white",
                            "backgroundColor": "orange",
                            "display": "inline-block",
                            "justifySelf": "center",
                            "border": "unset",
                            "padding": "4px",
                        },
                    ),
                    style={"display": "none"},
                    id="run_button",
                ),
                html.Br(),
                html.Br(),
            ],
        ),
        # modal_checks moved to app.py global layout (dbc.Modal doesn't render in page layouts)
        # Error modals for R analysis failures
        R_errors_data,
        R_errors_nma,
        R_errors_pair,
        R_errors_league,
        R_errors_funnel,
        html.Div(id="dummy-console-logger", style={"display": "none"}),
    ],
)


# Monitor function disabled in debug mode - comment out to enable
# @callback(
#     [Output("monitor_store", "children")],
#     [
#         Input("raw_data_STORAGE", "modified_timestamp"),
#     ],
#     [STORAGESTATE],
#     prevent_initial_call=True,
# )
# def project_store(_tsm, tstore):
#     if tstore:
#         mout = [
#             tstore[__get_state_of("results_ready")],
#             tstore[__get_state_of("raw_data_STORAGE")],
#         ]
#         if mout:
#             raw_table = mout
#         else:
#             raw_table = "empty"
#         res = [
#             html.Pre(
#                 f"OUR BEAUTIFUL STATE\n{json.dumps(raw_table, indent=2)}",
#                 style={"fontSize": "10px"},
#             )
#         ]
#     else:
#         res = ["nothing to see here"]
#     return res


# #Project reset
@callback(
    Output("confirm-reset", "displayed"),
    Input("reset_project", "n_clicks"),
    prevent_initial_call=True,
)
def display_confirm(value):
    return True


@callback(
    STORAGEOUTPUT,
    [Input("confirm-reset", "submit_n_clicks")],
    [STORAGESTATE],
    prevent_initial_call=True,
)
def empty_stt(_nclicks, storagium):
    # Guard: only proceed if user actually clicked (not on initial page load)
    if not _nclicks or _nclicks == 0:
        return [dash.no_update] * len(STORAGEOUTPUT)
    res = __load_project(storagium, EMPTY_STORAGE)
    idx = __get_state_of("results_ready_STORAGE")
    print(f"[DEBUG] empty_stt (reset): results_ready at index {idx} = {res[idx]}")
    return res


# Load psoriasis CHECKED
@callback(
    Output("confirm-psor", "displayed"),
    Input("load_psor", "n_clicks"),
    prevent_initial_call=True,
)
def display_confirm_psor(_value):
    return True


@callback(
    STORAGEOUTPUT + [Output("setup_page_location", "pathname")],
    [Input("confirm-psor", "submit_n_clicks")],
    [STORAGESTATE],
    prevent_initial_call=True,
)
def load_psr(_nclicks, storagium):
    # Guard: only proceed if user actually clicked (not on initial page load)
    if not _nclicks or _nclicks == 0:
        return [dash.no_update] * (len(STORAGEOUTPUT) + 1)
    print(f"[DEBUG] load_psr: CALLBACK TRIGGERED with n_clicks={_nclicks}")
    res = __load_project(storagium, PSORIASIS_3OUTCOMES_DATA)
    # Set results_ready to True - it's already included in STORAGEOUTPUT
    # The __load_project function returns all storage values, we need to update results_ready
    idx = __get_state_of("results_ready_STORAGE")
    print(f"[DEBUG] load_psr: Setting results_ready at index {idx} to True")
    print(f"[DEBUG] load_psr: Before = {res[idx]}, After setting to True")
    res[idx] = True
    print(f"[DEBUG] load_psr: res[{idx}] = {res[idx]}")
    # Redirect to results page by setting pathname (with refresh=True, causes page reload)
    print(f"[DEBUG] load_psr: Redirecting to /results")
    return res + ["/results"]


# Auto-redirect to results when project is uploaded (triggered by upload, not by results_ready)
@callback(
    Output("setup_page_location", "pathname", allow_duplicate=True),
    Input("project_upload_trigger", "data"),
    prevent_initial_call=True,
)
def redirect_after_project_upload(upload_trigger):
    """Redirect to results page only when a project is uploaded (not when results_ready changes)"""
    if upload_trigger is not None:
        print(
            f"[DEBUG] redirect_after_project_upload: Upload detected, redirecting to /results"
        )
        return "/results"
    return dash.no_update


### ---------------- PROJECT SETUP --------------- ###
@callback(
    Output("second-selection", "children"),
    [
        Input("dropdown-format", "value"),
        Input("dropdown-outcome1", "value"),
        Input("dropdown-outcome2", "value"),
    ],
    [
        State("datatable-upload2", "contents"),
        State("datatable-upload2", "filename"),
    ],
)
def update_options(
    search_value_format,
    search_value_outcome1,
    search_value_outcome2,
    contents,
    filename,
):
    return __update_options(
        search_value_format,
        search_value_outcome1,
        search_value_outcome2,
        contents,
        filename,
    )


# @app.callback([Output("upload_selection_second", "children"),
# Output("arrow_step2", "style")
# ],
# [Input("radio-format", "value"),
# Input("radio-outcome1", "value"),
# Input("radio-outcome2", "value")],
# [State('datatable-upload2', 'contents'),
# State('datatable-upload2', 'filename')]
# )
# def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
# return __second_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)


@callback(
    [
        Output("outcomes_primary", "children"),
        Output("arrow_step_4", "style"),
        Output("select-out-primary", "style"),
    ],
    [
        Input("number-outcomes", "value"),
        Input("num_outcomes_button", "n_clicks"),
    ],
)
def update_primary_outcomes(number_outcomes, click):
    return __primaryout_selection(number_outcomes, click)


@callback(
    [
        Output("outcomes_type", "children"),
        Output("arrow_step_primary", "style"),
        Output("select-out-type", "style"),
    ],
    [
        Input("number-outcomes", "value"),
        Input({"type": "outcomeprimary", "index": ALL}, "value"),
        Input({"type": "noprimary", "index": ALL}, "value"),
    ],
)
def update_outcomes_type(number_outcomes, primary_out, noprimary):
    return __outcomes_type(number_outcomes, primary_out, noprimary)


@callback(
    [
        Output("variable_selection", "children"),
        Output("arrow_step_5", "style"),
        Output("select_variables", "style"),
    ],
    [
        Input("number-outcomes", "value"),
        Input({"type": "outcometype", "index": ALL}, "value"),
        Input("radio-format", "value"),
    ],
    [State("datatable-upload2", "contents"), State("datatable-upload2", "filename")],
)
def update_variable_selection(
    number_outcomes, outcometype, data_format, contents, filename
):
    return __variable_selection(
        number_outcomes, outcometype, data_format, contents, filename
    )


# check with main
@callback(
    Output({"type": "outcomebutton", "index": ALL}, "disabled"),
    Input("number-outcomes", "value"),
    Input({"type": "effectselectors", "index": ALL}, "value"),
    Input({"type": "directionselectors", "index": ALL}, "value"),
    Input({"type": "variableselectors", "index": ALL}, "value"),
    State({"type": "outcometype", "index": ALL}, "value"),
    State("radio-format", "value"),
)
def next_outcome(
    number_outcomes, effect, direction, variables, outcometype, data_format
):
    if number_outcomes and effect:
        number_outcomes = int(number_outcomes)
        disables = [True] * (number_outcomes)  # Initialize with True for all outcomes

        # Calculate how many variables each outcome needs based on type and format
        var_counts = []
        for i in range(number_outcomes):
            if not outcometype or i >= len(outcometype):
                var_counts.append(2)  # default
                continue

            if data_format == "long":
                if outcometype[i] == "continuous":
                    var_counts.append(3)  # y, sd, n
                else:  # binary
                    var_counts.append(2)  # events, participants
            elif data_format == "contrast":
                if outcometype[i] == "continuous":
                    var_counts.append(6)  # y1, sd1, y2, sd2, n1, n2
                else:  # binary
                    var_counts.append(4)  # r1, n1, r2, n2
            elif data_format == "iv":
                var_counts.append(4)  # TE, seTE, n1, n2
            else:
                var_counts.append(2)  # default

        # Check if all variables for each outcome are filled
        var_idx = 0
        for i in range(number_outcomes):
            num_vars = var_counts[i]
            # Get all variable values for this outcome
            outcome_vars = (
                variables[var_idx : var_idx + num_vars]
                if var_idx + num_vars <= len(variables)
                else []
            )
            # Check if all are filled
            all_filled = len(outcome_vars) == num_vars and all(
                v is not None and v != "" for v in outcome_vars
            )

            if effect[i] and direction[i] and all_filled:
                disables[i] = (
                    False  # Enable the outcome button if all conditions are met
                )

            var_idx += num_vars

        disables[number_outcomes - 1] = True  # Keep last button disabled
        return disables
    return [True] * int(number_outcomes) if number_outcomes else []


@callback(
    Output({"type": "displayvariable", "index": ALL}, "style"),
    Input("number-outcomes", "value"),
    Input({"type": "outcomebutton", "index": ALL}, "n_clicks"),
    Input({"type": "outcomeprevious", "index": ALL}, "n_clicks"),
    State({"type": "displayvariable", "index": ALL}, "style"),
)
def next_outcome_display(number_outcomes, click, click_previous, style):
    ctx = dash.callback_context
    changed_id = [p["prop_id"] for p in ctx.triggered][0] if ctx.triggered else ""

    if number_outcomes:
        number_outcomes = int(number_outcomes)
        if number_outcomes > 0:
            style = [
                {"display": "grid" if i == 0 else "none"}
                for i in range(number_outcomes)
            ]
            for i in range(number_outcomes - 1):
                if (
                    click[i] > 0
                    and "outcomebutton" in changed_id
                    and f"{i}" in changed_id
                ):
                    style = [{"display": "none"} for _ in range(number_outcomes)]
                    style[i] = {"display": "none"}
                    style[i + 1] = {"display": "grid"}

            for i in range(1, number_outcomes):
                if (
                    click_previous[i] > 0
                    and "outcomeprevious" in changed_id
                    and f"{i}" in changed_id
                ):
                    style = [{"display": "none"} for _ in range(number_outcomes)]
                    style[i - 1] = {"display": "grid"}
                    style[i] = {"display": "none"}
            return style

    return style

    return style


@callback(
    [
        Output("select-box-1", "children"),
        Output("arrow_step_2", "style"),
        Output("select-overall", "style"),
    ],
    [Input("radio-format", "value")],
    [State("datatable-upload2", "contents"), State("datatable-upload2", "filename")],
)
def update_selectbox1_options(search_value_format, contents, filename):
    return __selectbox1_options(search_value_format, contents, filename)


@callback(
    [Output("number-outcomes-input", "style"), Output("arrow_step_3", "style")],
    Input("radio-format", "value"),
    Input({"type": "dataselectors_1", "index": ALL}, "value"),
)
def modal_ENABLE_UPLOAD_button(format, dataselectors):
    # Exclude rob and year indices (they are optional)
    if format == "long":
        idx = {2, 3}  # rob and year for long format
    else:
        idx = {3, 4}  # rob and year for contrast/iv format

    show_style = {"display": "grid", "justifyContent": "center"}
    hide_style = {"display": "none", "justifyContent": "center"}

    # Filter out optional fields (rob and year)
    filtered_values = [val for i, val in enumerate(dataselectors) if i not in idx]

    if len(filtered_values):
        if all(filtered_values):
            return show_style, show_style
        else:
            return hide_style, hide_style
    else:
        return hide_style, hide_style


@callback(Output("num_outcomes_button", "disabled"), Input("number-outcomes", "value"))
def enable_num_outcomes_button(value):
    if value:
        return False
    return True


@callback(
    Output("select_effect_modifier", "children"),
    Input("radio-format", "value"),
    State("datatable-upload2", "contents"),
    State("datatable-upload2", "filename"),
)
def update_effect_modifier_options(search_value_format, contents, filename):
    return __effect_modifier_options(search_value_format, contents, filename)


@callback(
    Output("select_effect_modifier", "style"),
    Output("arrow_step3", "style"),
    Output("effect_modifier_select", "style"),
    Input({"type": "variableselectors", "index": ALL}, "value"),
)
def show_effect_modifier_section(variableselectors):
    if len(variableselectors):
        if all(variableselectors):
            return (
                {"display": "grid", "justifyContent": "center"},
                {"display": "grid", "justifyContent": "center"},
                {"display": "grid", "justifyContent": "center"},
            )
        else:
            return (
                {"display": "none"},
                {"display": "none", "justifyContent": "center"},
                {"display": "none", "justifyContent": "center"},
            )
    else:
        return (
            {"display": "none"},
            {"display": "none", "justifyContent": "center"},
            {"display": "none", "justifyContent": "center"},
        )


@callback(
    Output("upload_modal_data2", "disabled"),
    Output("run_button", "style"),
    Output("arrow_step4", "style"),
    Input("effect_modifier_checkbox", "value"),
    Input("no_effect_modifier", "value"),
)
def enable_run_analysis_button(effect_mod, no_effect_mod):
    if effect_mod or no_effect_mod:
        return (
            False,
            {"display": "grid", "justifyContent": "center"},
            {"display": "grid", "justifyContent": "center"},
        )
    else:
        return (
            True,
            {"display": "none", "justifyContent": "center"},
            {"display": "none", "justifyContent": "center"},
        )


# ######## second instruction icon showup############
# @app.callback(Output("queryicon-studlb","style"),
# Output("queryicon-year","style"),
# Output("queryicon-rob","style"),
# Input("dropdown-format", "value"),
# Input("dropdown-outcome1", "value"))

# def is_secondicon_show(search_value_format,search_value_outcome1):
# show_studlb={'display': 'block'}
# donotshow_studlb={'display': 'none'}
# if search_value_format and search_value_outcome1 is not None:
# return show_studlb, show_studlb, show_studlb
# else:
# return donotshow_studlb, donotshow_studlb, donotshow_studlb


# #update filename DIV and Store filename in Session
# # @app.callback([Output("queryicon-outcome2", "style"),
# #                Output("dropdowns-DIV", "style"),
# #                Output("uploaded_datafile", "children"),
# #                Output("datatable-filename-upload","data"),
# #                ],
# #                [Input('datatable-upload', 'filename')]
# #               )
# # def is_data_file_uploaded(filename):
# #     show_outcome2_icon = {'display': 'block'}
# #     show_DIV_style = {'display': 'inline-block', 'marginBottom': '0px'}
# #     donot_show_DIV_style = {'display': 'none', 'marginBottom': '0px'}
# #     donotshow_outcome2_icon = {'display': 'none'}
# #     if filename:
# #         return show_outcome2_icon, show_DIV_style, filename or '', filename
# #     else:
# #         return donotshow_outcome2_icon, donot_show_DIV_style, '', filename

# @app.callback(
# Output('protocol_link_button', 'disabled'),
# Input('protocol-link', 'value')
# )
# def enable(value):
# if value:
# return False
# return True


# @app.callback([
# Output("upload_original_data", "style"),
# Output("arrow_protocol", "style")
# ],
# [Input('protocol-link', 'value'),
# Input("protocol_link_button", "n_clicks")
# ]
# )
# def is_data_file_uploaded(value,click):
# show_DIV_style = {'display': 'grid', 'justifyContent': 'center'}
# donot_show_DIV_style = {'display': 'none', 'justifyContent': 'center'}
# arrow1_show={'display':'grid', 'justifyContent': 'center'}
# arrow1_notshow={'display':'none', 'justifyContent': 'center'}

# if value and click:
# return  show_DIV_style,  arrow1_show
# else:
# return  donot_show_DIV_style, arrow1_notshow


@callback(
    [
        Output("dropdowns-DIV2", "style"),
        Output("uploaded_datafile2", "children"),
        Output("arrow_step1", "style"),
    ],
    [Input("datatable-upload2", "filename")],
)
def is_data_file_uploaded(filename):
    show_DIV_style = {"display": "grid", "justifyContent": "center"}
    donot_show_DIV_style = {"display": "none", "justifyContent": "center"}
    arrow1_show = {"display": "grid", "justifyContent": "center"}
    arrow1_notshow = {"display": "none", "justifyContent": "center"}

    if filename:
        return show_DIV_style, filename or "", arrow1_show
    else:
        return donot_show_DIV_style, "", arrow1_notshow


# Main callback to handle "Run Analysis" button click - opens modal for checks
@callback(
    [
        Output("modal_data_checks", "is_open"),
        Output("raw_data_STORAGE", "data"),
        Output("net_data_STORAGE", "data"),
        Output("Rconsole-error-data", "children"),
        Output("R-alert-data", "is_open"),
        Output("dropdown-intervention", "options"),
        Output("effect_modifiers_STORAGE", "data"),
        Output("outcome_names_STORAGE", "data"),
        Output("number_outcomes_STORAGE", "data"),
    ],
    [
        Input("upload_modal_data2", "n_clicks"),
    ],
    [
        State("radio-format", "value"),
        State({"type": "dataselectors_1", "index": ALL}, "value"),
        State("number-outcomes", "value"),
        State({"type": "outcometype", "index": ALL}, "value"),
        State({"type": "effectselectors", "index": ALL}, "value"),
        State({"type": "directionselectors", "index": ALL}, "value"),
        State({"type": "variableselectors", "index": ALL}, "value"),
        State({"type": "nameoutcomes", "index": ALL}, "value"),
        State("modal_data_checks", "is_open"),
        State("datatable-upload2", "contents"),
        State("datatable-upload2", "filename"),
        State("net_data_STORAGE", "data"),
        State("raw_data_STORAGE", "data"),
        State("effect_modifier_checkbox", "value"),
        State("no_effect_modifier", "value"),
    ],
    prevent_initial_call=True,
)
def data_trans(
    upload,
    search_value_format,
    overall_variables,
    number_outcomes,
    outcome_type,
    effectselectors,
    directionselectors,
    variableselectors,
    outcome_names_input,
    modal_data_checks_is_open,
    contents,
    filename,
    net_data_STORAGE,
    raw_data_STORAGE,
    effect_modifier_checkbox,
    no_effect_modifier,
):
    # Guard: Check if this is a genuine button click (not from persisted session state)
    if not upload or upload == 0:
        return [dash.no_update] * 9

    # Guard: Check if file has been uploaded
    if contents is None:
        return [dash.no_update] * 9

    try:
        print(f"[DEBUG data_trans] Called!")
        print(f"  upload (n_clicks): {upload}")
        print(f"  modal_data_checks_is_open (current): {modal_data_checks_is_open}")
        print(f"  filename: {filename}")
        print(f"  number_outcomes: {number_outcomes}")
        print(f"  search_value_format: {search_value_format}")
        print(
            f"  variableselectors count: {len(variableselectors) if variableselectors else 0}"
        )
        print(f"  effect_modifier_checkbox: {effect_modifier_checkbox}")
        print(f"  no_effect_modifier: {no_effect_modifier}")
    except Exception as e:
        print(f"[ERROR data_trans] Exception in debug logging: {e}")

    try:
        # Store effect modifiers as a list (or empty list if Skip, or None if not selected)
        if effect_modifier_checkbox and len(effect_modifier_checkbox) > 0:
            effect_modifiers_data = effect_modifier_checkbox
            print(f"  Storing effect modifiers: {effect_modifier_checkbox}")
        elif no_effect_modifier and len(no_effect_modifier) > 0:
            # User selected "Skip" - store empty list
            effect_modifiers_data = []
            print(f"  No effect modifiers selected (Skip was checked)")
        else:
            # No selection made yet
            effect_modifiers_data = None
            print(f"  Effect modifiers not yet selected")

        # __data_trans returns 8 values: (modal_open, raw_data, net_data, filename_exists, error, alert_open, dropdown_options, results_ready)
        # We need: (modal_open, raw_data, net_data, error, alert_open, dropdown_options) = 6 values
        # So we remove the last 2 values: filename_exists (uploaded_datafile_to_disable_cinema) and results_ready
        result = __data_trans(
            upload,
            None,  # filename2 - not used
            None,  # submit - not used in this callback anymore
            search_value_format,
            overall_variables,
            number_outcomes,
            outcome_type,
            effectselectors,
            directionselectors,
            variableselectors,
            modal_data_checks_is_open,
            contents,
            filename,
            net_data_STORAGE,
            raw_data_STORAGE,
            False,  # results_ready - not set here anymore
        )
        # Prepare outcome names storage
        # outcome_names_input is a list of outcome names from the input fields
        outcome_names_list = []
        number_outcomes_int = 0
        if outcome_names_input and len(outcome_names_input) > 0:
            # Filter out empty names
            outcome_names_list = [name for name in outcome_names_input if name]
            number_outcomes_int = len(outcome_names_list)
            print(
                f"[DEBUG data_trans] Outcome names: {outcome_names_list}, count: {number_outcomes_int}"
            )
        else:
            # If no names provided, use generic names based on number_outcomes
            if number_outcomes:
                try:
                    number_outcomes_int = int(number_outcomes)
                    outcome_names_list = [
                        f"Outcome{i + 1}" for i in range(number_outcomes_int)
                    ]
                    print(
                        f"[DEBUG data_trans] Using generic outcome names: {outcome_names_list}"
                    )
                except:
                    pass

        # Return: modal_open, raw_data, net_data, error, alert_open, dropdown_options, effect_modifiers, outcome_names, number_outcomes
        # (skip filename_exists at index 3 and results_ready at index 7)
        print(f"[DEBUG data_trans] Returning:")
        print(f"  modal_open (result[0]): {result[0]}")
        print(f"  raw_data type: {type(result[1])}")
        print(f"  net_data type: {type(result[2])}")
        print(f"  effect_modifiers_data: {effect_modifiers_data}")
        print(f"  outcome_names_list: {outcome_names_list}")
        print(f"  number_outcomes_int: {number_outcomes_int}")
        return (
            result[0],
            result[1],
            result[2],
            result[4],
            result[5],
            result[6],
            effect_modifiers_data,
            outcome_names_list,
            number_outcomes_int,
        )
    except Exception as e:
        print(f"[ERROR data_trans] EXCEPTION CAUGHT: {e}")
        import traceback

        traceback.print_exc()
        # Return error state
        return (
            False,  # modal not open
            raw_data_STORAGE if raw_data_STORAGE else {},  # keep current raw data
            net_data_STORAGE if net_data_STORAGE else {},  # keep current net data
            str(e),  # error message
            True,  # show alert
            [],  # empty dropdown options
            None,  # no effect modifiers
            [],  # empty outcome names
            0,  # zero outcomes
        )


# Analysis callbacks that chain together sequentially using modified_timestamp
# This matches the pattern from NMAstudio-app-main


# Step 1: Data checks - triggered when modal opens
# Outputs to both global Store (.data for submit button) and modal display (.children)
@callback(
    [
        Output("para-check-data", "data"),
        Output("para-check-data-modal", "children"),
    ],
    Input("modal_data_checks", "is_open"),
    [State("number-outcomes", "value"), State("net_data_STORAGE", "data")],
    prevent_initial_call=True,
)
def modal_submit_checks_DATACHECKS(
    modal_data_checks_is_open, num_outcomes, net_data_STORAGE
):
    # Guard: Only run when modal is open (prevents errors when on results page)
    if not modal_data_checks_is_open:
        return [dash.no_update, dash.no_update]

    result = __modal_submit_checks_DATACHECKS(
        modal_data_checks_is_open, num_outcomes, net_data_STORAGE
    )
    # result[0] = html.P element for display, result[1] = "__Para_Done__" marker
    return [result[1], result[0]]


# Step 2: NMA analysis - triggered when modal opens (runs in parallel with data checks)
# Outputs to both global Store (.data for submit button) and modal display (.children)
@callback(
    [
        Output("R-alert-nma", "is_open"),
        Output("Rconsole-error-nma", "children"),
        Output("para-anls-data", "data"),
        Output("para-anls-data-modal", "children"),
        Output("forest_data_STORAGE", "data"),
    ],
    Input("modal_data_checks", "is_open"),
    [
        State("number-outcomes", "value"),
        State("net_data_STORAGE", "data"),
        State("forest_data_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def modal_submit_checks_NMA_new(
    modal_data_checks_is_open, num_outcome, net_data_STORAGE, forest_data_STORAGE
):
    # Guard: Only run when modal is open (prevents errors when on results page)
    if not modal_data_checks_is_open:
        return [dash.no_update] * 5

    result = __modal_submit_checks_NMA_new(
        modal_data_checks_is_open, num_outcome, net_data_STORAGE, forest_data_STORAGE
    )
    # result is (alert_open, error_msg, children, data_marker, forest_data)
    # Output: alert, error_msg, marker to Store, children to modal, forest_data
    return [result[0], result[1], result[3], result[2], result[4]]


# Step 3: Pairwise analysis - triggered when NMA completes (forest_data_STORAGE updates)
# Outputs to both global Store (.data for submit button) and modal display (.children)
@callback(
    [
        Output("R-alert-pair", "is_open"),
        Output("Rconsole-error-pw", "children"),
        Output("para-pairwise-data", "data"),
        Output("para-pairwise-data-modal", "children"),
        Output("forest_data_prws_STORAGE", "data"),
    ],
    Input("forest_data_STORAGE", "modified_timestamp"),
    [
        State("number_outcomes_STORAGE", "data"),
        State("modal_data_checks", "is_open"),
        State("net_data_STORAGE", "data"),
        State("forest_data_prws_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def modal_submit_checks_PAIRWISE(
    nma_data_ts,
    num_outcome_storage,
    modal_data_checks_is_open,
    net_data_STORAGE,
    forest_data_prws_STORAGE,
):
    # Use stored number of outcomes (fallback to 1)
    num_outcome = num_outcome_storage if num_outcome_storage else 1
    # Guard: Only run when modal is open (prevents errors when on results page)
    if not modal_data_checks_is_open:
        return [dash.no_update] * 5

    result = __modal_submit_checks_PAIRWISE_new(
        nma_data_ts,
        num_outcome,
        modal_data_checks_is_open,
        net_data_STORAGE,
        forest_data_prws_STORAGE,
    )
    # result is (alert_open, error_msg, children, data_marker, forest_prws_data)
    # Output: alert, error_msg, marker to Store, children to modal, forest_prws_data
    return [result[0], result[1], result[3], result[2], result[4]]


# Step 4: League table - triggered when Pairwise completes (forest_data_prws_STORAGE updates)
# Outputs to both global Store (.data for submit button) and modal display (.children)
@callback(
    [
        Output("R-alert-league", "is_open"),
        Output("Rconsole-error-league", "children"),
        Output("para-LT-data", "data"),
        Output("para-LT-data-modal", "children"),
        Output("league_table_data_STORAGE", "data"),
        Output("ranking_data_STORAGE", "data"),
        Output("consistency_data_STORAGE", "data"),
        Output("net_split_data_STORAGE", "data"),
        Output("net_split_ALL_data_STORAGE", "data"),
    ],
    Input("forest_data_prws_STORAGE", "modified_timestamp"),
    [
        State("number_outcomes_STORAGE", "data"),
        State("modal_data_checks", "is_open"),
        State("net_data_STORAGE", "data"),
        State("league_table_data_STORAGE", "data"),
        State("ranking_data_STORAGE", "data"),
        State("consistency_data_STORAGE", "data"),
        State("net_split_data_STORAGE", "data"),
        State("net_split_ALL_data_STORAGE", "data"),
        State({"type": "outcomeprimary", "index": ALL}, "value"),
    ],
    prevent_initial_call=True,
)
def modal_submit_checks_LT(
    pw_data_ts,
    num_outcome_storage,
    modal_data_checks_is_open,
    net_data_STORAGE,
    league_table_data,
    ranking_data,
    consistency_data,
    net_split_data,
    netsplit_all,
    outcome_index,
):
    # Use stored number of outcomes (fallback to 1)
    num_outcome = num_outcome_storage if num_outcome_storage else 1
    # Guard: Only run when modal is open (prevents errors when on results page)
    if not modal_data_checks_is_open:
        return [dash.no_update] * 9

    result = __modal_submit_checks_LT_new(
        pw_data_ts,
        num_outcome,
        modal_data_checks_is_open,
        net_data_STORAGE,
        league_table_data,
        ranking_data,
        consistency_data,
        net_split_data,
        netsplit_all,
        outcome_index,
    )
    # result is (alert, error, children, data_marker, league, ranking, consistency, netsplit, netsplit_all)
    # Output: alert, error, marker to Store, children to modal, league, ranking, consistency, netsplit, netsplit_all
    return [
        result[0],
        result[1],
        result[3],
        result[2],
        result[4],
        result[5],
        result[6],
        result[7],
        result[8],
    ]


# Step 5: Funnel plot - triggered when League table completes (league_table_data_STORAGE updates)
# Outputs to both global Store (.data for submit button) and modal display (.children)
@callback(
    [
        Output("R-alert-funnel", "is_open"),
        Output("Rconsole-error-funnel", "children"),
        Output("para-FA-data", "data"),
        Output("para-FA-data-modal", "children"),
        Output("funnel_data_STORAGE", "data"),
    ],
    Input("league_table_data_STORAGE", "modified_timestamp"),
    [
        State("number_outcomes_STORAGE", "data"),
        State("modal_data_checks", "is_open"),
        State("net_data_STORAGE", "data"),
        State("funnel_data_STORAGE", "data"),
    ],
    prevent_initial_call=True,
)
def modal_submit_checks_FUNNEL(
    lt_data_ts,
    num_outcome_storage,
    modal_data_checks_is_open,
    net_data_STORAGE,
    funnel_data,
):
    # Guard: Only run when modal is open (prevents errors when on results page)
    if not modal_data_checks_is_open:
        return [dash.no_update] * 5

    # Use stored number of outcomes (fallback to 1)
    num_outcome = num_outcome_storage if num_outcome_storage else 1

    result = __modal_submit_checks_FUNNEL_new(
        lt_data_ts,
        num_outcome,
        modal_data_checks_is_open,
        net_data_STORAGE,
        funnel_data,
    )
    # result is (alert, error, children, data_marker, funnel_data)
    # Output: alert, error, marker to Store, children to modal, funnel_data
    return [result[0], result[1], result[3], result[2], result[4]]


# Collect R errors from all analysis steps and store them
@callback(
    Output("R_errors_STORAGE", "data"),
    [
        Input("R-alert-nma", "is_open"),
        Input("R-alert-pair", "is_open"),
        Input("R-alert-league", "is_open"),
        Input("R-alert-funnel", "is_open"),
    ],
    [
        State("Rconsole-error-nma", "children"),
        State("Rconsole-error-pw", "children"),
        State("Rconsole-error-league", "children"),
        State("Rconsole-error-funnel", "children"),
    ],
)
def collect_r_errors(
    nma_alert,
    pw_alert,
    lt_alert,
    funnel_alert,
    nma_error,
    pw_error,
    lt_error,
    funnel_error,
):
    """Collect all R errors from analysis steps for display in results page"""
    return {
        "nma": str(nma_error) if nma_alert else "",
        "pairwise": str(pw_error) if pw_alert else "",
        "league": str(lt_error) if lt_alert else "",
        "funnel": str(funnel_error) if funnel_alert else "",
    }


@callback(
    Output("submit_modal_data", "disabled"),
    [
        Input(id, "data")
        for id in [
            "para-check-data",
            "para-anls-data",
            "para-pairwise-data",
            "para-LT-data",
            "para-FA-data",
        ]
    ],
)
def modal_submit_button(
    para_check_data_DATA,
    para_anls_data_DATA,
    para_prw_data_DATA,
    para_LT_data_DATA,
    para_FA_data_DATA,
):
    """Enable Submit button once all analysis steps complete"""
    return not (
        para_check_data_DATA
        == para_anls_data_DATA
        == para_prw_data_DATA
        == para_LT_data_DATA
        == para_FA_data_DATA
        == "__Para_Done__"
    )


# Callback to set results_ready when user clicks Submit
@callback(
    [
        Output("results_ready_STORAGE", "data"),
        Output("setup_page_location", "pathname", allow_duplicate=True),
        Output("modal_data_checks", "is_open", allow_duplicate=True),
    ],
    Input("submit_modal_data", "n_clicks"),
    prevent_initial_call=True,
)
def finalize_analysis(n_clicks):
    """Set results_ready flag and redirect when user clicks Submit"""
    if n_clicks and n_clicks > 0:
        return True, "/results", False  # Set results ready, redirect, close modal
    # If prevent_initial_call didn't work, don't change anything
    return dash.no_update, dash.no_update, dash.no_update


# Hide uploader when results are ready
@callback(
    Output("uploader", "style"),
    [
        Input("results_ready_STORAGE", "data"),
        Input("setup_page_location", "pathname"),  # Also trigger on page navigation
    ],
    prevent_initial_call=False,  # Must run on initial load to check if results are already ready
)
def hide_uploader_when_results_ready(results_ready_STORAGE, pathname):
    """Hide the uploader section when results are ready"""
    # Base style for the uploader element
    base_style = {
        "display": "grid",
        "justifyContent": "center",
        "width": "1000px",
        "justifySelf": "center",
        "margin": "0 auto",
    }
    if results_ready_STORAGE:
        return {"display": "none"}  # Hide completely
    return base_style  # Show with full styling


# Populate project title input and label from STORAGE on page load
@callback(
    [
        Output("project-title", "value"),
        Output("project-title-label", "children"),
    ],
    Input("project_title_STORAGE", "modified_timestamp"),
    State("project_title_STORAGE", "data"),
    prevent_initial_call=False,
)
def populate_project_title_input(_ts, stored_title):
    """Populate project title input and update label from STORAGE if value exists"""
    if stored_title and isinstance(stored_title, str) and stored_title.strip():
        title = stored_title.strip()
        # Truncate label if too long
        display_title = title if len(title) <= 50 else title[:47] + "..."
        return title, f"Project title: {display_title}"
    return "", "Project title:"


# Populate protocol link input and label from STORAGE on page load
@callback(
    [
        Output("protocol-link", "value"),
        Output("protocol-link-label", "children"),
    ],
    Input("protocol_link_STORAGE", "modified_timestamp"),
    State("protocol_link_STORAGE", "data"),
    prevent_initial_call=False,
)
def populate_protocol_link_input(_ts, stored_link):
    """Populate protocol link input and update label from STORAGE if value exists"""
    if stored_link and isinstance(stored_link, str) and stored_link.strip():
        link = stored_link.strip()
        # Truncate label if too long
        display_link = link if len(link) <= 40 else link[:37] + "..."
        return link, f"Protocol link: {display_link}"
    return "", "Protocol link:"


# Enable project title button when input has value
@callback(
    Output("project_title_button", "disabled"),
    Input("project-title", "value"),
)
def enable_project_title_button(value):
    """Enable project title button when input has value"""
    return not bool(value)


# Sanitize and validate project title
def __sanitize_project_title(value):
    """
    Sanitize and validate project title.
    Returns (sanitized_value, is_valid, error_message)
    """
    if not value:
        return None, False, "Title cannot be empty"

    # Strip whitespace
    sanitized = value.strip()

    # Check length (3-200 characters)
    if len(sanitized) < 3:
        return None, False, "Title must be at least 3 characters"
    if len(sanitized) > 200:
        return None, False, "Title must be less than 200 characters"

    # Remove potentially dangerous characters (HTML/script injection)
    # Allow letters, numbers, spaces, and common punctuation
    sanitized = re.sub(r"[<>{}[\]\\]", "", sanitized)

    # Collapse multiple spaces
    sanitized = re.sub(r"\s+", " ", sanitized)

    return sanitized, True, None


# Save project title to STORAGE when OK button is clicked
@callback(
    [
        Output("project_title_STORAGE", "data"),
        Output("confirm-project-title", "displayed"),
        Output("error-project-title", "displayed"),
    ],
    Input("project_title_button", "n_clicks"),
    State("project-title", "value"),
    prevent_initial_call=True,
)
def save_project_title(n_clicks, value):
    """Save project title to STORAGE when OK button is clicked, with validation"""
    if not n_clicks:
        return dash.no_update, False, False

    sanitized, is_valid, error = __sanitize_project_title(value)

    if is_valid:
        return sanitized, True, False  # Save and show success
    else:
        return dash.no_update, False, True  # Show error dialog


# Enable protocol link button when input has value
@callback(
    Output("protocol_link_button", "disabled"),
    Input("protocol-link", "value"),
)
def enable_protocol_link_button(value):
    """Enable protocol link button when input has value"""
    return not bool(value)


# Validate and sanitize protocol link URL
def __validate_protocol_link(value):
    """
    Validate and sanitize protocol link URL.
    Accepts: http/https URLs, DOI formats (doi:10.xxx or 10.xxx/yyy)
    Returns (sanitized_url, is_valid, error_message)
    """
    if not value:
        return None, False, "URL cannot be empty"

    # Strip whitespace
    url = value.strip()

    # Basic length check
    if len(url) < 5:
        return None, False, "URL/DOI is too short"
    if len(url) > 2000:
        return None, False, "URL/DOI is too long"

    # Check for DOI format (doi:10.xxxx/yyyy or just 10.xxxx/yyyy)
    # DOI pattern: 10.prefix/suffix where prefix is 4+ digits
    doi_pattern = r"^(doi:)?(10\.\d{4,}(?:\.\d+)*/\S+)$"
    doi_match = re.match(doi_pattern, url, re.IGNORECASE)
    if doi_match:
        # Convert DOI to https://doi.org/ URL
        doi_id = doi_match.group(2)
        url = f"https://doi.org/{doi_id}"
        return url, True, None

    # Parse URL
    try:
        parsed = urlparse(url)

        # If no scheme, auto-prefix https://
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)
        # If scheme exists but is not http/https, reject
        elif parsed.scheme not in ("http", "https"):
            return None, False, "URL must use http or https (or DOI format)"

        # Check netloc (domain)
        if not parsed.netloc:
            return None, False, "Invalid URL format"

        # Basic domain validation
        domain_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}(:\d+)?$"
        if not re.match(domain_pattern, parsed.netloc):
            return None, False, "Invalid domain in URL"

        return url, True, None

    except Exception:
        return None, False, "Invalid URL format"


# Save protocol link to STORAGE when OK button is clicked
@callback(
    [
        Output("protocol_link_STORAGE", "data"),
        Output("confirm-protocol-link", "displayed"),
        Output("error-protocol-link", "displayed"),
    ],
    Input("protocol_link_button", "n_clicks"),
    State("protocol-link", "value"),
    prevent_initial_call=True,
)
def save_protocol_link(n_clicks, value):
    """Save protocol link to STORAGE when OK button is clicked, with URL validation"""
    if not n_clicks:
        return dash.no_update, False, False

    sanitized_url, is_valid, error = __validate_protocol_link(value)

    if is_valid:
        return sanitized_url, True, False  # Save and show success
    else:
        return dash.no_update, False, True  # Show error dialog


# ---------- clientside console logger for _STORAGE stores only ----------
# Only enable in debug mode - check environment variable directly
# This avoids circular import issues with app.py
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "yes")


# Debug function to log all _STORAGE items in localStorage
if DEBUG_MODE:
    from dash import clientside_callback, ClientsideFunction

    # Get all storage IDs from STORAGE list
    storage_ids = [store.id for store in STORAGE if hasattr(store, "id")]

    # Create clientside callback to log localStorage changes
    clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="logStorageChanges"),
        Output("dummy-console-logger", "children"),
        [Input(store_id, "modified_timestamp") for store_id in storage_ids],
        [State(store_id, "data") for store_id in storage_ids],
        prevent_initial_call=False,
    )

    # The actual JavaScript function will be in assets/clientside.js
    # It will console.log all _STORAGE items whenever any of them change
