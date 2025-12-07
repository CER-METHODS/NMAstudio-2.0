from dash import dcc
from dash import html
from dash import dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc

from assets.storage import CONSISTENCY_DATA
from assets.Infos.inconsInfo import infoIncons


def tab_consistency(consistency_data=CONSISTENCY_DATA):
    consistency_data["Q"] = consistency_data["Q"].round(2)
    consistency_data["p-value"] = consistency_data["p-value"].round(3)
    return html.Div(
        [
            infoIncons,
            html.Div(
                [
                    html.Br(),
                    html.Br(),
                    html.P(
                        "Design-by-treatment interaction model",
                        style={
                            "font-size": "medium",
                            "margin-top": "-0.6%",
                            "margin-left": "20%",
                        },
                        className="box__title",
                    ),
                ]
            ),
            dash_table.DataTable(
                id="consistency-table",
                export_format="csv",
                columns=[{"name": i, "id": i} for i in consistency_data.columns],
                data=consistency_data.to_dict("records"),
                style_cell={
                    "backgroundColor": "rgba(0,0,0,0.1)",
                    "color": "black",
                    "textAlign": "center",
                    "minWidth": "35px",
                    "maxWidth": "40px",
                    "border": "1px solid #5d6d95",
                    "overflow": "hidden",
                    "whiteSpace": "no-wrap",
                    "textOverflow": "ellipsis",
                    "fontFamily": "sans-serif",
                    "fontSize": "15px",
                },
                style_data_conditional=[
                    {
                        "if": {
                            "filter_query": "{p-value} > 0 && {p-value} < 0.10",
                            "column_id": "p-value",
                        },
                        "color": "tomato",
                        "fontWeight": "bold",
                    },
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgba(0,0,0,0.2)",
                    },
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "rgba(0, 116, 217, 0.3)",
                        "border": "1px solid rgb(0, 116, 217)",
                    },
                ],
                style_header={
                    "backgroundColor": "slategrey",
                    "fontWeight": "bold",
                    "border": "1px solid #5d6d95",
                },
                style_table={
                    "overflowX": "scroll",
                    "overflowY": "scroll",
                    "height": "99%",
                    "max-height": "400px",
                    "minWidth": "100%",
                    "width": "99%",
                    "max-width": "calc(52vw)",
                    "padding": "5px 5px 5px 5px",
                },
                css=[
                    {
                        "selector": "tr:hover",
                        "rule": "background-color: rgba(0, 0, 0, 0);",
                    },
                    {
                        "selector": "td:hover",
                        "rule": "background-color: rgba(0, 116, 217, 0.3) !important;",
                    },
                ],
            ),
            html.Br(),
            html.Div(
                [
                    html.Div(
                        [
                            html.Button(
                                "Export table",
                                id="consistency-export",
                                n_clicks=0,
                                className="btn-export2",
                                style={
                                    "margin-right": "5%",
                                    "padding": "4px 4px 4px 4px",
                                    "color": "black",
                                    "fontSize": "medium",
                                    "font-weight": "900",
                                    "font-family": "sans-serif",
                                    "display": "inline-block",
                                },
                            ),
                            html.P(
                                id="export-cons-button-hidden",
                                style={"display": "none"},
                            ),
                            dcc.Download(id="download_consistency"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Button(
                                "Save all",
                                "btn-netsplit-all",
                                n_clicks=0,
                                className="btn-export2",
                                style={
                                    "padding": "0px 4px 0px 4px",
                                    "margin-right": "5%",
                                    "margin-bottom": "2px",
                                    "fontSize": "medium",
                                    "font-weight": "900",
                                    "font-family": "sans-serif",
                                    "display": "inline-block",
                                },
                            ),
                            html.P(
                                id="export-cons-all-button-hidden",
                                style={"display": "none"},
                            ),
                            dcc.Download(id="download_consistency_all"),
                            dbc.Tooltip(
                                "All net-split results with indirect comparisons",
                                style={
                                    "color": "black",
                                    "font-size": "medium",
                                    "margin-left": "10px",
                                    "letter-spacing": "0.3rem",
                                },
                                placement="top",
                                target="btn-netsplit-all",
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                "Side-splitting model",
                                style={
                                    "font-size": "medium",
                                    "margin-top": "0.8%",
                                    "display": "inline-block",
                                },
                                className="box__title",
                            ),
                            html.Br(),
                            html.P(
                                "Select edge(s) to display specific comparison(s)",
                                style={
                                    "font-size": "medium",
                                    "margin-top": "-1.2%",
                                    "display": "inline-block",
                                },
                                className="box__title",
                            ),
                        ]
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id="netsplit_table-container",
                            fixed_rows={"headers": True, "data": 0},
                            # export_format="csv", #xlsx
                            # columns=[{"name": i, "id": i} for i in df.columns],
                            # data=df.to_dict('records'),
                            style_cell={
                                "backgroundColor": "rgba(0,0,0,0)",
                                "color": "black",
                                "textAlign": "center",
                                "minWidth": "35px",
                                "maxWidth": "40px",
                                "border": "1px solid #5d6d95",
                                "overflow": "hidden",
                                "whiteSpace": "no-wrap",
                                "textOverflow": "ellipsis",
                                "fontFamily": "sans-serif",
                                "fontSize": "15px",
                            },
                            style_data_conditional=[
                                {
                                    "if": {
                                        "filter_query": "{p-value} <= 0.05",
                                        "column_id": "p-value",
                                    },
                                    "color": "tomato",
                                    "fontWeight": "bold",
                                },
                                {
                                    "if": {
                                        "filter_query": "{p-value} > 0.05 && {p-value} <= 0.10",
                                        "column_id": "p-value",
                                    },
                                    "color": "blue",
                                    "fontWeight": "bold",
                                },
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgba(0,0,0,0.1)",
                                },
                                {
                                    "if": {"state": "active"},
                                    "backgroundColor": "rgba(0, 116, 217, 0.3)",
                                    "border": "1px solid rgb(0, 116, 217)",
                                },
                            ],
                            style_header={
                                "backgroundColor": "grey",
                                "fontWeight": "bold",
                                "border": "1px solid #5d6d95",
                            },
                            style_table={
                                "overflowX": "scroll",
                                "overflowY": "scroll",
                                "height": "97%",
                                "max-height": "calc(30vh)",
                                "minWidth": "100%",
                                "width": "90%",
                                "max-width": "calc(50vw)",
                                "padding": "5px 5px 5px 5px",
                            },
                            css=[
                                {
                                    "selector": "tr:hover",
                                    "rule": "background-color: rgba(0, 0, 0, 0);",
                                },
                                {
                                    "selector": "td:hover",
                                    "rule": "background-color: rgba(0, 116, 217, 0.3) !important;",
                                },
                            ],
                        )
                    ),
                ]
            ),
            html.Br(),
        ]
    )
