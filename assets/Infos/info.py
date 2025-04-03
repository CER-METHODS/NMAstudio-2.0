import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc

def InfoModal(infoid,infotitle,infotxt):
    infomodal = html.Div(
        [
            dbc.Button(
                infotitle, id=f'open-body-{infoid}', n_clicks=0,
                className="icon-info-sign"
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
