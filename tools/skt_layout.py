import dash_bootstrap_components as dbc, dash_html_components as html
from dash import dcc
import dash_cytoscape as cyto
from tools.navbar import Navbar
from tools.functions_skt_others import get_skt_elements, skt_stylesheet
import dash_ag_grid as dag 
import pandas as pd
from assets.storage import DEFAULT_DATA
import numpy as np
import plotly.express as px, plotly.graph_objects as go
import dash_daq as daq
from tools.functions_skt_forestplot import __skt_options_forstplot, __skt_mix_forstplot
import os
from tools.skt_table import treat_compare_grid, modal_compare_grid
# from dash_yada import YadaAIO

data = pd.read_csv('db/skt/final_all.csv')
pw_data = pd.read_csv('db/skt/forest_data_prws.csv')
p_score = pd.read_csv('db/ranking/rank.csv')
df = pd.DataFrame(data)

cinima_dat = pd.read_csv('db/Cinema/cinema_report_PASI90.csv')

out_list = [['PASI90',"SAE"]]

outcome_list = [{'label': '{}'.format(out_name), 'value': out_name} for out_name in np.unique(out_list)]


# treat_list = [['PBO',"AIL1223", "ATA", "AIL17", "SM", "CSA"]]

treat_list = [np.unique(df.Treatment)]

treatment_list = [{'label': '{}'.format(treat_name), 'value': treat_name} for treat_name in np.unique(treat_list)]

long_dat = pd.read_csv('db/psoriasis_long_complete.csv')
long_dat = pd.DataFrame(long_dat)

range_ref_ab = long_dat.groupby('treat').apply(
    lambda group: pd.Series({
        "min_value": (group["rPASI90"] / group["nPASI90"]).min() * 1000,
        "max_value": (group["rPASI90"] / group["nPASI90"]).max() * 1000
    })
).reset_index()

df['Certainty']= ''
df['within_study'] = ''
df['reporting'] = ''
df['indirectness'] = ''
df['imprecision'] = ''
df['heterogeneity'] = ''
df['incoherence'] = ''

for i in range(df.shape[0]):
    src = df['Reference'][i]
    trgt = df['Treatment'][i]
    slctd_comps = [f'{src}:{trgt}']
    slctd_compsinv = [f'{trgt}:{src}']
    cinima_df = cinima_dat[cinima_dat['Comparison'].isin(slctd_comps) | cinima_dat['Comparison'].isin(slctd_compsinv)]
    df['Certainty'][i] = cinima_df['Confidence rating'].iloc[0]
    df['within_study'][i] = cinima_df['Within-study bias'].iloc[0]
    df['reporting'][i] = cinima_df['Reporting bias'].iloc[0]
    df['indirectness'][i] = cinima_df['Indirectness'].iloc[0]
    df['imprecision'][i] = cinima_df['Imprecision'].iloc[0]
    df['heterogeneity'][i] = cinima_df['Heterogeneity'].iloc[0]
    df['incoherence'][i] = cinima_df['Incoherence'].iloc[0]




# df['p-value'] = 0.05
# certainty_values = ['High', 'Low', 'Moderate']
# df['Certainty'] = np.random.choice(certainty_values, size=df.shape[0])

df['Comments'] = ['' for _ in range(df.shape[0])]
df['CI_width_hf'] = df.CI_upper - df['RR']
df['lower_error'] = df['RR'] - df.CI_lower
df['weight'] = 1/df['CI_width_hf']


df = df.round(2)

up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
up_rng = 10**np.floor(np.log10(up_rng))
low_rng = 10 ** np.floor(np.log10(low_rng))

def update_indirect_direct(row):
    if pd.isna(row['direct']):
        row['indirect'] = pd.NA
    elif pd.isna(row['indirect']):
        row['direct'] = pd.NA
    return row

df['Graph'] = ''
df['risk'] = 'Enter a number'
df['Scale_lower'] = 'Enter a value for lower'
df['Scale_upper'] = 'Enter a value for upper'
# df['ab_effect'] = ''
df['ab_difference'] = ''
df['rationality'] = 'Enter a reason'
# p_score.rename(columns={'treatment': 'Treatment'}, inplace=True)
# df = pd.merge(df, p_score, on='Treatment', how='left')


value_effect = ['PI', 'direct', 'indirect']
df_all = __skt_options_forstplot(value_effect,df,0.2,scale_lower=None, scale_upper=None, refer_name=None)

df = df_all

grouped = df.groupby(["Reference", "risk", 'Scale_lower', 'Scale_upper'])
rowData = []
for (ref, risk, Scale_lower, Scale_upper), group in grouped:
    treatments = []
    for _, row in group.iterrows():
        treatment_data = {"Treatment": row["Treatment"], 
                          "RR": row["RR"], "direct": row["direct"],
                          "Graph": row["Graph"], "indirect": row["indirect"],
                          "p-value": row["p-value"], "Certainty": row["Certainty"],
                          "direct_low": row["direct_low"],"direct_up": row["direct_up"],
                          "indirect_low": row["indirect_low"],"indirect_up": row["indirect_up"],
                          "CI_lower": row["CI_lower"],"CI_upper": row["CI_upper"],
                          "Comments": row["Comments"],
                        #   "ab_effect": row["ab_effect"],
                          "ab_difference": row["ab_difference"],
                          "within_study": row["within_study"],"reporting": row["reporting"],
                          "indirectness": row["indirectness"],"imprecision": row["imprecision"],
                          "heterogeneity": row["heterogeneity"],"incoherence": row["incoherence"],
                          }
        treatments.append(treatment_data)
    rowData.append({"Reference": ref, "risk": risk,
                    'Scale_lower': Scale_lower ,
                    'Scale_lower': Scale_upper ,
                    "Treatments": treatments})

