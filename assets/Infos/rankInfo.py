import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

rank_info = html.P("P-scores for two selected outcomes simultaneously. Interventions lying in the upper-right corner are those that are ranked high for both outcomes. The different colors represent different clusters of interventions with similar performance based on the p-score values"
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                   )

infoRank = __info_modal("rank", "Infobox", rank_info)
