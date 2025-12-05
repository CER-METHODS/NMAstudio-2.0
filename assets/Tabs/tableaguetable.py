from assets.dropdowns_values import *
from assets.Infos.leagueInfo import infoCinema, infoLeague1, infoRoB


tab_league = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        infoLeague1,
                    ],
                    style={"display": "inline-block", "padding-top": "10px"},
                ),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    [
                        html.Button(
                            "Export table",
                            id="league-export",
                            n_clicks=0,
                            className="btn-export",
                            style={
                                "margin-left": "5px",
                                "padding": "4px 4px 4px 4px",
                                "fontSize": "medium",
                                "text-align": "left",
                                "font-weight": "900",
                                "font-family": "sans-serif",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        dcc.Download(id="download_leaguetable"),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Upload(
                            html.A(
                                "Upload CINeMA report",
                                style={
                                    "margin-left": "5px",
                                    "font-size": "15px",
                                    "font-weight": "bold",
                                    "color": "rgb(90, 135, 196)",
                                },
                            ),
                            id="datatable-secondfile-upload",
                            multiple=False,
                            style={
                                "display": "inline-block",
                                "font-size": "12px",
                                "padding-top": "12px",
                                "margin-right": "-30px",
                            },
                        )
                    ],
                    style={"display": "inline-block"},
                ),
                infoCinema,
                dbc.Col(
                    [
                        html.Ul(
                            id="file2-list",
                            style={
                                "margin-left": "15px",
                                "color": "#dae8e8",
                                "font-size": "11px",
                            },
                        )
                    ],
                    style={"display": "inline-block"},
                ),
            ]
        ),
        html.Div(
            [
                html.P(
                    "Risk of Bias",
                    id="cinemaswitchlabel1",
                    style={
                        "display": "inline-block",
                        "font-size": "large",
                        "padding-left": "10px",
                    },
                ),
                daq.ToggleSwitch(
                    id="rob_vs_cinema",
                    value=False,
                    color="",
                    size=30,
                    labelPosition="bottom",
                    style={
                        "display": "inline-block",
                        "margin": "auto",
                        "padding-left": "10px",
                        "padding-right": "10px",
                    },
                ),
                html.P(
                    "CINeMA rating",
                    id="cinemaswitchlabel2",
                    style={
                        "display": "inline-block",
                        "margin": "auto",
                        "font-size": "large",
                        "padding-right": "0px",
                    },
                ),
                infoRoB,
            ],
            style={
                "float": "right",
                "padding": "5px 5px 5px 5px",
                "display": "inline-block",
                "margin-top": "-2px",
            },
        ),
        html.Div(
            id="league_table_legend",
            style={
                "display": "flex",
                "width": "100%",
                "justify-content": "end",
                "padding": "5px 5px 5px 5px",
            },
        ),
        html.Div(id="league_table"),
        html.Div(id="img_div"),
    ]
)


tab_league_both = html.Div(
    [
        dbc.Row(
            [
                html.Div(
                    [
                        html.Button(
                            "Export table",
                            id="league-export-both",
                            n_clicks=0,
                            className="btn-export",
                            style={
                                "margin-left": "5px",
                                "padding": "4px 4px 4px 4px",
                                "fontSize": "medium",
                                "text-align": "left",
                                "font-weight": "900",
                                "font-family": "sans-serif",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        dcc.Download(id="download_leaguetable_both"),
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Upload(
                            html.A(
                                "Upload CINeMA report for outcome 1",
                                style={
                                    "margin-left": "5px",
                                    "font-size": "15px",
                                    "font-weight": "bold",
                                    "color": "rgb(90, 135, 196)",
                                },
                            ),
                            id="datatable-secondfile-upload-1",
                            multiple=False,
                            style={
                                "display": "inline-block",
                                "font-size": "14px",
                                "padding-left": "45px",
                            },
                        )
                    ],
                    style={"display": "inline-block"},
                ),
                dbc.Col(
                    [
                        html.Ul(
                            id="file-list-out1",
                            style={
                                "margin-left": "15px",
                                "color": "black",
                                "font-size": "11px",
                            },
                        )
                    ],
                    style={"display": "inline-block"},
                ),
                dbc.Col(
                    [
                        dcc.Upload(
                            html.A(
                                "Upload CINeMA report 2 for outcome 2",
                                style={
                                    "margin-left": "5px",
                                    "margin-top": "1px",
                                    "font-size": "15px",
                                    "font-weight": "bold",
                                    "padding-bottom": "4px",
                                    "color": "rgb(90, 135, 196)",
                                },
                            ),
                            id="datatable-secondfile-upload-2",
                            multiple=False,
                            style={"display": "inline-block", "font-size": "12px"},
                        )
                    ],
                    style={"display": "inline-block"},
                ),
                dbc.Col(
                    [
                        html.Ul(
                            id="file-list-out2",
                            style={
                                "margin-left": "15px",
                                "color": "black",
                                "font-size": "11px",
                                "vertical-alignment": "middle",
                            },
                        )
                    ],
                    style={
                        "display": "inline-block",
                        "margin-top": "0px",
                        "margin-bottom": "0px",
                    },
                ),
            ]
        ),
        html.Div(
            [
                html.P(
                    "Risk of Bias",
                    id="cinemaswitchlabel1-both",
                    style={
                        "display": "inline-block",
                        "font-size": "large",
                        "padding-left": "10px",
                    },
                ),
                daq.ToggleSwitch(
                    id="rob_vs_cinema-both",
                    value=False,
                    color="",
                    size=30,
                    labelPosition="bottom",
                    style={
                        "display": "inline-block",
                        "margin": "auto",
                        "padding-left": "10px",
                        "padding-right": "10px",
                    },
                ),
                html.P(
                    "CINeMA rating",
                    id="cinemaswitchlabel2-both",
                    style={
                        "display": "inline-block",
                        "margin": "auto",
                        "font-size": "large",
                        "padding-right": "0px",
                    },
                ),
            ],
            style={
                "float": "right",
                "padding": "5px 5px 5px 5px",
                "display": "inline-block",
                "margin-top": "-2px",
            },
        ),
        html.Div(
            id="league_table_legend_both",
            style={
                "display": "flex",
                "width": "100%",
                "justify-content": "end",
                "padding": "5px 5px 5px 5px",
            },
        ),
        html.Div(id="league_table_both"),
        html.Div(id="img_div_both"),
    ]
)
