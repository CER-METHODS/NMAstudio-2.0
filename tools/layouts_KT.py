
import dash_bootstrap_components as dbc, dash_html_components as html
from tools.navbar import Navbar
from dash import dcc
import dash_daq as daq
import dash_cytoscape as cyto
from tools.functions_skt_others import get_skt_elements, skt_stylesheet
from tools.functions_chatbot import render_chatbot
from tools.kt_table_standard import treat_compare_grid, modal_compare_grid, modal_fullname_grid
from tools.kt_table_advance import grid
from assets.dropdowns_values import *
from tools.functions_ranking_plots import __ranking_plot_skt


FAQ_total = html.Div([
                      dbc.Button(
                                "How can I use this tool for my own project?",
                                id="faq_ques1",
                                className="faq_ques",
                                n_clicks=0,
                                ),
                      dbc.Collapse(
                                dbc.Card(dbc.CardBody("This content is hidden in the collapse")),
                                id="faq_ans1",
                                is_open=False,
                                className="faq_ans",
                            ),
                      dbc.Button(
                                "How can I ......",
                                id="faq_ques2",
                                className="faq_ques",
                                n_clicks=0,
                                ),
                      dbc.Collapse(
                                dbc.Card(dbc.CardBody("This content is hidden in the collapse")),
                                id="faq_ans2",
                                is_open=False,
                                className="faq_ans",
                            ),
                        ])

def Sktpage():
    return html.Div([
                     Navbar(),switch_table(),
                     html.Button(
                                [
                                    html.Img(src="/assets/icons/question-talk.png", className="icon-faq"),
                                    html.Span("Frequently Asked Questions", className="text-faq"),
                                ],
                                className="button-faq", id='faq_button'
                            ),
                        dbc.Toast(
                                    [
                                        dbc.Row(
                                            [
                                                html.P("Frequently Asked Questions", id = 'faq_head'),
                                                html.Img(src="/assets/icons/cancel.png", id ='close_faq')
                                                ], className='faq-header'),
                                        FAQ_total],
                                    id="faq_toast",
                                    # header="Frequently Asked Questions",
                                    is_open=False,
                                    dismissable=True,
                                    # top: 66 positions the toast below the navbar
                                    className='toast-faq'
                                ),
                     html.Div([skt_nonexpert()], id='skt_sub_content')
                     ], id='skt_page_content')


def switch_table():
    return html.Div([
                    html.Br(),
                    dcc.Markdown('Knowledge Translation Tool',
                                                className="markdown_style_main",
                                                style={
                                                    "font-weight": 'bold',
                                                    "font-size": '30px',
                                                    'text-align': 'center',
                                                    'color':'#5c7780',
                                                       }),
                    dbc.Row(dbc.Col([
                            html.P(
                            "Standard Version",
                            id='skttable_1',
                            style={'display': 'inline-block',
                                    'margin': 'auto',
                                    'font-size': '16px',
                                    'font-weight': 'bold',
                                    'color': 'chocolate',
                                    'padding-left': '0px'}),
                            daq.ToggleSwitch(
                                id='toggle_grid_select',
                                value = False,
                                color='green', size=50, vertical=False,
                                label={'label': "",
                                        'style': dict(color='white', font='0.5em')},
                                labelPosition="top",
                                style={'display': 'inline-block',
                                        'margin': 'auto', 'font-size': '10px',
                                        'padding-left': '10px',
                                        'padding-right': '10px'}),
                            html.P('Advanced Version',
                                    id='skttable_2',
                                    style={'display': 'inline-block',
                                        'margin': 'auto',
                                        'color': 'green',
                                        'font-weight': 'bold',
                                        'font-size': '16px',
                                        'padding-right': '0px'})],
                            style={'justify-content': 'center',
                                    # 'margin-left': '70%',
                                    'font-size': '0.8em', 'margin-top': '2%'},
                            ), style={'justify-content': 'center',
                                    'width': '100%'})])

