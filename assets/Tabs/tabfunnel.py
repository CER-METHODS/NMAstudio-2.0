from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from assets.Tabs.saveload_modal_button import saveload_modal
from assets.Infos.funnelInfo import infoFunnel, infoFunnel2


# Graph configuration shared between both funnel plots
funnel_graph_config = {
    "editable": True,
    "edits": dict(
        annotationPosition=True,
        annotationTail=True,
        colorbarPosition=True,
        colorbarTitleText=False,
        titleText=False,
        legendPosition=True,
        legendText=True,
        shapePosition=False,
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
        "filename": "funnel_plot",
        "scale": 5,
    },
    "displaylogo": False,
}

funnel_graph_style = {
    "height": "99%",
    "max-height": "calc(50vw)",
    "width": "98%",
    "margin-top": "1%",
    "max-width": "calc(52vw)",
}

# Comparison-adjusted funnel plot (click a node)
tab_funnel1 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        "Click a node to generate the plot",
                        className="graph__title2",
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "font-size": "18px",
                            "margin-bottom": "-10px",
                        },
                    )
                ),
                infoFunnel,
            ]
        ),
        dcc.Loading(
            dcc.Graph(
                id="funnel-fig",
                style=funnel_graph_style,
                config=funnel_graph_config,
            )
        ),
    ]
)

# Standard funnel plot (click an edge)
tab_funnel2 = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        "Click on an edge to generate the plot",
                        className="graph__title2",
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "font-size": "18px",
                            "margin-bottom": "-10px",
                        },
                    )
                ),
                infoFunnel2,
            ]
        ),
        dcc.Loading(
            dcc.Graph(
                id="funnel-fig-normal",
                style=funnel_graph_style,
                config=funnel_graph_config,
            )
        ),
    ]
)

# Tab-based funnel view - shows one funnel at a time
tab_funnel = dcc.Tabs(
    id="funnel-subtabs",
    value="tab_funnel",
    vertical=False,
    persistence=True,
    children=[
        dcc.Tab(
            label="Comparison-adjusted plot",
            id="tab_funnel",
            value="tab_funnel",
            className="control-tab",
            style={
                "height": "30%",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "font-size": "medium",
                "color": "black",
                "padding": "0",
            },
            selected_style={
                "height": "30%",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "background-color": "#f5c198",
                "font-size": "medium",
                "padding": "0",
            },
            children=[tab_funnel1],
        ),
        dcc.Tab(
            label="Standard plot",
            id="tab_funnel_2",
            value="funnel_2",
            className="control-tab",
            style={
                "height": "30%",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "font-size": "medium",
                "color": "black",
                "padding": "0",
            },
            selected_style={
                "height": "30%",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "background-color": "#f5c198",
                "font-size": "medium",
                "padding": "0",
            },
            children=[tab_funnel2],
        ),
    ],
)
