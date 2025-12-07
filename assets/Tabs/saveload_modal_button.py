import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback
from dash import html, dcc
import json
import base64
from assets.storage import (
    STORAGESTATE,
    STORAGEOUTPUT,
    __load_project,
    __storage_to_dict,
)

saveload_modal = html.Div(
    [
        # Hidden store to trigger redirect after project upload
        dcc.Store(id="project_upload_trigger", data=None),
        dbc.Button(
            "Save/Load Project",
            id="open_saveload",
            n_clicks=0,
            style={
                "backgroundColor": "#00ab9c",
                "height": "40px",
            },
        ),
        dbc.Modal(
            dcc.Tabs(
                id="all-tabs-saveload",
                persistence=True,
                children=[
                    dcc.Tab(
                        style={
                            "color": "grey",
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                        },
                        selected_style={
                            "color": "grey",
                            "display": "flex",
                            "justifyContent": "center",
                            "backgroundColor": "#738788",
                            "alignItems": "center",
                        },
                        label="Save Project",
                        children=html.Div(
                            className="control-tab",
                            children=[
                                dbc.ModalBody(
                                    "You can save your project on your computer and\
                               load it later for further use on the Load\
                               Project\
                               tab"
                                ),
                                dbc.ModalBody("Please choose name for project file"),
                                html.Div(
                                    [
                                        html.H4(
                                            "Project Filename:",
                                            style={
                                                "display": "grid",
                                                "alignItems": "center",
                                                "backgroundColor": "beige",
                                                "width": "500px",
                                                "justifyContent": "center",
                                                "height": "100px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="input-projectname",
                                            type="text",
                                            placeholder="",
                                            style={
                                                "marginLeft": "2%",
                                                "display": "inline-block",
                                                "width": "20%",
                                            },
                                        ),
                                        html.Div(
                                            id="output_username",
                                            style={"marginLeft": "1%", "width": "45%"},
                                        ),
                                    ],
                                    style={
                                        "fontSize": "20px",
                                        "color": "#587485",
                                        "paddingLeft": "3%",
                                        "paddingRight": "3%",
                                        "fontFamily": "sans-serif",
                                        "fontWeight": "530",
                                    },
                                ),
                                dbc.ModalBody(""),
                                html.Br(),
                                html.Button("Save Project", id="btn_json"),
                                dcc.Download(id="download-project-json"),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Close",
                                        id="close_saveload",
                                        className="ms-auto",
                                        n_clicks=0,
                                    )
                                ),
                            ],
                            style={
                                "overflowX": "auto",
                                "overflowY": "auto",
                                "height": "99%",
                                "fontFamily": "sans-serif",
                                "fontSize": "20px",
                                "color": "black",
                            },
                        ),
                    ),
                    dcc.Tab(
                        style={
                            "color": "grey",
                            "display": "flex",
                            "justifyContent": "center",
                            "alignItems": "center",
                        },
                        selected_style={
                            "color": "grey",
                            "display": "flex",
                            "justifyContent": "center",
                            "backgroundColor": "#738788",
                            "alignItems": "center",
                        },
                        label="Load Project",
                        children=html.Div(
                            className="control-tab",
                            children=[
                                dbc.ModalBody(
                                    "You can upload a previously saved project. Project filenames use the .nmastudio extension",
                                    style={
                                        "fontSize": "20px",
                                        "marginLeft": "1%",
                                        "color": "black",
                                    },
                                ),
                                html.Div(
                                    [
                                        dcc.Upload(
                                            id="upload-json",
                                            children=html.Button(
                                                "Select a .nmastudio File",
                                                className="btn btn-primary",
                                                style={
                                                    "backgroundColor": "#00ab9c",
                                                    "border": "unset",
                                                    "fontSize": "18px",
                                                    "padding": "10px 30px",
                                                    "color": "white",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                            multiple=False,
                                        ),
                                    ],
                                    style={
                                        "textAlign": "center",
                                        "margin": "20px",
                                    },
                                ),
                                # html.Div(id="output-data-upload"),
                                dbc.ModalFooter(
                                    dbc.Button(
                                        "Close",
                                        id="close_saveload_2",
                                        className="ms-auto",
                                        n_clicks=0,
                                    )
                                ),
                            ],
                            style={
                                "overflowX": "auto",
                                "overflowY": "auto",
                                "height": "99%",
                            },
                        ),
                    ),
                ],
            ),  # close dcc.Tabs
            id="modal_saveload",
            is_open=False,
            size="xl",
        ),
    ],
    style={"display": "grid", "alignItems": "center"},
)


# modal Save/Load Project
@callback(
    Output("modal_saveload", "is_open"),
    [
        Input("open_saveload", "n_clicks"),
        Input("close_saveload", "n_clicks"),
        Input("close_saveload_2", "n_clicks"),
    ],
    [State("modal_saveload", "is_open")],
)
def toggle_modal(n1, n2, n2_close, is_open):
    if n1 or n2 or n2_close:
        return not is_open
    return is_open


def func(n_clicks, prjname):
    # Build the project dict from current storage
    from assets.storage import STORAGE_KEYS, __storage_to_dict

    # We need to read the current storage state – for now use a dummy empty dict
    # In real usage this would be passed from the callback
    proj_dict = {k: None for k in STORAGE_KEYS}
    return dcc.send_file(
        json.dumps(proj_dict), f"{prjname}.nmastudio", type="application/json"
    )


# Download project
@callback(
    Output("download-project-json", "data"),
    Input("btn_json", "n_clicks"),
    [STORAGESTATE],
    State("input-projectname", "value"),
    prevent_initial_call=True,
)
def export_json(n_clicks, storagium, prjname):
    project_dict = __storage_to_dict(storagium)
    json_string = json.dumps(project_dict, indent=4)
    if prjname:
        flnm = prjname
    else:
        flnma = "project"
    return dict(
        content=json_string, filename=f"{prjname}.nmastudio", type="application/json"
    )


# Define callback to process uploaded file (reactivated for file processing, but output display is disabled)
@callback(
    STORAGEOUTPUT + [Output("project_upload_trigger", "data")],  # Add trigger output
    Input("upload-json", "contents"),
    State("upload-json", "filename"),
    [STORAGESTATE],
    prevent_initial_call=True,
)
def update_output(contents, filename, storagium):
    # Guard: only proceed if there's actual file content (not on initial page load)
    if contents is None:
        from dash import no_update

        return [no_update] * (len(STORAGEOUTPUT) + 1)  # Don't update anything

    # Decode the file contents
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        # Parse JSON data
        prjdata = json.loads(decoded.decode("utf-8"))
        res = __load_project(storagium, prjdata)

        # Set results_ready to True
        from assets.storage import __get_state_of

        idx = __get_state_of("results_ready_STORAGE")
        res[idx] = True

        # Derive number of outcomes and outcome names from loaded data
        # First try to get from the project data directly (if it was saved)
        num_outcomes = prjdata.get("number_outcomes_STORAGE")
        outcome_names = prjdata.get("outcome_names_STORAGE")

        # If not in project, derive from forest_data_STORAGE
        if not num_outcomes:
            forest_data = prjdata.get("forest_data_STORAGE", [])
            if isinstance(forest_data, list):
                num_outcomes = len(forest_data)
            elif isinstance(forest_data, dict):
                # New format: count keys starting with "outcome"
                num_outcomes = len(
                    [k for k in forest_data.keys() if k.startswith("outcome")]
                )
            else:
                num_outcomes = 2  # Default

        # If outcome names not in project, use generic names
        if not outcome_names or not isinstance(outcome_names, list):
            outcome_names = [f"Outcome{i + 1}" for i in range(num_outcomes)]

        # Store the number of outcomes (as integer, not dict)
        idx_outcomes = __get_state_of("number_outcomes_STORAGE")
        res[idx_outcomes] = num_outcomes

        # Store outcome names (as list, not dict)
        idx_names = __get_state_of("outcome_names_STORAGE")
        res[idx_names] = outcome_names

        print(f"[DEBUG] Project loaded with {num_outcomes} outcomes")

        print(f"[DEBUG] Loaded project '{filename}' with {num_outcomes} outcomes")
        # Return storage data and trigger redirect with timestamp
        import time

        return res + [time.time()]  # Timestamp triggers redirect
    except Exception as e:
        print(f"[ERROR] Failed to load project '{filename}': {e}")
        import traceback

        traceback.print_exc()
        # Return storage without changes on error, no trigger
        return storagium + [None]
