import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc

def __info_modal(infoid,infotitle,infotxt, direction="right"):
    infomodal = html.Div(
        [
            dbc.Button(
                 html.Img(
                    src="/assets/icons/query.png",
                    style={
                        'display': 'inline-block',
                        "width": "16px",
                        "margin-top": "0px",
                        "border-radius": "0px",},
                ),
                id=f'open-body-{infoid}', n_clicks=0,
                className="icon-info-sign",
                style={'display': 'inline-block',
                       'float': f'{direction}'}
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(infotitle),
                    dbc.ModalBody(infotxt),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close",
                            id=f'close-body-{infoid}',
                            className="ms-auto",
                            n_clicks=0,
                        )
                    ),
                ],
                id=f'modal-body-{infoid}',
                scrollable=True,
                is_open=False,
            ),
        ]
    )
    return infomodal
