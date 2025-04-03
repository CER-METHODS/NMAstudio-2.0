from dash import html
import dash_bootstrap_components as dbc
from assets.Infos.info import InfoModal

funnel_info = html.P("This is the information you need to do forall funnel plots"
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'right'}
                    )

infoFunnel = InfoModal("funnel","Info for Funnel plots", funnel_info)

