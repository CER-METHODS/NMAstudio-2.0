from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from assets.Tabs.saveload_modal_button import saveload_modal
from assets.Infos.funnelInfo import infoFunnel


tab_funnel = html.Div(
    [
        # Instructions
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        "Click on a node for comparison-adjusted funnel plot, or click on an edge for comparison-specific funnel plot",
                        className="graph__title2",
                        style={
                            "display": "inline-block",
                            "verticalAlign": "top",
                            "font-size": "12px",
                            "margin-bottom": "-10px",
                        },
                    )
                ),
            ]
        ),
        # Uncomment to activate info box funnel
        # infoFunnel,
        # Node-based funnel plot (click a treatment node)
        html.H6(
            "Comparison-Adjusted Funnel Plot (Click Node)",
            style={"margin-top": "10px", "font-size": "14px", "color": "#5a87c4"},
        ),
        dcc.Loading(
            dcc.Graph(
                id="funnel-fig",
                style={
                    "height": "99%",
                    "max-height": "calc(45vw)",
                    "width": "98%",
                    "margin-top": "1%",
                    "max-width": "calc(52vw)",
                },
                config={
                    "editable": True,
                    # 'showEditInChartStudio': True,
                    # 'plotlyServerURL': "https://chart-studio.plotly.com",
                    "edits": dict(
                        annotationPosition=True,
                        annotationTail=True,
                        # annotationText=True, axisTitleText=True,
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
                        "format": "png",  # one of png, svg,
                        "filename": "funnel_node_based",
                        "scale": 5,
                    },
                    "displaylogo": False,
                },
            )
        ),
        html.Hr(style={"margin": "20px 0"}),
        # Edge-based funnel plot (click an edge/connection)
        html.H6(
            "Comparison-Specific Funnel Plot (Click Edge)",
            style={"margin-top": "10px", "font-size": "14px", "color": "#5a87c4"},
        ),
        dcc.Loading(
            dcc.Graph(
                id="funnel-fig-normal",
                style={
                    "height": "99%",
                    "max-height": "calc(45vw)",
                    "width": "98%",
                    "margin-top": "1%",
                    "max-width": "calc(52vw)",
                },
                config={
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
                        "filename": "funnel_edge_based",
                        "scale": 5,
                    },
                    "displaylogo": False,
                },
            )
        ),
    ]
)
