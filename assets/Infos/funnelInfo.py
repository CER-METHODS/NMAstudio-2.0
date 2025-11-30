import dash_html_components as html
import dash_bootstrap_components as dbc
from assets.Infos.info import __info_modal

funnel_info = html.P("Comparison-adjusted funnel plots where each point correspond to the difference between the study effects and the corresponding direct summary effect. When the points are symmetrically positioned around zero, there is no indication of small-study effects in the network as a whole. Comparisons with one study only have been removed from the graph as they will always appear on the zero line. Click the color points in the legend to remove or put back in the graph interventions"
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                    )

infoFunnel = __info_modal("funnel", "Info for Comparison-adjusted Funnel Plot", funnel_info)


funnel_info2 = html.P("Standard funnel plots display each study's effect estimate against a measure of its precision (such as sample size or standard error). In a typical funnel-shaped plot, smaller and less precise studies appear widely scattered at the bottom, while larger and more precise studies cluster toward the top with narrower spread. If the plot shows asymmetry or missing points at the bottom, it may indicate publication bias, where studies with non-significant or unfavorable results are less likely to be published. \n Users can select a comparison that includes at least two studies in the network diagram to generate the plot, and at least ten studies are required to assess potential asymmetry."
                    ,className="infoModal"
                    ,style={'display':'inline-block',"text-align":'left', 'font-size': 'large'}
                    )

infoFunnel2 = __info_modal("funnel2", "Info for Standard Funnel Plot", funnel_info2)
