from dash import html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

incons_info = html.P(
    "Select interventions or comparisons in the network diagram "
    "to filter the table of the side-splitting results accordingly. Comparisons in "
    "red are those with statistically significant inconsistency (p-value≤0.05) and "
    "those in blue are those with 0.05≤p-value≤0.10",
    className="infoModal",
    style={"display": "inline-block", "text-align": "left", "font-size": "large"},
)

infoIncons = __info_modal("incons", "Information", incons_info)
