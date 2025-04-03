from dash import html
import dash_bootstrap_components as dbc
from assets.Infos.info import InfoModal

expand_info = html.P(
    "Click this button to expand or reduce the corresponding window. This button is available for all outputs and the network diagram.",
    className="infoModal",
    style={"display": "inline-block", "text-align": "left", "font-size": "large"},
)

infoExpand = InfoModal("expand", "Infobox", expand_info)

year_info = html.P(
    "Use the slider to see the evolution of the network over time. The data table will be filtered accordingly.",
    className="infoModal",
    style={"display": "inline-block", "text-align": "left", "font-size": "large"},
)

infoYear = InfoModal("year", "Infobox", year_info)

scatter_info = html.P(
    "Please include a 'sample_size' column in your dataset to make the scatter point sizes proportional to sample size. Otherwise, all points will have the same size.",
    className="infoModal",
    style={"display": "inline-block", "text-align": "left", "font-size": "large"},
)

infoscatter = InfoModal("scatter", "Infobox", scatter_info)
