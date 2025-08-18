import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
import dash_daq as daq
from assets.Tabs.saveload_modal_button import saveload_modal
from assets.Infos.funnelInfo import infoFunnel




tab_funnel1 = html.Div([dbc.Row([dbc.Col(html.P("Click on a node to generate the plot", #Click treatment sequentially to get desired ordering",
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
tab_funnel2 = html.Div([dbc.Row([dbc.Col(html.P("Click on an edge to generate the plot", #Click treatment sequentially to get desired ordering",
                                         className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '18px',
                                                'margin-bottom': '-10px'})),
                                infoFunnel]),
                       dcc.Loading(
                           dcc.Graph(
                               id='funnel-fig-normal',
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

tab_funnel = dcc.Tabs(id='', value = 'tab_funel', vertical=False, persistence=True,
                      children=[dcc.Tab(label='Comparison-adjusted plot', id='tab_funel', value='tab_funel', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'black', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center','background-color': '#f5c198',
                                                 'font-size': '12px', 'padding': '0'},
                                children=[tab_funnel1]),
                                dcc.Tab(label='Standard plot', id='tab_funel_2', value='funel_2', className='control-tab',
                                 style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                        'align-items': 'center',
                                        'font-size': '12px', 'color': 'black', 'padding': '0'},
                                 selected_style={'height': '30%', 'display': 'flex', 'justify-content': 'center',
                                                 'align-items': 'center','background-color': '#f5c198',
                                                 'font-size': '12px', 'padding': '0'},
                                children=[tab_funnel2])
                                ]
                      )

