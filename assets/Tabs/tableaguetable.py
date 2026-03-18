from assets.dropdowns_values import *
from assets.Infos.leagueInfo import infoCinema, infoLeague1, infoRoB
from dash import dcc, html
import dash_bootstrap_components as dbc


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
                        # Link to CINeMA page - always a link, not an upload
                        dcc.Link(
                            "Upload CINeMA report",
                            id="cinema-link-to-page",
                            href="/cinema",
                            style={
                                "margin-left": "5px",
                                "font-size": "15px",
                                "font-weight": "bold",
                                "color": "rgb(90, 135, 196)",
                                "textDecoration": "underline",
                                "paddingTop": "12px",
                                "display": "inline-block",
                            },
                        ),
                        # Display loaded filename when CINeMA data exists
                        html.Span(
                            id="cinema-filename-display",
                            style={
                                "marginLeft": "10px",
                                "fontSize": "13px",
                                "color": "green",
                                "fontWeight": "bold",
                            }
                        ),
                    ],
                    style={"display": "inline-block", "paddingTop": "12px"},
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
                        # Single link to CINeMA page for both outcomes
                        dcc.Link(
                            id="cinema-link-both",
                            children="Upload CINeMA report for both outcomes",
                            href="/cinema",
                            style={
                                "margin-left": "5px",
                                "font-size": "15px",
                                "font-weight": "bold",
                                "color": "rgb(90, 135, 196)",
                                "textDecoration": "underline",
                            },
                        ),
                        # Display status when CINeMA data exists for both selected outcomes
                        html.Span(
                            id="cinema-filename-display-both",
                            style={
                                "marginLeft": "10px",
                                "fontSize": "13px",
                                "color": "green",
                                "fontWeight": "bold",
                            }
                        ),
                    ],
                    style={"display": "inline-block", "paddingTop": "12px"},
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
