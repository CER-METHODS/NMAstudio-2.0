import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

league_info = html.P("The lower triangle shows all the network estimates \
for the selected outcome and the upper triangles shows the direct estimates. \
Each cell includes the relative effect along with the respective confidence \
interval of the intervention in the column versus the intervention in the row. \
Empty cells correspond to comparisons without direct evidence"
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'right'}
                   )

infoLeague1 = __info_modal("league1", "Infobox", league_info, "left")

rob_info = html.P("By default, the colors in the cells represent the average risk of bias of the studies in each direct comparison. Use this button to switch to colors representing the CINeMA evaluations for all comparisons. This requires that the CINeMA report has already been uploaded"
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'right'}
                   )

infoRoB = __info_modal("RoB", "Infobox", rob_info)

cinema_info = html.P("This requires that the CINeMA evaluation has been already performed for the selected outcome. If not, please visit https://cinema.ispm.unibe.ch/. The final CINeMA report including the columns “Comparison”, “Confidence rating”, and “Reasons for downgrading”, can be uploaded. Then the ratings of all comparisons appear optionally in the league table as different colors"
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'right'}
                   )

infoCinema = __info_modal("cinema", "Infobox", cinema_info)

league2_info = html.P("The lower triangle corresponds to the network estimates for the first outcome and the upper triangle to the network estimates for the second outcome as these have been specified during data upload. (here it is impossible to identify which triangle corresponds to which outcome so the legend would be very helpful). Select the interventions in the network diagram in the desired order to re-order or reduce the interventions in the diagonal of the table"
                   ,className="infoModal"
                   ,style={'display':'inline-block',"text-align":'right'}
                   )

infoLeague2 = __info_modal("league2", "Infobox", league_info, "left")

