import dash
from dash import html, no_update
from dash import dcc
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ALL, callback
from dash_extensions import Download
from dash_extensions.snippets import send_file
from dash.exceptions import PreventUpdate
import pandas as pd
import base64
import io

from tools.functions_project_setup import __upload_cinema

dash.register_page(__name__, path="/cinema", name="CINeMA")


layout = html.Div(id="cinema-page", children=[
                    dcc.Location(id="cinema_location", refresh=True),
                    # CINeMA info header
                    html.Div(
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div([
                                        html.Span(
                                            "Some features in the NMAstudio require users to upload CINeMA reports for each outcome. Please go to the ",
                                            style={"fontSize": "larger", 'color':'red'}
                                        ),
                                        html.A(
                                            'CINeMA',
                                            # html.Img(
                                            #     src="/assets/logos/cinema_logo.png",
                                            #     style={"height": "50px", "verticalAlign": "middle", "margin": "0 5px"}
                                            # ),
                                            href="https://cinema.ispm.unibe.ch/",
                                            target="_blank",
                                            title="Go to CINeMA application",
                                            style={"color": "#3498db"},
                                        ),
                                        html.Span(
                                            " application to obtain the reports.",
                                            style={"fontSize": "larger", 'color':'red'}
                                        ),
                                    ], style={"display": "flex", "alignItems": "center", "justifyContent": "center", "flexWrap": "wrap"}),
                                    width=12
                                ),
                            ],
                            style={"marginBottom": "20px", "padding": "15px", "backgroundColor": "#f8f9fa", "borderRadius": "8px"}
                        ),
                        style={"padding": "10px 20px", 'display': 'grid', 'justifyContent': 'center'}
                    ),
                    html.Div(dbc.Row(
                        [
                            dbc.Col(id="cinema_file"),
                            dbc.Col(
                                html.Div(
                                    html.Span(
                                        "* If you want to include CINeMA certainty in evidence in the league tables and the knowledge translation tool for multiple outcomes, you must upload the CINeMA reporting files for the corresponding outcomes here.",
                                        className="upload_instuspan",
                                    )
                                ),
                                className="upload_instrucol",
                            ),
                        ],
                        className="upload_row",
                    ),style={"display": "none", "justifyContent": "center"},
                    id="cinema-file-upload")])



@callback(
    [
        Output("cinema_file", "children"),
        # Output("arrow_step_cinema", "style"),
        Output("cinema-file-upload", "style"),
    ],
    [
        Input("number_outcomes_STORAGE", "data"),
        Input("outcome_names_STORAGE", "data"),
    ]
)
def update_cinema_selection(
    number_outcomes, outcome_names
):
    num_outcomes = int(number_outcomes or 0)
    return __upload_cinema(
        num_outcomes, outcome_names
    )


@callback(
    [
        Output("cinema_net_data_STORAGE", "data"),
        Output({"type": "uploaded_cinema", "index": ALL}, "children",allow_duplicate=True),
        Output('cinema_filename_STORAGE', 'data'),
    ],
    Input({"type": "cinemafile", "index": ALL}, "contents"),
    State({"type": "cinemafile", "index": ALL}, "filename"),
    State("number_outcomes_STORAGE", "data"),
    State("cinema_net_data_STORAGE", "data"),
    State("cinema_filename_STORAGE", "data"),
    prevent_initial_call=True,
)
def upload_cinema_files(
    contents_list, filename_list, number_outcomes, existing_cinema_data, existing_filenames
):
    from tools.utils import parse_contents
    from tools.functions_cinema import validate_cinema_csv
    number_outcomes = int(number_outcomes or 0)
    if number_outcomes is None or number_outcomes < 1:
        raise PreventUpdate
    
    # Check if any new content was actually uploaded
    has_new_content = any(c is not None for c in contents_list)
    if not has_new_content:
        raise PreventUpdate
    
    # Initialize from existing storage or create new
    if existing_cinema_data and isinstance(existing_cinema_data, list):
        cinema_net_data = existing_cinema_data.copy()
        # Extend if needed
        while len(cinema_net_data) < number_outcomes:
            cinema_net_data.append(None)
    else:
        cinema_net_data = [None] * number_outcomes

    if existing_filenames and isinstance(existing_filenames, list):
        stored_filenames = existing_filenames.copy()
        while len(stored_filenames) < number_outcomes:
            stored_filenames.append(None)
    else:
        stored_filenames = [None] * number_outcomes

    # Initialize filename display from existing
    uploaded_labels = [""] * number_outcomes
    for idx in range(number_outcomes):
        if stored_filenames[idx]:
            uploaded_labels[idx] = f"Loaded: {stored_filenames[idx]}"

    # Process new uploads
    for idx, contents in enumerate(contents_list):
        if contents is None:
            continue

        try:
            cinema_df = parse_contents(contents, filename_list[idx])

            is_valid, error_msg = validate_cinema_csv(cinema_df)
            if not is_valid:
                print(f"CINeMA validation failed for {filename_list[idx]}: {error_msg}")
                continue

            cinema_net_data[idx] = cinema_df.to_json(orient="split")
            stored_filenames[idx] = filename_list[idx]
            uploaded_labels[idx] = f"Loaded: {filename_list[idx]}"

        except Exception as e:
            print(f"Error uploading CINeMA report for outcome {idx}: {e}")
    
    return cinema_net_data, uploaded_labels, stored_filenames



@callback(
    Output({"type": "uploaded_cinema", "index": ALL}, "children", allow_duplicate=True),
    Input("cinema_location", "pathname"),
    State("cinema_net_data_STORAGE", "data"),
    State("cinema_filename_STORAGE", "data"),
    State("number_outcomes_STORAGE", "data"),
    prevent_initial_call='initial_duplicate'
)
def load_cinema_from_storage(pathname, stored_data, stored_filenames, number_outcomes):
    """
    Load CINeMA data from STORAGE when navigating to CINeMA page.
    This restores the filenames when the page is refreshed or a project is imported.
    """
    if pathname != "/cinema":
        raise PreventUpdate
    
    num_outcomes = int(number_outcomes or 0)
    if num_outcomes < 1:
        raise PreventUpdate
    
    # Initialize filename display list
    filename_display = [""] * num_outcomes
    
    # Check if there's stored data and filenames
    if stored_data and isinstance(stored_data, list) and stored_filenames and isinstance(stored_filenames, list):
        for idx in range(min(len(stored_filenames), num_outcomes)):
            if stored_filenames[idx]:
                filename_display[idx] = f"Loaded: {stored_filenames[idx]}"
    
    return filename_display

