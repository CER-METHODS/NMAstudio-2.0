import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.Tabs.saveload_modal_button import saveload_modal
from assets.Infos.funnelInfo import infoFunnel


tab_funnel = html.Div([dbc.Row([dbc.Col(html.P("Click on a node or edges to generate the plot", #Click treatment sequentially to get desired ordering",
                                         className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '18px',
                                                'margin-bottom': '-10px'})),
                                infoFunnel]),
                       dcc.Loading(
                           dcc.Graph(
                               id='funnel-fig',
                               style={'height': '99%',
                                      'max-height': 'calc(50vw)',
                                      'width': '98%',
                                      'margin-top': '1%',
                                      'max-width': 'calc(52vw)'},
                               config={'editable': True,
                                      # 'showEditInChartStudio': True,
                                      # 'plotlyServerURL': "https://chart-studio.plotly.com",
                                       'edits': dict(annotationPosition=True,
                                                     annotationTail=True,
                                                    # annotationText=True, axisTitleText=True,
                                                     colorbarPosition=True,
                                                     colorbarTitleText=False,
                                                     titleText=False,
                                                     legendPosition=True, legendText=True,
                                                     shapePosition=False),
                                       'modeBarButtonsToRemove': [
                                           'toggleSpikelines',
                                           'resetScale2d',
                                           "pan2d",
                                           "select2d",
                                           "lasso2d",
                                           "autoScale2d",
                                           "hoverCompareCartesian"],
                                       'toImageButtonOptions': {
                                           'format': 'png',  # one of png, svg,
                                           'filename': 'custom_image',
                                           'scale': 5
                                       },
                                       'displaylogo': False}))
                       ])