row_data = pd.DataFrame(rowData)

row_data = row_data.merge(p_score, left_on='Reference', right_on='treatment', how='left')
row_data = row_data.merge(range_ref_ab, left_on='Reference', right_on='treat', how='left')
row_data['risk_range'] = row_data.apply(
    lambda row: f"from {int(row['min_value'])} to {int(row['max_value'])}",
    axis=1
)


row_data_default = []
for (ref, risk, Scale_lower, Scale_upper), group in grouped:
    treatments = []
    for _, row in group.iterrows():
        treatment_data = {"Treatment": row["Treatment"], 
                          "RR": row["RR"], "direct": row["direct"],
                          "Graph": row["Graph"], "indirect": row["indirect"],
                          "p-value": row["p-value"], "Certainty": row["Certainty"],
                          "direct_low": row["direct_low"],"direct_up": row["direct_up"],
                          "indirect_low": row["indirect_low"],"indirect_up": row["indirect_up"],
                          "CI_lower": row["CI_lower"],"CI_upper": row["CI_upper"],
                          "Comments": row["Comments"],
                        #   "ab_effect": row["ab_effect"],
                          "ab_difference": row["ab_difference"],
                          "within_study": row["within_study"],"reporting": row["reporting"],
                          "indirectness": row["indirectness"],"imprecision": row["imprecision"],
                          "heterogeneity": row["heterogeneity"],"incoherence": row["incoherence"],
                          }
        treatments.append(treatment_data)
    row_data_default.append({"Reference": ref, "risk": risk,
                    'Scale_lower': Scale_lower ,
                    'Scale_upper': Scale_upper ,
                    "Treatments": treatments})

row_data_default = pd.DataFrame(row_data_default)

row_data_default = row_data_default.merge(p_score, left_on='Reference', right_on='treatment', how='left')
row_data_default = row_data_default.merge(range_ref_ab, left_on='Reference', right_on='treat', how='left')

row_data_default['risk_range'] = row_data_default.apply(
    lambda row: f"from {int(row['min_value'])} to {int(row['max_value'])}",
    axis=1
)


for j in range(0, row_data_default.shape[0]):
    
    detail_data = row_data_default.loc[j, 'Treatments']
    detail_data = pd.DataFrame(detail_data)
    
    for i in range(1,detail_data.shape[0]):
        row_data_default.loc[j,'Treatments'][i]['RR'] = str(row_data_default.loc[j,'Treatments'][i]['RR'])+ '\n(' + str(row_data_default.loc[j,'Treatments'][i]['CI_lower']) + ', ' + str(row_data_default.loc[j,'Treatments'][i]['CI_upper']) + ')'
        row_data_default.loc[j,'Treatments'][i]['direct'] = f"{row_data_default.loc[j,'Treatments'][i]['direct']}" + f"\n({row_data_default.loc[j,'Treatments'][i]['direct_low']}, {row_data_default.loc[j,'Treatments'][i]['direct_up']})" if pd.notna(row_data_default.loc[j,'Treatments'][i]['direct']) else ""
        row_data_default.loc[j,'Treatments'][i]['indirect'] = f"{row_data_default.loc[j,'Treatments'][i]['indirect']}" + f"\n({row_data_default.loc[j,'Treatments'][i]['indirect_low']}, {row_data_default.loc[j,'Treatments'][i]['indirect_up']})" if pd.notna(row_data_default.loc[j,'Treatments'][i]['indirect']) else ""
        


style_certainty = {'white-space': 'pre','display': 'grid','text-align': 'center','align-items': 'center','border-left': 'solid 0.8px'}
style_mixed = {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                #    'line-height': '20px',
                   "text-align":'center',
                   'white-space': 'pre',
                   'display': 'grid',
                   'line-height': 'normal',
                   'align-items': 'center'}

