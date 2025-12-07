from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from assets.COLORS import *
from assets.Infos.rankInfo import infoRank

# Graph configurations shared between both graphs
graph_config = {
    "editable": True,
    "edits": dict(
        annotationPosition=True,
        annotationTail=True,
        annotationText=True,
        axisTitleText=True,
        colorbarPosition=True,
        colorbarTitleText=False,
        titleText=False,
        legendPosition=True,
        legendText=True,
        shapePosition=True,
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
        "filename": "custom_image",
        "scale": 5,
    },
    "displaylogo": False,
}

graph_style = {
    "height": "99%",
    "max-height": "calc(51vh)",
    "width": "100%",
    "margin-top": "5%",
}

# Tab styles
tab_style = {
    "height": "40%",
    "display": "flex",
    "justify-content": "center",
    "alignItems": "center",
    "font-size": "12px",
    "color": "grey",
    "padding": "0",
}

tab_selected_style = {
    "height": "40%",
    "display": "flex",
    "justify-content": "center",
    "alignItems": "center",
    "background-color": "#f5c198",
    "font-size": "12px",
    "padding": "0",
}

# Heatmap content (Tab 1)
heatmap_content = html.Div(
    id="ranking-heatmap-container",
    children=[
        dcc.Loading(
            dcc.Graph(
                id="graph-rank1",
                style=graph_style,
                config=graph_config,
            ),
            style={"display": "grid", "justify-content": "center"},
        )
    ],
    style={"display": "block"},  # Visible by default
)

# Scatter plot content (Tab 2)
scatter_content = html.Div(
    id="ranking-scatter-container",
    children=[
        infoRank,
        dbc.Col(
            dbc.Row(
                [
                    html.P(
                        f"Select outcome 2",
                        className="selectbox",
                        style={
                            "display": "inline-block",
                            "text-align": "right",
                            "margin-left": "0px",
                            "font-size": "12px",
                        },
                    ),
                    dcc.Dropdown(
                        id="ranking_outcome_select2",
                        searchable=True,
                        placeholder="...",
                        className="box",
                        value=1,
                        clearable=False,
                        style={
                            "width": "80px",
                            "height": "30px",
                            "vertical-align": "middle",
                            "font-family": "sans-serif",
                            "margin-bottom": "2px",
                            "display": "inline-block",
                            "color": "black",
                            "font-size": "10px",
                            "margin-left": "-7px",
                        },
                    ),
                ]
            ),
            style={
                "margin-bottom": "0px",
                "justify-content": "end",
                "display": "flex",
            },
        ),
        dcc.Loading(
            dcc.Graph(
                id="graph-rank2",
                style=graph_style,
                config=graph_config,
            ),
            style={"display": "grid", "justify-content": "center"},
        ),
    ],
    style={"display": "none"},  # Hidden by default
)

# Tabs for navigation only (content is outside)
tab_ranking = html.Div(
    [
        dcc.Tabs(
            id="subtabs-rank1",
            value="Tab-rank1",
            vertical=False,
            persistence=True,
            children=[
                dcc.Tab(
                    label="P-scores Heatmap",
                    id="tab-rank1",
                    value="Tab-rank1",
                    className="control-tab",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="P-scores Scatter plot",
                    id="tab-rank2",
                    value="Tab-rank2",
                    className="control-tab",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
            ],
            colors={"border": "grey", "primary": "grey", "background": "white"},
        ),
        # Content containers outside tabs - both always exist in DOM
        heatmap_content,
        scatter_content,
    ]
)
