import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

forest_info = html.P("Switch on or off the display of the prediction intervals \
on top of the confidence intervals. Prediction intervals show the interval \
within which the effect of a future study is expected to lie and serve as a way \
to evaluate the impact of heterogeneity (tau-square) in the results."
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                    )

infoForest = __info_modal("forest","Info for Forest plot", forest_info)


forest_info2 = html.P("Summary estimates and confidence intervals for two \
outcomes simultaneously. Click the points in the legends to remove or put back \
in the graph corresponding interventions "
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                    )

infoForest2 = __info_modal("forest2","Info for 2D Forest plot", forest_info2)
