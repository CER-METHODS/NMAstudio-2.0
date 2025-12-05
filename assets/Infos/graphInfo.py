from dash import html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

graph_info = html.P(
    "Click an edge or a node to select the corresponding direct comparison or intervention and filter or highlight the outputs at the right accordingly. Hold the 'shift' button to select multiple nodes and edges. Click at the center of the network diagram to move it up, down, left, or right. Zoom in and out with your mouse or trackpad. Click anywhere at the white space in the graph window to reset the network diagram to the default options",
    className="infoModal",
    style={"display": "inline-block", "text-align": "left", "font-size": "large"},
)

infoGraph = __info_modal("graph", "Info for Graph", graph_info)
