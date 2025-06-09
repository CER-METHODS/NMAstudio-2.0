import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

expand_info = html.P("Click this button to expand or reduce the corresponding window. This button is available for all outputs and the network diagram."
                   ,className="infoModal"
                   ,style={'display':'inline-block',
                           "text-align":'left', 'font-size': 'large'}
                   )

infoExpand = __info_modal("expand","Infobox", expand_info)

year_info = html.P("Use the slider to see the evolution of the network over\
time. The data table will be filtered accordingly."
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                   )

infoYear = __info_modal("year","Infobox", year_info)
