import dash_core_components as dcc, dash_html_components as html, dash_bootstrap_components as dbc
from assets.storage import OPTIONS_VAR
import dash_table, dash_daq as daq
from assets.Infos.dataInfo import infoscatter

OPTIONS = [{'label': '{}'.format(col), 'value': col} for col in ['age', 'bmi', 'weight', 'male_percentage']]

tab_trstvty = html.Div([html.Div([dbc.Row([html.P("Choose effect modifier:", className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",}),
                                  dcc.Dropdown(id='dropdown-effectmod', options=OPTIONS,
                                               clearable=True, placeholder="",
                                               className="tapEdgeData-fig-class",
                                               style={'width': '150px', 'height': '30px',
                                                      'display': 'inline-block', # 'background-color': '#40515e'
                                                      }),
                                   html.Div([html.P("Box plot", id='cinemaswitchlabel1_modal',
                                                       style={'display': 'inline-block',
                                                              'font-size': '15px',
                                                              'padding-left': '10px'}),
                                                daq.ToggleSwitch(id='box_vs_scatter',
                                                                 color='', size=30,
                                                                 labelPosition="bottom",
                                                                 style={'display': 'inline-block',
                                                                        'margin': 'auto',
                                                                        'padding-left': '10px',
                                                                        'padding-right': '10px'}),
                                                html.P('Scatter plot', id='cinemaswitchlabel2_modal',
                                                       style={'display': 'inline-block', 'margin': 'auto',
                                                              'font-size': '15px',
                                                              'padding-right': '0px'})
                                                ], style={'float': 'right', 'padding': '5px 5px 5px 5px',
                                                          'display': 'inline-block', 'margin-top': '0px'}),
                                   infoscatter,                      
                                  ])], 
                                  style={'margin-top':'4px',
                                         'display': 'flex',
                                         'justify-content': 'center'
                                         }),
                html.Div([dcc.Graph(id='tapEdgeData-fig',
                     style={'height': '98%',
                         #  'max-height': 'calc(51vw)',
                             'width': '-webkit-fill-available'
                         #   'max-width': 'calc(52vw)'
                           },
                                  config={'editable': True,
                                       #   'showEditInChartStudio': True,
                                       #   'plotlyServerURL': "https://chart-studio.plotly.com",
                                          'edits': dict(annotationPosition=True,
                                                    annotationTail=True,
                                                    annotationText=True, axisTitleText=True,
                                                    colorbarPosition=True,
                                                    colorbarTitleText=True,
                                                    titleText=False,
                                                    legendPosition=True, legendText=True,
                                                    shapePosition=True),
                                          'modeBarButtonsToRemove': ['toggleSpikelines', "pan2d",
                                                                 "select2d", "lasso2d",
                                                                 "autoScale2d", 'resetScale2d',
                                                                 "hoverCompareCartesian"],
                                          'toImageButtonOptions': {'format': 'png', # one of png, svg,
                                                               'filename': 'custom_image',
                                                               'scale': 5
                                                               },
                                          'displaylogo': False})
                    ], style={'margin-top':'-30px', 
                              # 'width':'1000px', 
                            #   'display':'grid',
                            #   'justify-content':'center',
                              'height':'500px',
                              })])