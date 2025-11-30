import dash_ag_grid as dag
import os
import pandas as pd
import numpy as np
from tools.functions_skt_forestplot import __skt_options_forstplot, __skt_mix_forstplot

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
        "headerComponent": "HeaderWithIcon",
        # 'headerTooltip': 'Click a treatment to open a nested table',
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
     "headerComponent": "HeaderWithIcon",
     "editable": True,
     'cellStyle': {
        'border-right': 'solid 0.8px'}
     },

    {"headerName": "Risk per 1000", 
     "field": "risk",
     "editable": True,
     "headerComponent": "HeaderWithIcon",
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
     
     {"headerName": "The rationality of selecting the risk", 
     "field": "rationality",
     "editable": True,
     "headerComponent": "HeaderWithIcon",
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
    
     {"headerName": "Scale lower\n(forestplots)", 
     "field": "Scale_lower",
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'This is for the forest plots in the nested table',
     "editable": True,
     'cellStyle': {
        'color': 'grey','border-right': 'solid 0.8px'}
     },
    {"headerName": "Scale upper\n(forestplots)", 
     "field": "Scale_upper",
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'This is for the forest plots in the nested table',
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
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'Click a cell to see the details of the corresponding comparison',
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
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'Specify a value for the reference treatment in \'Risk per 1000\'',
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
        "headerComponent": "HeaderWithIcon",
        "width": 300,
        "resizable": True,
        'cellStyle': {'border-left': 'solid 0.8px',
                      'border-right': 'solid 0.8px' ,'backgroud-color':'white'}

    },
    {"field": "direct",
     "headerName": "Direct effect\n(95%CI)",
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'Click a cell with values to open the pairwise forest plot',
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
     "headerComponent": "HeaderWithIcon",
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
     "headerComponent": "HeaderWithIcon",
    #  'headerTooltip': 'Editable for adding comments', 
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
                       "detailRowAutoHeight": True,
                       }, 
    getRowId='params.data.Reference',
    style={ "width": "100%",
           'height':f'{46.5 *20}px'
           }
    
)