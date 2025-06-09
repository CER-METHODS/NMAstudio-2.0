import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

funnel_info = html.P("Comparison-adjusted funnel plots where each point correspond to the difference between the study effects and the corresponding direct summary effect. When the points are symmetrically positioned around zero, there is no indication of small-study effects in the network as a whole. Comparisons with one study only have been removed from the graph as they will always appear on the zero line. Click the color points in the legend to remove or put back in the graph interventions"
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                    )

infoFunnel = __info_modal("funnel", "Info for Funnel plot", funnel_info)