masterColumnDefs = [
    {
        "headerName": "Reference Treatment",
        "filter": True,
        "field": "Reference",
        'headerTooltip': 'Click a treatment to open a nested table',
        "cellRenderer": "agGroupCellRenderer",
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px'}
        # "cellRendererParams": {
        #     'innerRenderer': "DCC_GraphClickData",
        # },
    },
    
    {"headerName": "P score\n(Ranking)", 
     "field": "pscore",
     "editable": True,
     'cellStyle': {
        'border-right': 'solid 0.8px'}
     },

      
     {"headerName": "Range of the risk\n(in dataset)", 
     "field": "risk_range",
     "editable": True,
     'cellStyle': {
        'border-right': 'solid 0.8px'}
     },

    {"headerName": "Risk per 1000", 
     "field": "risk",
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
     
     {"headerName": "The rationality of selecting the risk", 
     "field": "rationality",
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
    
     {"headerName": "Scale lower\n(forestplots)", 
     "field": "Scale_lower",
     'headerTooltip': 'This is for the forest plots in the nested table',
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
    {"headerName": "Scale upper\n(forestplots)", 
     "field": "Scale_upper",
     'headerTooltip': 'This is for the forest plots in the nested table',
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}}
]
detailColumnDefs = [
   
    {"field": "Treatment", 
     "headerName": 'Treatment',
    #  "checkboxSelection": {"function": "params.data.Treatment !== 'Instruction'"},
     "sortable": False,
     "filter": True,
     "width": 130,
     'headerTooltip': 'Click a cell to see the details of the corresponding comparison',
    #  "tooltipField": 'Treatment',
    #  "tooltipComponentParams": { "color": '#d8f0d3'},
    #  "tooltipComponent": "CustomTooltiptreat",
      "resizable": True ,
      'cellStyle': {
        'display': 'grid',
        "text-align":'center',
        'white-space': 'pre',
        'line-height': 'normal',
        'align-items': 'center'
          }},
    
    {"field": "RR", 
     "headerName": "Mixed effect\n95%CI",
     "width": 180,
     "resizable": True,
     'cellStyle': {
         "styleConditions": [
        {"condition": "params.value =='RR'", "style": { **style_mixed}},
        {"condition": "params.data.CI_lower < 1 && params.data.CI_upper < 1", "style": {"color": "red", **style_mixed}}, 
        {"condition": "params.data.CI_lower > 1 && params.data.CI_upper > 1", "style": {"color": "red", **style_mixed}},
        {
                "condition": "!(params.data.CI_lower < 1 && params.data.CI_upper < 1) && !(params.data.CI_lower > 1 && params.data.CI_upper > 1)",
                "style": {**style_mixed}
            }      
    ]}
       },

    # {"field": "ab_effect", 
    #  "headerName": "Absolute Effect",
    #  'headerTooltip': 'Specify a value for the reference treatment in \'Risk per 1000\'',
    #  "width": 180,
    #  "resizable": True,
    #  'cellStyle': {'border-left': 'solid 0.8px',
    #                'backgroud-color':'white',
    #             #    'line-height': '20px',
    #                "text-align":'center',
    #                'white-space': 'pre',
    #                'display': 'grid',
    #                'line-height': 'normal',
    #                'align-items': 'center'
    #                }
    #    },

       {"field": "ab_difference", 
     "headerName": "Absolute Difference",
     'headerTooltip': 'Specify a value for the reference treatment in \'Risk per 1000\'',
     "width": 180,
     "resizable": True,
     'cellStyle': {'border-left': 'solid 0.8px',
                   'backgroud-color':'white',
                #    'line-height': '20px',
                   "text-align":'center',
                   'white-space': 'pre',
                   'display': 'grid',
                   'line-height': 'normal',
                   'align-items': 'center'
                   }
       },

    {
        "field": "Graph",
        "cellRenderer": "DCC_GraphClickData",
        "headerName": "Forest plot",
        "width": 300,
        "resizable": True,
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px' ,'backgroud-color':'white'}

    },
    {"field": "direct",
     "headerName": "Direct effect\n(95%CI)",
     'headerTooltip': 'Click a cell with values to open the pairwise forest plot',
      "width": 170,
      "resizable": True,
      'cellStyle': {'color': '#707B7C', "text-align":'center', 'display': 'grid',
                    'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},
    {"field": "indirect",
     "headerName": "Indirect effect\n(95%CI)",
      "width": 170,
      "resizable": True,
      'cellStyle': {'color': '#ABB2B9', "text-align":'center','display': 'grid',
                    'white-space': 'pre', 'line-height': 'normal', 'align-items': 'center'}},
    {"field": "p-value",
     "headerName": "p-value\n(Consistency)",
      "width": 140,
      "resizable": True,
      'cellStyle': {"text-align":'center', 'display': 'grid','line-height': 'normal',
                    'white-space': 'pre', 'align-items': 'center'}
      },
    {"field": "Certainty", 
     "headerName": "Certainty",
    #  'headerTooltip': 'Hover the mouse on each cell to see the details',
    "filter": True,
     "width": 110,
     "resizable": True,
     "tooltipField": 'Certainty',
     "tooltipComponentParams": { "color": '#d8f0d3'},
     "tooltipComponent": "CustomTooltip",
     'cellStyle':{
        "styleConditions": [
        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},   
        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
    ]}},
    {"field": "Comments", "width": 120,
     'headerTooltip': 'Editable for adding comments', 
     "resizable": True,
     'editable': True,
     'cellStyle': {'border-left': 'solid 0.5px',"text-align":'center', 'display': 'grid','border-right': 'solid 0.8px'}},
    
    ]


getRowStyle = {
    "styleConditions": [
        {
            "condition": "params.data.RR === 'RR'",
            "style": {"backgroundColor": "#faead7",'font-weight': 'bold'},
        },
    ]
}


# sideBar={
#     "toolPanels": [
#         {
#             "id": "columns",
#             "labelDefault": "Columns",
#             "labelKey": "columns",
#             "iconKey": "columns",
#             "toolPanel": "agColumnsToolPanel",
#         },
#         {
#             "id": "filters",
#             "labelDefault": "Filters",
#             "labelKey": "filters",
#             "iconKey": "menu",
#             "toolPanel": "agFiltersToolPanel",
#         },
#     ],
#     "position": "left",
#     "defaultToolPanel": "filters",
# }

grid = dag.AgGrid(
    id="quickstart-grid",
    className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=os.environ["AG_GRID_KEY"],
    columnDefs=masterColumnDefs,
    rowData = row_data_default.to_dict("records"),
    masterDetail=True,
    # getRowStyle=getRowStyle,
    detailCellRendererParams={
                "detailGridOptions": {
                "columnDefs": detailColumnDefs,
                # "sideBar": sideBar,
                "rowHeight": 80,
                "rowDragManaged": True,
                "rowDragMultiRow": True,
                "rowDragEntireRow": True,
                "rowSelection": "multiple",
                'getRowStyle': getRowStyle,
                "detailCellClass": "ag-details-grid",
                },
                "detailColName": "Treatments",
                "suppressCallback": True,
            },
    dangerously_allow_code=True,
    defaultColDef={
                    # "resizable": True, 
                #    "sortable": False, "filter": True,
                    "wrapText": True, 
                    'autoHeight': True,
                    "enableRowGroup": False,
                    "enableValue": False,
                    "enablePivot": False,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                  'border-bottom': 'solid 0.5px',
                                #   'background-color':'#faead7'
                                  },
                    # "tooltipComponent": "CustomTooltip"
                    },
    columnSize="sizeToFit", 
    dashGridOptions = {'suppressRowTransform': True,
                    #    "domLayout":'print',
                       "rowSelection": "multiple",
                    #    "tooltipShowDelay": 100,
                       "rowDragManaged": True,
                       "rowDragMultiRow": True,
                       "rowDragEntireRow": True,
                    #    "detailRowHeight": 70+83*19,
                       "detailRowAutoHeight": True,
                       }, 
    getRowId='params.data.Reference',
    style={ "width": "100%",
           'height':f'{46.5 *20}px'
           }
    
)




####################################################################################################################################################################
####################################################################################################################################################################
OPTIONS = [{'label': '{}'.format(col), 'value': col} for col in ['age', 'male']]
model_transitivity = dbc.Modal(
                        [dbc.ModalHeader("Transitivity Check Boxplots"),
                         dbc.ModalBody(html.Div([html.Div([dbc.Row([html.P("Choose effect modifier:", className="graph__title2",
                                         style={'display': 'inline-block',
                                                'verticalAlign':"top",
                                                'font-size': '12px',
                                                'margin-bottom': '-10px'}),
                                  dcc.Dropdown(id='ddskt-trans', options=OPTIONS,
                                               clearable=True, placeholder="",
                                               className="tapEdgeData-fig-class",
                                               style={'width': '150px', 'height': '30px',
                                                      'display': 'inline-block', # 'background-color': '#40515e'
                                                      })
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
                                                        
radio_treattment = dbc.RadioItems(id='ref_selected', options=treatment_list, value='PBO',inline=True, 
                                                                                       inputStyle={'width':'30px'}, 
                                                                                style={'display': 'contents','font-size':"medium"},
                                                                                      labelCheckedStyle={"color": "red"},)

display_treatment = [html.Span(treat, className='span_treat') for treat in treat_list[0]]




model_password = dbc.Modal(
        [
            dbc.ModalBody(
                [
                html.Span('Input the password:', style={'font-size':'large'}),
                dcc.Input(id='password', className='upload_radio', style={'width':'150px'}),
                html.Br(),
                dbc.Button( "OK", id="password_ok",n_clicks=0, style={'background-color':'grey'})
                ]),
    ],id="pass_model", is_open=True, contentClassName="pass_content", style={'display':'block'})
####################################################################################################################################################################
####################################################################################################################################################################
# instruct_plot = ('/assets/figure/instruction_skt1.png')

empty = [html.Span('Instruction',className='skt_span1', 
                   style={'color': '#B85042', 'font-weight': 'bold'}),
         html.Span([html.Strong('Ref:'), ' selected reference treatment\n',
                    html.Strong('Treatment:'), ' click the cell to see the corresponding comparison information\n',
                    html.Strong('Direct effect:'), ' click to see the forestplot for the corresponding comparsion\n',
                    html.Strong('Certainty:'), ' hover your mouse see the details about certainty of evidence\n',
                    html.Strong('Comments:'), ' editable, add comments if necessary'],
                   className='empty_class'),
        #  html.Img(src=instruct_plot, height="100px", style={'justify-self': 'center'})
                   ]
options_effects = [
       {'label': 'Add prediction interval to forestplots', 'value': 'PI'},
       {'label': 'Add direct effects to forestplots', 'value': 'direct'},
       {'label': 'Add indirect effects to forestplots', 'value': 'indirect'},
   ]

# def Sktpage():
#     return html.Div([Navbar(), model_password], id='skt_page_content')
# def Sktpage():
#     return html.Div([Navbar(), skt_home(), skt_layout(), skt_nonexpert()], id='skt_page_content')
def Sktpage():
    return html.Div([Navbar(),switch_table(),html.Div([skt_nonexpert()], id='skt_sub_content')], id='skt_page_content')
# def Sktpage():
#     return html.Div([Navbar(),skt_nonexpert()], id='skt_page_content')

# def skt_home():
#     return html.Div([
#         html.Div(id='skt_profile', 
#                  children=[html.Br(), html.Br(),html.Br(), html.Br(),
#                      dcc.Markdown('Select your profile',
#                                                 className="markdown_style_main",
#                                                 style={
#                                                     "font-size": '40px',
#                                                     'text-align': 'center',
#                                                     'color':'#5c7780',
#                                                        }),
#                            html.Br(), html.Br(),
#                            dbc.Row([html.A([html.Img(src="/assets/icons/expert.png",
#                                         style={'width': '200px'}),
#                                     html.Span('Methodologists',className='profile_text'),
#                                         ],
#                                         id="expert_profile"),
#                                     html.A([html.Img(src="/assets/icons/nonexpert.png",
#                                         style={'width': '200px'}),
#                                         html.Span('Others',className='profile_text'),
#                                         ],
#                                         id="nonexpert_profile")    
#                                         ], id='profile_row'),
#                                         ])
#     ], id="skt_profile_page")

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


def skt_layout():
    return html.Div([
            html.Div(id='skt_all',children=[
                # dcc.Markdown('Scalable Knowledge Translation Tool',
                #                                 className="markdown_style_main",
                #                                 style={
                #                                     "font-size": '30px',
                #                                     'text-align': 'center',
                #                                     'color':'#5c7780',
                #                                        }),
                                    # html.Button("Export to Excel", id="btn-excel-export"),
                                    # html.Button("print", id="grid-printer-layout-btn"),
                                    # html.Button("regular", id="grid-regular-layout-btn"),
                                            # dbc.Col([
                                            #     html.P(
                                            #     "Standard skt",
                                            #     id='skttable_1',
                                            #     style={'display': 'inline-block',
                                            #             'margin': 'auto',
                                            #             'font-size': '10px',
                                            #             'padding-left': '0px'}),
                                            #     daq.ToggleSwitch(
                                            #         id='toggle_grid_select',
                                            #         value = False,
                                            #         color='green', size=30, vertical=False,
                                            #         label={'label': "",
                                            #                 'style': dict(color='white', font='0.5em')},
                                            #         labelPosition="top",
                                            #         style={'display': 'inline-block',
                                            #                 'margin': 'auto', 'font-size': '10px',
                                            #                 'padding-left': '2px',
                                            #                 'padding-right': '2px'}),
                                            #     html.P('league table',
                                            #             id='skttable_2',
                                            #             style={'display': 'inline-block',
                                            #                 'margin': 'auto',
                                            #                 'font-size': '10px',
                                            #                 'padding-right': '0px'})],
                                            #     style={'justify-content': 'flex-end',
                                            #             'margin-left': '70%',
                                            #             'font-size': '0.8em', 'margin-top': '2%'},
                                            #     ),
                                            html.Br(),html.Br(),
                                            dcc.Markdown('Instruction: Hover your mouse over the table header to see how you can interact with it.',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '25px',
                                                    'text-align': 'start',
                                                    'font-family': 'math',
                                                    "font-weight": 'bold',
                                                    'color':'rgb(184 80 66)',
                                                    'width': '90%'
                                                       }),
                                            dbc.Row([html.P(f"Select outcome",className="", style={'display': 'flex', 
                                                                                                          "text-align": 'right',
                                                                                                          'align-items': 'center',
                                                                                                          'font-weight':'bold',
                                                                                                          'color':'rgb(184, 80, 66)',
                                                                                                          'margin-left': '10px', 'font-size': 'large'}),
                                            dcc.Dropdown(id='sktdropdown-out', options=[{'label': 'PASI90', 'value': 0}, {'label': 'SAE', 'value': 1}],
                                               clearable=True, placeholder="",
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

                                                                # dbc.Col([
                                                                #          dbc.Row([html.Span('Interventions', className='inter_label'),
                                                                #                 #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                                                #                  ], style={'padding-top': 0}),
                                                                #          dbc.Toast(
                                                                #                 display_treatment, 
                                                                #                 bodyClassName='skt_interbody',
                                                                #                 className='skt_intervention',
                                                                #                 headerClassName='headtab1',
                                                                #                 id='treatment_toast'
                                                                #               )
                                                                #               ], className='tab2_col'),
                                                                dbc.Col([
                                                                         dbc.Row([html.Span('Interventions Diagram', className='inter_label'),
                                                                                 ], style={'padding-top': 0}),
                                                                         dbc.Row([dbc.Col(cyto.Cytoscape(id='cytoscape_skt', responsive=False, autoRefreshLayout=True,
                                                                                        minZoom=0.6,  maxZoom=1.2,  panningEnabled=True,   
                                                                                        elements=get_skt_elements(),
                                                                                        style={ 
                                                                                            'height': '40vh', 
                                                                                            'width': '100%', 
                                                                                            'margin-top': '-2%',
                                                                                            'z-index': '999',
                                                                                            'padding-left': '-10px', 
                                                                                                # 'max-width': 'calc(52vw)',
                                                                                            },
                                                                                layout={'name':'circle','animate': False, 'fit':True },
                                                                                stylesheet=skt_stylesheet()), 
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
                                                            dbc.Col(
                                                                    [dbc.Row(html.Span('Options (For the forest plots in the table)', className='option_select'), style={'display':'grid', 'padding-top':'unset'}),
                                                                     dbc.Col([dbc.Toast([
                                                                            html.Span('Enter the minimum clinical difference value:',className='select_outcome'),
                                                                            dcc.Input(id="range_lower",
                                                                                        type="text",
                                                                                        name='risk',
                                                                                        value=0.2,
                                                                                        placeholder="e.g. 0.2", style={'width':'80px'}),
                                                                            # html.Span('Enter the range of equvalence upper:',className='select_outcome'),
                                                                            # dcc.Input(id="range_upper",
                                                                            #             type="text",
                                                                            #             name='risk',
                                                                            #             value=1.25,
                                                                            #             placeholder="e.g. 1.25",style={'width':'80px'}) 
                                                                                                ],className='skt_studyinfo2', bodyClassName='slect_body',headerClassName='headtab1'),
                                                                            dbc.Col([dcc.Checklist(options= options_effects, value= ['PI', 'direct', 'indirect'], 
                                                                                          id='checklist_effects', style={'display': 'grid', 'align-items': 'end'}),
                                                                            # html.Div([
                                                                            #     html.Div([ html.P("The forest plots in the table will be presented on a logarithmic scale.",
                                                                            #      id='logscale-instruction'),
                                                                            #     html.A(
                                                                            #     html.Img(
                                                                            #         src="/assets/icons/query.png",
                                                                            #         style={
                                                                            #             "width": "16px",
                                                                            #             # "float":"right",
                                                                            #             },
                                                                            #     )),],id="query-logscale",),
                                                                            #     html.P("log scale", id='',
                                                                            #             style={'display': 'inline-block',
                                                                            #                     'font-size': '12px',
                                                                            #                     'padding-left': '10px'}),
                                                                            #         daq.ToggleSwitch(id='nomal_vs_log',
                                                                            #                         color='', size=30,
                                                                            #                         labelPosition="bottom",
                                                                            #                         style={'display': 'inline-block',
                                                                            #                                 'margin': 'auto',
                                                                            #                                 'padding-left': '10px',
                                                                            #                                 'padding-right': '10px'}),
                                                                            #         html.P('absolute scale', id='',
                                                                            #             style={'display': 'inline-block', 'margin': 'auto',
                                                                            #                     'font-size': '12px',
                                                                            #                     'padding-right': '0px'}),
                                                                            #         html.Div([ html.P("The forest plots in the table will be presented on a absolute scale.",
                                                                            #                    id='abscale-instruction'),
                                                                            #         html.A(
                                                                            #         html.Img(
                                                                            #             src="/assets/icons/query.png",
                                                                            #             style={
                                                                            #                 "width": "16px",
                                                                            #                 # "float":"right",
                                                                            #                 },
                                                                            #         )),],id="query-abscale",),
                                                                            #         ], style={'display': 'inline-block', 'margin-top': '0px'})
                                                                                    ])],
                                                                                            style={'display': 'grid', 'grid-template-columns': '1fr 1fr'})
                                                                                                ],
                                                                    style={'width':'38%','margin-left': '1%', 'border': '1px dashed rgb(184, 80, 66)','display':'grid'}),
                                                               
                                                                          
                                                                          ], className='row_skt'),
                                                      
                                                      dbc.Row([
                                                               dbc.Col([grid, model_skt_stand1, model_skt_stand2],className='skt_col2', id = 'grid_type'),
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

#############################################SKT Non-experts####################################################################################################
ROUTINE = '/assets/icons/routine.png'
SIDE = '/assets/icons/side_effect.png'
CONT = '/assets/icons/contrain.png'
VISIT = '/assets/icons/visit.png'
COST = '/assets/icons/cost.png'
RANK = '/assets/ranking.png'
from tools.functions_chatbot import render_chatbot


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
                                            


# from tools.yada import yada_stand

def skt_nonexpert():
    return html.Div([
            # yada_stand,
            html.Div(id='skt_all',children=[
                # dcc.Markdown('Scalable Knowledge Translation Tool',
                #                                 className="markdown_style_main",
                #                                 style={
                #                                     "font-size": '30px',
                #                                     'text-align': 'center',
                #                                     'color':'#5c7780',
                #                                        }),
                                            html.Br(id='yoda_stand_start'),html.Br(),
                                            dcc.Markdown('Instruction: Hover your mouse over the table header to see how you can interact with it.',
                                                className="markdown_style_main",
                                                style={
                                                    "font-size": '25px',
                                                    'text-align': 'start',
                                                    'font-family': 'math',
                                                    "font-weight": 'bold',
                                                    'color':'rgb(184 80 66)',
                                                    'width': '90%'
                                                       }),
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
                                                                                                            )),],id="query-diagram",)]),
                                                                            dbc.Row([html.Span('Ask Dr.Bot',className='skt_span1', 
                                                                                              style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                                              html.Img(src="/assets/icons/chatbot.png",
                                                                                                       style={ "height": 30, 
                                                                                                              'margin-left': '7px'})
                                                                                              ], style={'justify-content':'center',
                                                                                                        'align-items': 'center'}),
                                                                            #  html.Span('Please tick to select the reference treatment', className='note_tick')
                                                                                ], style={'padding-top': 0, 'display':'grid', 'grid-template-columns': '1fr 1fr'}),
                                                                        dbc.Row([dbc.Col(cyto.Cytoscape(id='cytoscape_skt2', responsive=False, autoRefreshLayout=True,
                                                                                    minZoom=0.6,  maxZoom=1.5,  panningEnabled=True,   
                                                                                    elements=get_skt_elements(),
                                                                                    style={ 
                                                                                        'height': '100%', 
                                                                                        'width': '100%', 
                                                                                        'margin-top': '-2%',
                                                                                        'z-index': '999',
                                                                                        'padding-left': '-10px', 
                                                                                            # 'max-width': 'calc(52vw)',
                                                                                        },
                                                                            layout={'name':'circle','animate': False, 'fit':True },
                                                                            stylesheet=skt_stylesheet()), 
                                                                            style={'border-right': '3px solid #B85042',
                                                                                    'width': '50%'}),
                                                                            dbc.Col(render_chatbot(), style={'width':'50%','justify-items': 'center',"height": "500px"})
                                                                            # dbc.Col([
                                                                            #     # html.Span('Interventions practical issues',className='skt_span1', 
                                                                            #     #               style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                            #         dbc.Row([
                                                                            #                 dbc.Col([html.Img(src=ROUTINE,
                                                                            #                 width="45px", style={'justify-self':'center'},
                                                                            #                 className='medpractice', id='routine'),
                                                                            #                 html.Span('Medical routine',className= 'main_results1')], 
                                                                            #                 className='col_results1'),
                                                                            #                 dbc.Col([html.Img(src=CONT,
                                                                            #                 width="45px", style={'justify-self':'center'},
                                                                            #                 className='medpractice', id='cont'),
                                                                            #                 html.Span('Contraindications', className= 'main_results1')],
                                                                            #                 className='col_results1'),
                                                                            #                 dbc.Col([html.Img(src=SIDE,
                                                                            #                 width="45px", style={'justify-self':'center'},
                                                                            #                 className='medpractice', id='side'),
                                                                            #                 html.Span('Side effects', className= 'main_results1')],
                                                                            #                 className='col_results1'),
                                                                            #                 dbc.Col([html.Img(src=VISIT, n_clicks=0,
                                                                            #                 width="45px", style={'justify-self':'center'},
                                                                            #                 className='medpractice', id='visit'),
                                                                            #                 html.Span('Visit and test', className= 'main_results1')],
                                                                            #                 className='col_results1'),
                                                                            #                 dbc.Col([html.Img(src=COST,
                                                                            #                 width="45px", style={'justify-self':'center'},
                                                                            #                 className='medpractice', id='cost'),
                                                                            #                 html.Span('Cost', className= 'main_results1')],
                                                                            #                 className='col_results1'),
                                                                            #                 ],
                                                                            #                 style={'width' : '-webkit-fill-available',
                                                                            #                             'justify-content': 'center',}
                                                                            #                             ),
                                                                            #         dbc.Row(html.Span(id='trigger_info2'),
                                                                            #             style={'align-items': 'center','margin-bottom': '50%',
                                                                            #                    'display': 'grid','background-color':'burlywood', 'height': '95%'})
                                                                            #                             ],style={'width':'50%', 'justify-content': 'center','display': 'grid'})
                                                                                                        ]),], className='tab3_col2')], className='row_skt'),
                                                      html.Br(),
                                                      dbc.Row(
                                                        [dbc.Col(
                                                            [
                                                                model_skt_compare_simple,
                                                                # dbc.Row([dbc.Col([
                                                                # html.Span('Absolute Values for Comparators (per 1000)',className='skt_span1', 
                                                                #         style={'color': '#B85042', 'font-weight': 'bold'}),
                                                                #         outcome_absolute],className='out_abs_col'),
                                                                #         # dbc.Col([html.Img(src=RANK, style={'justify-self':'center','width':'300px'}, id='rank_img')],className='out_rank_col')
                                                                #         ], style={'justify-content':'space-around'}),
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
                                                                              ], id="skt_nonexpert_page",style={'display':'block'})
####################################################################################################################################################################
####################################################################################################################################################################

df_league = pd.read_csv("db/skt/league_table.csv")

n_row =df_league.shape[0]

# def add_line_break(value):
#     return str(value).replace("(", "\n(")

# # Apply the function to the entire DataFrame
# df_league = df_league.applymap(add_line_break)

column_names = df_league.columns.tolist()


for idx, column in enumerate(column_names):
    if idx < 2:
        pass   
    for row_idx in range(idx-1):
        treat1 = column
        treat2 = df_league['Treatment'][row_idx]
        df_league.iloc[row_idx,idx] = f' {treat2} VS. {treat1} \n Randomize control trial: 3\n Total participants in arm: xxx \n Mean age: xxx \nMean male percentage: XXX'

for column_idx, column in enumerate(column_names):
    if column_idx < 1 or column_idx >19:
        continue


    for row_idx in range(column_idx, n_row):

        filterdata = df_league.iloc[row_idx]
        filterdata = pd.DataFrame([filterdata])
        treat_t = filterdata['Treatment'].iloc[0]
        treat_c = column_names[column_idx]
        direct_info = df[(df['Treatment'] == treat_c) & (df['Reference'] == treat_t)]
        direct_info = direct_info.apply(update_indirect_direct, axis=1)
        filterdata = df_league.iloc[row_idx]
        filter_df = pd.DataFrame([filterdata])  
        filter_df[column_names[column_idx]] = filter_df[column_names[column_idx]].str.replace(r'\s', '', regex=True)

        filter_df['point'] = filter_df[column_names[column_idx]].str.extract(r'(\d+\.\d+)')[0].astype(float)
        filter_df['lower'] = filter_df[column_names[column_idx]].str.extract(r'\((\d+\.\d+),')[0].astype(float)
        filter_df['upper'] = filter_df[column_names[column_idx]].str.extract(r',(\d+\.\d+)\)')[0].astype(float)
        filter_df['CI_width_hf'] = (filter_df.upper - filter_df['point'])
        filter_df['lower_error'] = (filter_df['point'] - filter_df.lower)
    
        filter_df['direct'] = direct_info['direct']
        filter_df['indirect'] = direct_info['indirect']
        
        filterDf = filter_df.iloc[0]
        filter_df = pd.DataFrame([filterDf])

        filter_df = pd.concat([filter_df] * 4, ignore_index=True)

        filter_df['CI_width_hf'][3] = (direct_info.CI_upper - direct_info['RR']*1.2)
        filter_df['lower_error'][3] = (direct_info['RR'] - direct_info.CI_lower*1.2)


        filter_df['Treatment'][1] = 'Direct'
        filter_df['point'][1] = direct_info['direct']
        filter_df['CI_width_hf'][1] = (direct_info.direct_up - direct_info['direct'])
        filter_df['lower_error'][1] = (direct_info['direct'] - direct_info.direct_low)

        filter_df['Treatment'][0] = 'Indirect'
        filter_df['point'][0] = direct_info['indirect']
        filter_df['CI_width_hf'][0] = (direct_info.indirect_up - direct_info['indirect'])
        filter_df['lower_error'][0] = (direct_info['indirect'] - direct_info.indirect_low)

        # filter_df['weight'] = 1/(filter_df.upper - filter_df.lower)
        # error_x_colors = ['red', 'black']

        colors = ['#C35214', '#4D4DFF', 'red','black']
        text1 = f"<b>{treat_c} VS. {treat_t}</b> <span style='color:black'><br>{filter_df[column_names[column_idx]][0]}</span>"
        text2 = f"<span style='color:#4D4DFF'><br>{direct_info['direct'].iloc[0]}({direct_info['direct_low'].iloc[0]},{direct_info['direct_up'].iloc[0]})</span>" if pd.notna(direct_info['direct'].iloc[0]) else ""
        text3 =f"<span style='color:#C35214'><br>{direct_info['indirect'].iloc[0]}({direct_info['indirect_low'].iloc[0]},{direct_info['indirect_up'].iloc[0]})</span>" if pd.notna(direct_info['indirect'].iloc[0]) else ""
        text_leagtab = text1+text2+text3

        fig = go.Figure()
        for idx in range(filter_df.shape[0]):
            data_point = filter_df.iloc[idx]
            if not pd.notna(data_point['point']):
                continue
            fig.add_trace(go.Scatter(
                            x=[data_point['point']],
                            y=[data_point['Treatment']],
                            # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                            error_x=dict(type='data',color = colors[idx],array=[data_point['lower_error'],data_point['CI_width_hf']],visible=True),
                            marker=dict(color=colors[idx], size=8),
                            showlegend=False,
                        ))

        fig.update_layout(
                barmode='group',
                bargap=0.25,
                showlegend=False,
                yaxis_visible=False,
                yaxis_showticklabels=False,
                xaxis_visible=False,
                xaxis_showticklabels=False,
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=True,
                hovermode = False,
                height=150,  # Set the height to 100 pixels
                width=200,
                shapes=[
                dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0="0.8",
                    y0="0",
                    x1="1.25",
                    y1='1',
                    fillcolor="gray",
                    opacity=0.4,
                    line_width=0,
                    layer="below"
                ),]
               
        )
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                            line=dict(color="green", width=1,dash="dot"), layer='below')


        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                            plot_bgcolor='rgba(0,0,0,0)')

        fig.add_annotation(
                            x=np.log10(2), 
                            y=1, 
                            # xanchor='center',  align='center',yanchor='top',
                            # xref='paper', yref='y domain',
                            # text= f"<b>{treat_c} VS. {treat_t}</b> <br>{filter_df[column_names[column_idx]][0]}",
                            text = text_leagtab,
                            showarrow=False, font=dict(size=12)
                            )
        # fig.add_annotation(
        #                     # x=np.log10(np.abs(filter_df['point'][0])),
        #                     x=np.log10(2),
        #                     y = 0.7,
        #                     # xanchor='center',  align='center',yanchor='top',
        #                     # xref='paper', yref='y domain',
        #                     text= f"<br>",
        #                     showarrow=False,
        #                     font=dict(size=12,color = 'gray'))

        df_league.iloc[row_idx, column_idx] = fig


treatnames = df_league.columns[1:]

default_style = {'white-space': 'pre',
                'display': 'grid',
                'text-align': 'center',
                # 'align-items': 'center',
                'border': 'solid 0.5px gray',
                # 'line-height': 'initial'
                'height' : '163px',
                'line-height': 'normal'
                }

columnDefs2=[
    {"field": "Treatment", 
     "headerName": "Treatment",
     "tooltipField": 'ticker',
     "tooltipComponentParams": { "color": '#d8f0d3' },
     "sortable": False,
     "filter": True, 
     'cellStyle': {'font-weight':'bold',
                    'background-color':'#B85042','color':'white','font-size':'12px', **default_style}}  
    ]+[{"field": i,
        "cellRenderer": "DCC_GraphClickData",
        "maxWidth": 500,
        "minWidth": 300,
        'cellStyle': {"styleConditions":[{"condition": f"params.value === '{i}'", 
                                       "style": {"backgroundColor": "antiquewhite", **default_style}},
                                       {"condition": f"params.value !== '{i}'", 
                                       "style": {**default_style}}
                                       ]}}  for i in treatnames]
############################League Table######################################################

# grid2 = dag.AgGrid(
#     id="grid2",
#     rowData=df_league.to_dict("records"),
#     columnDefs= columnDefs2,
#     defaultColDef={"resizable": False, 
#                    "filter": True, "minWidth":125,
#                    "wrapText": True, 
#                    'autoHeight': True,
#                     'cellStyle': {'white-space': 'pre',
#                                   'display': 'grid2',
#                                   'text-align': 'center',
#                                 #   'align-items': 'center',
#                                   'background-color':'#E7E8D1',
#                                   'border': 'solid 0.5px gray',
#                                 #   "styleConditions":styleConditions
#                                     # "styleConditions": [
#                                     #   {"condition": "params.value === 'ADA'", 
#                                     #    "style": {"backgroundColor": "green"}}]
#                                 },
#                    }, 
#     columnSize="sizeToFit",
#     # dashGridOptions = {'suppressRowTransform': True,
#     #                    "rowSelection": "multiple",
#     #                    "tooltipShowDelay": 100}, 
#     style={'width': '1200px','height': f'{48 + 163 * n_row}px'},
# )

# checklist = dcc.Checklist(options= df_league.columns[1:], value= df_league.columns[1:3].values, 
#                           id='checklist_treat', style={'display': 'contents'})
# button_clear=html.Button('select all', id='clear-val', n_clicks=0)