def skt_nonexpert():
    return html.Div([
            html.Div(id='skt_all',children=[
                                            html.Br(id='yoda_stand_start'),html.Br(),
                                            # dcc.Markdown('Instruction: Hover your mouse over the table header to see how you can interact with it.',
                                            #     className="markdown_style_main",
                                            #     style={
                                            #         "font-size": '25px',
                                            #         'text-align': 'start',
                                            #         'font-family': 'math',
                                            #         "font-weight": 'bold',
                                            #         'color':'rgb(184 80 66)',
                                            #         'width': '90%'
                                            #            }),
                                            html.Div([dbc.Row([dbc.Col(html.Span('Project Title', className='title_first'),className='title_col1'), 
                                                               html.Div([ html.P("editable, put your project title here",
                                                                                 id='title-instruction'),
                                                                            html.A(
                                                                            html.Img(
                                                                                src="/assets/icons/query.png",
                                                                                style={
                                                                                    "width": "16px",
                                                                                    # "float":"right",
                                                                                    },
                                                                            )),],id="query-title",),
                                                              dbc.Col(dcc.Input(id='title_skt',
                                                                            value='Systematic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis', 
                                                                            style={'width':'800px'}
                                                                            ),className='title_col2')],
                                                                       className='row_skt'),
                                                      dbc.Row([dbc.Col([
                                                          dbc.Toast([dbc.Row([html.Span('PICOS', className='study_design'),
                                                                              html.Div([ html.P("editable, add more PICOS information",
                                                                                id='PICOS-instruction'),
                                                                                html.A(
                                                                                    html.Img(
                                                                                            src="/assets/icons/query.png",
                                                                                            style={
                                                                                                "width": "16px",
                                                                                                # "float":"right",
                                                                                                },
                                                                                                )),],id="query-PICOS",)
                                                                                                ]),
                                                                     dcc.Textarea(value ='Patients: patients with psoriasis\n'+
                                                                                'Primary outcome: PASI90, SAE\n'+
                                                                                'Study design: randomized control trial'
                                                                                ,className='skt_span1', style={'width':'200%'}),
                                                                            #   html.Span('Primary outcome: PASI90',className='skt_span1'), 
                                                                            #   html.Span('Study design: randomized control study', className='skt_span1'),
                                                                              ], className='tab1',headerClassName='headtab1',bodyClassName='bodytab1')
                                                                              ],className='tab1_col2'),
                                                           dbc.Col(dbc.Toast(
                                                                              [html.Span('Overall Info', className='study_design'),
                                                                              html.Span('Number of studies: 96',className='skt_span1'),
                                                                              html.Span('Number of interventions: 20', className='skt_span1'),
                                                                              html.Span('Number of participants: 1020',className='skt_span1'), 
                                                                              html.Span('Number of comparisons: 190', className='skt_span1'),
                                                                              ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'25%'}),
                                                            dbc.Col(dbc.Toast(
                                                                              [
                                                                              html.Span('Potential effect modifiers Info',className='skt_span1', style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                              html.Span('Mean age: 45.3',className='skt_span1'),
                                                                              html.Span('Mean male percentage: 43.4%',className='skt_span1'),
                                                                              html.Button('Distribution of modifiers', id='trans_button',className='sub-button',
                                                                                                            style={'color': 'rgb(118 135 123)',
                                                                                                                   'background-color':'#dedecf',
                                                                                                                    'display': 'inline-block',
                                                                                                                    'justify-self':'center',
                                                                                                                    'border': 'unset',
                                                                                                                    'padding': '4px'}),
                                                                              ], className='skt_studyinfo',headerClassName='headtab1', bodyClassName='bodytab2'), style={'width':'25%','margin-left': '1%'}),
                                
                                                            model_transitivity,
                                                            model_fullname, 
                                                            model_ranking, 
                                                            html.Div(modal_kt, style={'display': 'inline-block', 'font-size': '11px'}),
                                                            html.Div(modal_edges_kt, style={'display': 'inline-block', 'font-size': '11px'}),            
                                                                              ], className='row_skt'),

                                                      dbc.Row([
                                                            dbc.Col([
                                                                        dbc.Row([
                                                                            dbc.Row([html.Span('Interventions Diagram', className='inter_label'),
                                                                            html.Div([html.P("Select nodes/edges to display results for specific interventions or comparisons in the table below.",
                                                                                            id='diagram-instruction'),
                                                                                            html.A(
                                                                                                html.Img(
                                                                                                        src="/assets/icons/query.png",
                                                                                                        style={
                                                                                                            "width": "16px",
                                                                                                            # "float":"right",
                                                                                                            },
                                                                                                            )),],id="query-diagram",),
                                                                            html.Div(KT_Dropdown_graphlayout, style={'font-size': '11px','justify-self': 'end', 'margin-right':'20px'})],
                                                                            style={'display': 'grid', 'grid-template-columns':'1fr 1fr 3fr'}),
                                                                            dbc.Row([html.Span('Ask Dr.Bot',className='skt_span1', 
                                                                                              style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                                              html.Img(src="/assets/icons/chatbot.png",
                                                                                                       style={ "height": 30, 
                                                                                                              'margin-left': '7px'})
                                                                                              ], style={'justify-content':'center',
                                                                                                        'align-items': 'center'}),
                                                                            #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                                                                ], style={'padding-top': 0, 'display':'grid', 'grid-template-columns': '1fr 1fr'}),
                                                                        dbc.Row([
                                                                            dbc.Col([cyto.Cytoscape(id='cytoscape_skt2', responsive=False, autoRefreshLayout=True,
                                                                                    minZoom=0.6,  maxZoom=1.5,  panningEnabled=True,   
                                                                                    elements=get_skt_elements(),
                                                                                    style={ 
                                                                                        'height': '94%', 
                                                                                        'width': '100%', 
                                                                                        'margin-top': '-2%',
                                                                                        'z-index': '999',
                                                                                        'padding-left': '-10px', 
                                                                                            # 'max-width': 'calc(52vw)',
                                                                                        },
                                                                            layout={'name':'circle','animate': False, 'fit':True },
                                                                            stylesheet=get_stylesheet()),
                                                                            html.Button('Click to see treatment names', id='fullname_button',className='sub-button',
                                                                                                            style={'color': 'rgb(118 135 123)',
                                                                                                                'background-color':'#dedecf',
                                                                                                                    'display': 'inline-block',
                                                                                                                    'justify-self':'center',
                                                                                                                    'border': 'unset',
                                                                                                                    'margin-left':'2%',
                                                                                                                    'padding': '4px'}),
                                                                            html.Button('Click to see the ranking info', id='ranking_button',className='sub-button',
                                                                                                            style={'color': 'rgb(118 135 123)',
                                                                                                                'background-color':'#dedecf',
                                                                                                                    'display': 'inline-block',
                                                                                                                    'justify-self':'center',
                                                                                                                    'border': 'unset',
                                                                                                                    'margin-left':'25%',
                                                                                                                    'padding': '4px'})], 
                                                                            style={'border-right': '3px solid #B85042',
                                                                                    'width': '50%'},),
                                                                            dbc.Col(render_chatbot(), 
                                                                                    style={'width':'50%','justify-items': 'center',"height": "500px"})
                                                                                    ])
                                                                                    ], className='tab3_col2')], className='row_skt'),
                                                      html.Br(),
                                                      dbc.Row(
                                                        [dbc.Col(
                                                            [
                                                                 dbc.Popover(
                                                                        "Click a cell to open a popup for detailed and study-level information for the corresponding comparison.",
                                                                        target="info-icon-RR",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-RR",
                                                                        className= 'popover-grid'
                                                                    ),
                                                                 dbc.Popover(
                                                                        "Click a cell to open a popup for detailed and study-level information for the corresponding comparison.",
                                                                        target="info-icon-RR_out2",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-RR2",
                                                                        className= 'popover-grid'
                                                                    ),
                                                                 dbc.Popover(
                                                                        "Click switch button to switch treament and comparator.",
                                                                        target="info-icon-switch",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-switch",
                                                                        className= 'popover-grid'
                                                                    ),
                                                                 dbc.Popover(
                                                                        "Hover your mouse over a cell to view detailed information for each field.",
                                                                        target="info-icon-Certainty_out1",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-certainty1",
                                                                        className= 'popover-grid'
                                                                    ),
                                                                 dbc.Popover(
                                                                        "Hover your mouse over a cell to view detailed information for each field.",
                                                                        target="info-icon-Certainty_out2",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-certainty2",
                                                                        className= 'popover-grid'
                                                                    ),
                                                                model_skt_compare_simple,
                                                                dbc.Row(treat_compare_grid, 
                                                                        style={'width':'95%', 'justify-self':'center'}),
                                                                        ],
                                                              className='tab3_col2', id='col_nonexpert')],
                                                              className='row_skt') 
                                                        ]),html.Br(), html.Br(),
                                                      dbc.Col([
                                                dcc.Markdown('Expert Committee Members',
                                                className="markdown_style_main",
                                                style={
                                                        "font-size": '20px',
                                                        'text-align': 'center',
                                                        'color':'orange',
                                                        'border-bottom': '2px solid',
                                                        'font-weight': 'bold',
                                                        'height': 'fit-content',
                                                        # 'margin-left': '20px',
                                                        'width': '100%',
                                                        'margin-top': '0'
                                                        }),
                                                dcc.Markdown('Toshi Furukawa, Isabelle Boutron, Emily Karahalios, Tianjing li, Michael Mccaul, Adriani Nikolakopoulou, Haliton Oliveira, Thodoris Papakonstantiou, Georgia Salanti, Guido Schwarzer, Ian Saldanha, Nicky Welton, Sally Yaacoub',
                                                                className="markdown_style", style={"color": "black", 'font-size': 'large'}),
                                                html.Br(),html.Br(),html.Br(),],style={ 'width': '95%', 'padding-left': '5%'}) 
                                                        ], style={'display':'block'}),
                                                # html.Button(
                                                #         [
                                                #             html.Img(src="/assets/icons/question-talk.png", className="icon-faq"),
                                                #             html.Span("Frequently Asked Questions", className="text-faq"),
                                                #         ],
                                                #         className="button-faq", id='faq_button'
                                                #     ),
                                                # dbc.Toast(
                                                #             [
                                                #              dbc.Row(
                                                #                     [
                                                #                         html.P("Frequently Asked Questions"),
                                                #                         html.Img(src="/assets/icons/cancel.png", id ='close_faq')
                                                #                      ], className='faq-header'),
                                                #              html.P("This is the content of the toast")],
                                                #             id="faq_toast",
                                                #             # header="Frequently Asked Questions",
                                                #             is_open=False,
                                                #             dismissable=True,
                                                #             # top: 66 positions the toast below the navbar
                                                #             className='toast-faq'
                                                #         ),
                                                    ], id="skt_nonexpert_page",style={'display':'block'})

options_effects = [
       {'label': 'Add prediction interval to forestplots', 'value': 'PI'},
       {'label': 'Add direct effects to forestplots', 'value': 'direct'},
       {'label': 'Add indirect effects to forestplots', 'value': 'indirect'},
   ]

def skt_layout():
    return html.Div([
            html.Div(id='skt_all',
                     children=[
                                html.Br(),html.Br(),
                                # dcc.Markdown('Instruction: Hover your mouse over the table header to see how you can interact with it.',
                                #     className="markdown_style_main",
                                #     style={
                                #         "font-size": '25px',
                                #         'text-align': 'start',
                                #         'font-family': 'math',
                                #         "font-weight": 'bold',
                                #         'color':'rgb(184 80 66)',
                                #         'width': '90%'
                                #             }),
                                dbc.Row([html.P(f"Select outcome",className="", style={'display': 'flex', 
                                                                                                "text-align": 'right',
                                                                                                'align-items': 'center',
                                                                                                'font-weight':'bold',
                                                                                                'color':'rgb(184, 80, 66)',
                                                                                                'margin-left': '10px', 'font-size': 'large'}),
                                dcc.Dropdown(id='sktdropdown-out', options=[{'label': 'PASI90', 'value': 0}, {'label': 'SAE', 'value': 1}],
                                    clearable=False, placeholder="",value = 0,
                                    className="sktdropdown-out")], id='outselect_row'),
                                html.Br(),
                                html.Div([dbc.Row([dbc.Col(html.Span('Project Title', className='title_first'),className='title_col1'),
                                                    html.Div([ html.P("editable, put your project title here",
                                                                        id='title-instruction'),
                                                                html.A(
                                                                html.Img(
                                                                    src="/assets/icons/query.png",
                                                                    style={
                                                                        "width": "16px",
                                                                        # "float":"right",
                                                                        },
                                                                )),],id="query-title",), 
                                                    dbc.Col(dcc.Input(id='title_skt',
                                                                value='Systematic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis', 
                                                                style={'width':'800px'}
                                                                ),className='title_col2')],
                                                            className='row_skt'),
                                            dbc.Row([dbc.Col([
                                                dbc.Toast([dbc.Row([html.Span('PICOS', className='study_design'),
                                                                    html.Div([ html.P("editable, add more PICOS information",
                                                                    id='PICOS-instruction'),
                                                                    html.A(
                                                                        html.Img(
                                                                                src="/assets/icons/query.png",
                                                                                style={
                                                                                    "width": "16px",
                                                                                    # "float":"right",
                                                                                    },
                                                                                    )),],id="query-PICOS",)
                                                                                    ]),
                                                            dcc.Textarea(value ='Patients: patients with psoriasis\n'+
                                                                    'Primary outcome: PASI90\n'+
                                                                    'Study design: randomized controlled trial'
                                                                    ,className='skt_span1', style={'width':'160%'}),
                                                                #   html.Span('Primary outcome: PASI90',className='skt_span1'), 
                                                                #   html.Span('Study design: randomized control study', className='skt_span1'),
                                                                    ], className='tab1',headerClassName='headtab1',bodyClassName='bodytab1')
                                                                    ],className='tab1_col'),
                                                    dbc.Col([
                                                                dbc.Row([html.Span('Interventions Diagram', className='inter_label'),
                                                                         html.Div(KT2_Dropdown_graphlayout, 
                                                                                  style={'font-size': '11px','justify-self': 'end', 'margin-left':'60px'}),
                                                                        html.Button('Click to see treatment names', id='fullname_button',className='sub-button',
                                                                                                            style={
                                                                                                                    'background-color':'#00ab9c',
                                                                                                                    'color':'white', 
                                                                                                                    'height':'30px',
                                                                                                                    'display': 'inline-block',
                                                                                                                    'justify-self':'center',
                                                                                                                    'border': 'unset',
                                                                                                                    'margin-left':'11%',
                                                                                                                    'padding': '4px'}),
                                                                        html.Div([html.Button("Check statistical info", 
                                                                                                id="statsettings", 
                                                                                                style={
                                                                                                    'background-color':'#00ab9c',
                                                                                                    'color':'white', 
                                                                                                    'height':'30px',
                                                                                                    'display': 'inline-block',
                                                                                                    'justify-self':'center',
                                                                                                    'border': 'unset',
                                                                                                    'margin-left':'2%',
                                                                                                    'padding': '4px'}),
                                                                                  Download(id="download-statistic")]),
                                                                        ], style={'padding-top': 0}),
                                                                dbc.Row([dbc.Col([cyto.Cytoscape(id='cytoscape_skt', responsive=False, autoRefreshLayout=True,
                                                                            minZoom=0.6,  maxZoom=1.2,  panningEnabled=True,   
                                                                            elements=get_skt_elements(),
                                                                            style={ 
                                                                                'height': '50vh', 
                                                                                'width': '100%', 
                                                                                'margin-top': '-2%',
                                                                                'z-index': '999',
                                                                                'padding-left': '-10px', 
                                                                                    # 'max-width': 'calc(52vw)',
                                                                                },
                                                                    layout={'name':'circle','animate': False, 'fit':True },
                                                                    stylesheet=get_stylesheet())
                                                                    ], 
                                                                    style={'border-right': '3px solid #B85042',
                                                                            'width': '50%'}),
                                                                    dbc.Col(html.Span(id='trigger_info'),
                                                                            style={'width': '50%','align-items': 'center', 'display': 'grid'})
                                                                        ]),
                                                                    ], className='tab3_col')               
                                                                    ], className='row_skt'),

                                            dbc.Row([
                                                dbc.Col(dbc.Toast(
                                                                    [html.Span('Overall Info', className='study_design'),
                                                                    html.Span('Number of studies: 96',className='skt_span1'),
                                                                    html.Span('Number of participants: 1020',className='skt_span1'), 
                                                                    html.Span('Number of interventions: 20', className='skt_span1'),
                                                                    html.Span('Number of comparisons with direct evidence: 13', className='skt_span1'),
                                                                    html.Span('Number of comparisons without direct evidence: 8 \n', className='skt_span1',
                                                                            #  style={'border-bottom': 'dashed 1px gray'}
                                                                                )
                                                                    ], className='skt_studyinfo',headerClassName='headtab1'), style={'width':'35%'}),
                                                dbc.Col(dbc.Toast(
                                                                    [
                                                                    html.Span('Potential effect modifiers Info',className='skt_span1', style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                    html.Span('Mean age: 45.3',className='skt_span1'),
                                                                    html.Span('Mean male percentage: 43.4%',className='skt_span1'),
                                                                    html.Button('Transitivity check', id='trans_button',className='sub-button',
                                                                                                style={'color': 'rgb(118 135 123)',
                                                                                                        'background-color':'#dedecf',
                                                                                                        'display': 'inline-block',
                                                                                                        'justify-self':'center',
                                                                                                        'border': 'unset',
                                                                                                        'padding': '4px'}),
                                                                    ], className='skt_studyinfo',headerClassName='headtab1', bodyClassName='bodytab2'), style={'width':'15%','margin-left': '1%'}),
                    
                                                model_transitivity,
                                                model_fullname, 
                                                html.Div(modal_kt2, style={'display': 'inline-block', 'font-size': '11px'}),
                                                html.Div(modal_edges_kt2, style={'display': 'inline-block', 'font-size': '11px'}),                                  
                                                dbc.Col(
                                                        [dbc.Row(html.Span('Options (For the forest plots in the table)', className='option_select'), style={'display':'grid', 'padding-top':'unset'}),
                                                            dbc.Col([dbc.Toast([
                                                                html.Span('Enter the minimum clinical difference value:',className='select_outcome'),
                                                                dcc.Input(id="range_lower",
                                                                            type="text",
                                                                            name='risk',
                                                                            value=0.2,
                                                                            placeholder="e.g. 0.2", style={'width':'80px'}),
                                                                                    ],className='skt_studyinfo2', bodyClassName='slect_body',headerClassName='headtab1'),
                                                                dbc.Col([dcc.Checklist(options= options_effects, value= ['PI', 'direct', 'indirect'], 
                                                                                id='checklist_effects', style={'display': 'grid', 'align-items': 'end'}),
                                                                        ])],
                                                                                style={'display': 'grid', 'grid-template-columns': '1fr 1fr'})
                                                                                    ],
                                                        style={'width':'38%','margin-left': '1%', 'border': '1px dashed rgb(184, 80, 66)','display':'grid'}),
                                                    
                                                                
                                                                ], className='row_skt'),
                                            
                                            dbc.Row([
                                                    dbc.Col([
                                                             dcc.Store(id="detail-status",data={}),
                                                             grid, 
                                                             model_skt_stand1, 
                                                             model_skt_stand2,
                                                             html.Div(id="popover-container"),
                                                             dbc.Popover(
                                                                        "Clicking a cell will open a nested table, where the corresponding treatment will be a reference treatment.",
                                                                        target="info-icon-Reference",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-ref",
                                                                        className= 'popover-grid'
                                                                    ),
                                                             dbc.Popover(
                                                                        "This is the range of risk per 1000 in your original dataset. This can be a reference when you enter the number in 'Risk per 1000' column.",
                                                                        target="info-icon-risk_range",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-range",
                                                                        className= 'popover-grid'
                                                                    ),
                                                             
                                                             dbc.Popover(
                                                                        "You can enter a risk for the reference treatment, then the corresponding nested table will include effects in absolute scale.",
                                                                        target="info-icon-risk",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-risk",
                                                                        className= 'popover-grid'
                                                                    ),
                                                             dbc.Popover(
                                                                        "Please explain why you specified this particular risk for the reference treatment.",
                                                                        target="info-icon-rationality",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-rationality",
                                                                        className= 'popover-grid'
                                                                    ),
                                                             dbc.Popover(
                                                                        "Here you can specify the lower limit of the x-axis range for the forest plot in the nested table.",
                                                                        target="info-icon-Scale_lower",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-Scale_lower",
                                                                        className= 'popover-grid'
                                                                    ),
                                                             dbc.Popover(
                                                                        "Here you can specify the upper limit of the x-axis range for the forest plot in the nested table.",
                                                                        target="info-icon-Scale_upper",  # this must match the icon's ID
                                                                        trigger="click",
                                                                        placement="top",
                                                                        id="popover-advance-Scale_upper",
                                                                        className= 'popover-grid'
                                                                    )
                                                             ],className='skt_col2', id = 'grid_type'),
                                                                    ],className='skt_rowtable'),
                                            html.Br(), html.Br(),
                                            dbc.Row()
                                            ]),
                                            dbc.Col([
                                    dcc.Markdown('Expert Committee Members',
                                    className="markdown_style_main",
                                    style={
                                            "font-size": '20px',
                                            'text-align': 'center',
                                            'color':'orange',
                                            'border-bottom': '2px solid',
                                            'font-weight': 'bold',
                                            'height': 'fit-content',
                                            # 'margin-left': '20px',
                                            'width': '100%',
                                            'margin-top': '0'
                                            }),
                                    dcc.Markdown('Toshi Furukawa, Isabelle Boutron, Emily Karahalios, Tianjing li, Michael Mccaul, Adriani Nikolakopoulou, Haliton Oliveira, Thodoris Papakonstantiou, Georgia Salanti, Guido Schwarzer, Ian Saldanha, Nicky Welton, Sally Yaacoub',
                                                    className="markdown_style", style={"color": "black", 'font-size': 'large'}),
                                    html.Br(),html.Br(),html.Br(),],style={ 'width': '95%', 'padding-left': '5%'}) 
                                            ], style={'display':'block'}), 
                                                                    ], id='sky_expert_page')


###################################################################################################################################################################
####################################################################################################################################################################
OPTIONS = [{'label': '{}'.format(col), 'value': col} for col in ['age', 'male_percentage']]
model_transitivity = dbc.Modal(
                        [dbc.ModalHeader("Transitivity Check Boxplots"),
                         dbc.ModalBody(html.Div([html.Div([
                             dbc.Row([
                                  html.P("Choose effect modifier:", className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'}),
                                  dcc.Dropdown(id='ddskt-trans', options=OPTIONS,
                                               clearable=True, placeholder="",
                                               className="tapEdgeData-fig-class",
                                               style={'width': '150px', 'height': '30px',
                                                      'display': 'inline-block', # 'background-color': '#40515e'
                                                      }),
                                  html.Div([html.P("Box plot", id='cinemaswitchlabel1_modal',
                                                       style={'display': 'inline-block',
                                                              'font-size': 'large',
                                                              'padding-left': '10px'}),
                                                daq.ToggleSwitch(id='box_kt_scatter',
                                                                 color='', size=30,
                                                                 labelPosition="bottom",
                                                                 style={'display': 'inline-block',
                                                                        'margin': 'auto',
                                                                        'padding-left': '10px',
                                                                        'padding-right': '10px'}),
                                                html.P('Scatter plot', id='cinemaswitchlabel2_modal',
                                                       style={'display': 'inline-block', 'margin': 'auto',
                                                              'font-size': 'large',
                                                              'padding-right': '0px'})
                                                ], style={'float': 'right', 'padding': '5px 5px 5px 5px',
                                                          'display': 'inline-block', 'margin-top': '-8px'}),
                                  ])], style={'margin-top':'4px'}),
                                  html.Div([dcc.Graph(id='boxplot_skt',
                                                      style={'height': '98%',
                                                             'width': '-webkit-fill-available'},
                                  config={'editable': True,
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
                              'height':'500px',
                              })])),
                         dbc.ModalFooter(dbc.Button( "Close", id="close_trans", className="ms-auto", n_clicks=0)),
                    ],id="modal_transitivity", size='lg',is_open=False, scrollable=True,contentClassName="trans_content")


model_fullname = dbc.Modal(
    [
        dbc.ModalHeader([html.P("Full names of all interventions")],className="skt_info_head_simple", id='modal_fullname_head'),
        
        dbc.ModalBody(
            [
                dbc.Row([modal_fullname_grid],
                        style={'width':'95%', 'justify-self':'center',
                               'justify-content':'center'}),
            ],
            className="skt_info_body_simple",
        ),
        
        # Modal footer with close button
        dbc.ModalFooter(
            dbc.Button(
                "Close", 
                id="close_fullname_simple", 
                className="ms-auto", 
                n_clicks=0
            ),
            className="skt_info_close_simple",
        ),
    ],
    id="skt_modal_fullname_simple",  
    is_open=False,
    scrollable=True,
    contentClassName="skt_modal_fullname",
)


model_ranking = dbc.Modal(
                        [dbc.ModalHeader("P-score heatmap for ranking"),
                         dbc.ModalBody(
                                  html.Div([dcc.Loading(
                                         dcc.Graph(
                                             id='tab-rank1',
                                             figure = __ranking_plot_skt(),
                                             style={'height': '99%',
                                                    'max-height': 'calc(51vh)',
                                                    'width': '100%',
                                                    'margin-top': '5%',
                                                    # 'max-width': 'calc(52vw)'
                                                    },
                                             config={'editable': True,
                                                #     'showEditInChartStudio': True,
                                                #     'plotlyServerURL': "https://chart-studio.plotly.com",
                                                     'edits': dict(annotationPosition=True,
                                                                   annotationTail=True,
                                                                   annotationText=True, axisTitleText=True,
                                                                   colorbarPosition=True,
                                                                   colorbarTitleText=False,
                                                                   titleText=False,
                                                                   legendPosition=True, legendText=True,
                                                                   shapePosition=True),
                                                     'modeBarButtonsToRemove': [
                                                         'toggleSpikelines',
                                                         'resetScale2d',
                                                         "pan2d",
                                                         "select2d",
                                                         "lasso2d",
                                                         "autoScale2d",
                                                         "hoverCompareCartesian"],
                                                     'toImageButtonOptions': {
                                                         'format': 'png',
                                                         # one of png, svg,
                                                         'filename': 'custom_image',
                                                         'scale': 5
                                                         # Multiply title/legend/axis/canvas sizes by this factor
                                                     },
                                                     'displaylogo': False}), style={'display':'grid', 'justify-content':'center'})
                    ], style={'margin-top':'-30px', 
                              'height':'500px',
                              })),
                         dbc.ModalFooter(dbc.Button( "Close", id="close_rank", className="ms-auto", n_clicks=0)),
                    ],id="modal_ranking", size='lg',is_open=False, scrollable=True,contentClassName="trans_content")

model_skt_compare_simple = dbc.Modal(
    [
        dbc.ModalHeader([html.P("")],className="skt_info_head_simple", id='modal_info_head'),
        
        dbc.ModalBody(
            [
                # First row for the risk input
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span(
                                    "Enter the risk for comparator (per 1000):", 
                                    className="abvalue_simple"
                                ),
                                dcc.Input(
                                    id="simple_abvalue",
                                    type="text",
                                    name="risk",
                                    placeholder="e.g. 20", 
                                    style={"width": "80px", "margin-left": "15px"}
                                ),
                                html.Span(
                                    [html.P("The risk of comparator ranges from 10 per 1000 to 30 per 1000 in the dataset.")], 
                                    className="abvalue_range", id='risk_range'
                                ),
                                html.Br(),
                            ]
                        ),
                    ]
                ),

                # Second row for displaying other information
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Span("Outcome: PASI90", className="skt_span_info2", id="treat_comp"),
                                html.Span("Treatment: ADA", className="skt_span_info2", id="num_RCT"),
                                html.Span("Comparator: PBO", className="skt_span_info2", id="num_RCT"),
                                html.Span(
                                    "Absolute difference: 30 more per 1000", 
                                    className="skt_span_info2", 
                                    id="num_sample"
                                ),
                                html.Span(
                                    "CI: 10 per 1000 to 40 per 1000",
                                    className="skt_span_info2",
                                    id="mean_modif",
                                ),
                            ], style={'margin-right': '20px'}, id= 'text_info_col'
                        ),
                        dbc.Col(dcc.Loading(
                                    html.Div([
                                        dcc.Graph(
                                            id='barplot_compare',
                                            style={'width':'100%'},
                                            config={'editable': True,
                                                    'displayModeBar': False,
                                            'edits': dict(annotationPosition=True,
                                                        annotationTail=True,
                                                        annotationText=True, axisTitleText=False,
                                                        colorbarPosition=False,
                                                        colorbarTitleText=False,
                                                        titleText=False,
                                                        legendPosition=True, legendText=True,
                                                        shapePosition=True),
                                                'toImageButtonOptions': {
                                                    'format': 'png',
                                                    # one of png, svg,
                                                    'filename': 'custom_image',
                                                    'scale': 3.5
                                                    # Multiply title/legend/axis/canvas sizes by this factor
                                                },
                                                'displaylogo': False})], style={'width':'100%'})
                                             ),),  # Empty column for alignment
                    ], 
                    style={'display': 'grid', 
                           'grid-template-columns': '1fr 1fr', 
                           'align-items': 'center', 'border-bottom': '2px solid green'}
                ),
                
                dbc.Row([html.Span("Study Information", 
                                    className="studyinfo_simple"),
                                    modal_compare_grid],
                        style={'width':'95%', 'justify-self':'center',
                               'justify-content':'center'}),
            ],
            className="skt_info_body_simple",
        ),
        
        # Modal footer with close button
        dbc.ModalFooter(
            dbc.Button(
                "Close", 
                id="close_compare_simple", 
                className="ms-auto", 
                n_clicks=0
            ),
            className="skt_info_close_simple",
        ),
    ],
    id="skt_modal_compare_simple",  # Corrected id for typo
    is_open=False,
    scrollable=True,
    contentClassName="skt_modal_simple",
)


model_skt_stand1 = dbc.Modal(
                        [dbc.ModalHeader("Pairwise Forest Plot",className='forest_head'),
                            dbc.ModalBody([dcc.Loading(
                                    html.Div([
                                        dcc.Graph(
                                            id='forest-fig-pairwise',
                                            style={'height': '99%',
                                                'max-height': 'calc(52vw)',
                                                'width': '99%',
                                                'max-width': 'calc(52vw)'},
                                            config={'editable': True,
                                            'edits': dict(annotationPosition=True,
                                                        annotationTail=True,
                                                        annotationText=True, axisTitleText=False,
                                                        colorbarPosition=False,
                                                        colorbarTitleText=False,
                                                        titleText=False,
                                                        legendPosition=True, legendText=True,
                                                        shapePosition=True),
                                                'modeBarButtonsToRemove': [
                                                    'toggleSpikelines',
                                                    "pan2d",
                                                    "select2d",
                                                    "lasso2d",
                                                    "autoScale2d",
                                                    "hoverCompareCartesian"],
                                                'toImageButtonOptions': {
                                                    'format': 'png',
                                                    # one of png, svg,
                                                    'filename': 'custom_image',
                                                    'scale': 3.5
                                                    # Multiply title/legend/axis/canvas sizes by this factor
                                                },
                                                'displaylogo': False})], 
                                                style={'height': '450px'})
                                                ),],className='forest_body'),
                            dbc.ModalFooter(dbc.Button( "Close", id="close_forest", className="ms-auto", n_clicks=0), className='forest_close'),
                    ],id="modal_forest", is_open=False, scrollable=True,contentClassName="forest_content")

model_skt_stand2 = dbc.Modal(
        [dbc.ModalHeader("Detail information",className='skt_info_head'),
            dbc.ModalBody(
                [
                html.Span('Treatment: FUM, Comparator: PBO',className='skt_span_info', id = 'treat_comp'),
                html.Span('Randomized controlled trial: 3',className='skt_span_info', id = 'num_RCT'),
                html.Span('Total participants: 1929',className='skt_span_info', id = 'num_sample'), 
                html.Span('Mean age: xxx', className='skt_span_info', id = 'mean_modif'),
                ],className='skt_info_body'),
            dbc.ModalFooter(dbc.Button( "Close", id="close_compare", className="ms-auto", n_clicks=0), className='skt_info_close'),
    ],id="skt_modal_copareinfo", is_open=False, scrollable=True,contentClassName="forest_content")