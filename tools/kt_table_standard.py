
import dash_ag_grid as dag
import os
import pandas as pd
import itertools
import numpy as np
import dash_iconify
import json


# data_absolute = {
#     'Outcome 1': ['Enter a value'],
#     'Outcome 2': ['Enter a value']
# }

# data_absolute = pd.DataFrame(data_absolute)
# data_absolute['index']=data_absolute.index

# absolueColumnDefs = [
   
#     {"headerName": "Outcome 1", 
#      "field": "Outcome 1",
#      "editable": True,
#      "resizable": False,
#      'cellStyle': {
#         'color': 'grey','border-right': 'solid 0.8px'}
#      },

#     {"headerName": "Outcome 2", 
#      "field": "Outcome 2",
#      "editable": True,
#      "resizable": False,
#      'cellStyle': {
#         'color': 'grey','border-right': 'solid 0.8px'}
#      }
# ]


# outcome_absolute = dag.AgGrid(
#     id="grid_absolute",
#     className="absolute-alpine color-fonts",
#     enableEnterpriseModules=True,
#     licenseKey=os.environ["AG_GRID_KEY"],
#     columnDefs=absolueColumnDefs,
#     rowData = data_absolute.to_dict("records"),
#     dangerously_allow_code=True,
#     defaultColDef={
#                     'filter':False,
#                     "floatingFilter": False,
#                     "wrapText": True, 
#                     'autoHeight': True,
#                     "enableRowGroup": False,
#                     "enableValue": False,
#                     "enablePivot": False,
#                     'cellStyle': {'white-space': 'pre',
#                                   'display': 'grid',
#                                   'text-align': 'center',
#                                   'align-items': 'center',
#                                   'border-bottom': 'solid 0.5px'
#                                   },
#                     # "tooltipComponent": "CustomTooltip"
#                     },
#     columnSize="sizeToFit", 
#     getRowId='params.data.index',
#     style={"height":"58px"}  
# )



data = pd.read_csv('db/skt/skt_df_two.csv')
df = pd.DataFrame(data)
df["index"] = df.index
# treat_list = np.unique(df.Treatment).tolist()

# combinations = list(itertools.combinations(treat_list, 2))

# treatment = []
# comparator =[]

# for pair in combinations:
#     treatment.append(pair[0])
#     comparator.append(pair[1])

# treat_compare = pd.DataFrame({
#     'treatment': treatment,
#     'comparator': comparator
# })



df['switch']=np.nan
# df['ab_out1'] = ''
# df['ab_out2'] = ''
df = np.round(df,2)
# df['RR_inv']=np.round(1/df['RR'],2)
# df['RR_inv2']=np.round(1/df['RR_out2'],2)

df['RR'] = df.apply(lambda row: f"{row['RR']}\n({row['CI_lower']} to {row['CI_upper']})", axis=1)

df['RR_out2'] = df.apply(lambda row: f"{row['RR_out2']}\n({row['CI_lower_out2']} to {row['CI_upper_out2']})", axis=1)

df_origin = df.copy()

style_certainty = {'white-space': 'pre','display': 'grid','text-align': 'center','align-items': 'center','border-left': 'solid 0.8px'}
ColumnDefs_treat_compare = [
   
    {"headerName": "Treatment", 
     "field": "Treatment",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
      #   'background-color': '#a6d4a6bd',
      #   'color':'#04800f',
        'font-weight':'bold'
        }
     },
    
     {"headerName": "Switch", 
      "suppressHeaderMenuButton": True,
     "field": "switch",
     "editable": False,
     "resizable": False,
     "headerComponent": "HeaderWithIcon", 
     "cellRenderer": "DMC_Button",
     "cellRendererParams": {
            # "variant": "text",
            "icon": "subway:round-arrow-3",  # Use 'icon' instead of 'leftIcon' or 'rightIcon'
            "color": "#ffc000",
        },
     'cellStyle': {
        'background-color': 'white',
        'white-space': 'pre',
        }
     },

    {"headerName": "Comparator", 
     "field": "Reference",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
      #   'background-color': '#ffc1078a',
      #   'color':'#04800f',
        'white-space': 'pre',
        'font-weight':'bold',
        'border-right': 'solid 0.8px'
        }
     },
     {
        'headerName': 'Pasi90',
        'headerClass': 'center-aligned-group-header',
        "resizable": False,
        'suppressStickyLabel': True,
        'children': [
            {'field': 'RR', 
             'headerName': 'RR',
             "headerComponent": "HeaderWithIcon", 
             "suppressHeaderMenuButton": True},
            # {'field': 'ab_out1', 'headerName': 'Absoute',
            #  'cellStyle': {'line-height': 'normal'}
            #  },
            {'field': 'Certainty_out1',
             "suppressHeaderMenuButton": True, 
             'headerName': 'Certainty',
             "resizable": False,
             "headerComponent": "HeaderWithIcon",
             "tooltipField": 'Certainty_out1',
             "tooltipComponentParams": { "color": '#d8f0d3'},
             "tooltipComponent": "CustomTooltip2",
             'cellStyle':{
                        "styleConditions": [
                        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},   
                        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
                        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
                    ]}
             },
        ]
    },
    {
        'headerName': 'SAE',
        'headerClass': 'center-aligned-group-header',
        "resizable": False,
        'suppressStickyLabel': True,
        'children': [
            {'field': 'RR_out2', 
             'headerName': 'RR',
             "headerComponent": "HeaderWithIcon",
             "suppressHeaderMenuButton": True},
            # {'field': 'ab_out2', 'headerName': 'Absoute',
            #  'cellStyle': {'line-height': 'normal'}},
            {'field':'Certainty_out2', 
             "suppressHeaderMenuButton": True,
             'headerName': 'Certainty',
             "headerComponent": "HeaderWithIcon",
             "tooltipField": 'Certainty_out2',
             "tooltipComponentParams": { "color": '#d8f0d3'},
             "tooltipComponent": "CustomTooltip3",
              'cellStyle':{
                        "styleConditions": [
                        {"condition": "params.value == 'High'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},   
                        {"condition": "params.value == 'Low'", "style": {"backgroundColor": "#B85042", **style_certainty}},
                        {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
                    ]}
             },
        ]
    },
]

treat_compare_grid = dag.AgGrid(
    id="grid_treat_compare",
    className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=os.environ["AG_GRID_KEY"],
    columnDefs=ColumnDefs_treat_compare,
    rowData = df.to_dict("records"),
    dangerously_allow_code=True,
    dashGridOptions = {"rowHeight": 60},
    defaultColDef={
                    'filter':False,
                    "floatingFilter": False,
                    "resizable": False,
                    "wrapText": True, 
                    # 'autoHeight': True,
                    "enableRowGroup": False,
                    "enableValue": False,
                    "enablePivot": False,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                  'line-height': 'normal'
                                  },
                    "animateRows": False,
                    # "tooltipComponent": "CustomTooltip"
                    },
    columnSize="sizeToFit", 
    getRowId='params.data.index', 
    style={ "width": "100%",
           'height':f'{45.5 *30}px'
           }
)

############################# Modal Grid ####################################################


data_modal = pd.read_csv('db/psoriasis_wide_complete1.csv')
df_modal = pd.DataFrame(data_modal)
filtered_df = df_modal[((df_modal['treat1'] == 'ADA') & (df_modal['treat2'] == 'PBO')) |
                 ((df_modal['treat1'] == 'PBO') & (df_modal['treat2'] == 'ADA'))]
filtered_df = filtered_df[filtered_df['TE1'].notna()]
filtered_df['TE1_up'] = filtered_df['TE1'] + 1.96*filtered_df['seTE1']
filtered_df['TE1_low'] = filtered_df['TE1'] - 1.96*filtered_df['seTE1']
filtered_df['RR'] = np.exp(filtered_df['TE1'])
filtered_df['RR_up'] = np.exp(filtered_df['TE1_up'])
filtered_df['RR_low'] = np.exp(filtered_df['TE1_low'])

for index, row in filtered_df.iterrows():
    if row['treat1'] == 'PBO' and row['treat2'] == 'ADA':
        # Swap treat1 and treat2
        filtered_df.at[index, 'treat1'], filtered_df.at[index, 'treat2'] = row['treat2'], row['treat1']
        filtered_df.at[index, ['RR_up', 'RR_low']] = filtered_df.loc[index, ['RR_low', 'RR_up']].values
        # Invert the values for the specified columns
        for col in ['TE1', 'TE1_up', 'TE1_low', 'RR', 'RR_up', 'RR_low']:
            filtered_df.at[index, col] = 1 / row[col]

# # Calculate the 'ab_diff' column in a vectorized way
# abrisk = (20 * filtered_df['RR'] - 20).astype(int)

# # Use a condition to assign the appropriate text based on the value of 'abrisk'
# filtered_df['ab_diff'] = abrisk.apply(lambda x: f"{x} more per 1000" if x > 0 else f"\n{abs(x)} less per 1000")

filtered_df['RR_ci'] = filtered_df.apply(
    lambda row: f"{round(row['RR'], 2)}\n({round(row['RR_low'], 2)} to {round(row['RR_up'], 2)})", 
    axis=1)
# # Replace values in the 'bias' column
filtered_df['bias'] = filtered_df['bias'].replace({'L': 'Low', 'M': 'Moderate', 'H': 'High'})

filtered_df['ntc'] = 'NTC00001'
filtered_df['link'] = 'https://www.nejm.org/doi/10.1056/NEJMoa1314258?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%20%200www.ncbi.nlm.nih.gov'

modal_treat_compare = [
   
    {"headerName": "Study", 
     "field": "studlab",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        },
     "cellRenderer": "StudyLink",
     },
     
   #   {"headerName": "NTC", 
   #   "field": "ntc",
   #   "suppressHeaderMenuButton": True,
   #   "editable": False,
   #   "resizable": False,
   #   'cellStyle': {
   #      'background-color': '#ffecb3',
   #      }
   #   },

     {"headerName": "RR", 
     "field": "RR_ci",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },
     
     {"headerName": "Study size", 
     "field": "sample_size",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },

     {"headerName": "Age", 
     "field": "age",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },

     {"headerName": "BMI", 
     "field": "bmi",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },

     {"headerName": "Weight", 
     "field": "weight",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },
     
     {"headerName": "Risk of bias", 
     "field": "bias",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle':{
                "styleConditions": [
                {"condition": "params.value == 'High'", "style": {"backgroundColor": "#B85042", **style_certainty}},   
                {"condition": "params.value == 'Low'", "style": {"backgroundColor": "rgb(90, 164, 105)", **style_certainty}},
                {"condition": "params.value == 'Moderate'", "style": {"backgroundColor": "rgb(248, 212, 157)", **style_certainty}},       
                    ]}
     },
]



modal_compare_grid = dag.AgGrid(
    id="modal_treat_compare",
    # className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=os.environ["AG_GRID_KEY"],
    columnDefs=modal_treat_compare,
    rowData = filtered_df.to_dict("records"),
    dangerously_allow_code=True,
    dashGridOptions = {"rowHeight": 60},
    suppressDragLeaveHidesColumns=False,
    defaultColDef={
                    'filter':True,
                    "floatingFilter": False,
                    "resizable": False,
                    "wrapText": True, 
                    # 'autoHeight': True,
                    "enableRowGroup": False,
                    "enableValue": False,
                    "enablePivot": False,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                  'line-height': 'normal'
                                  },
                    "animateRows": False,
                    # "tooltipComponent": "CustomTooltip"
                    },
    columnSize="autoSize", 
    getRowId='params.data.studlab', 
    style={ 
        # "width": "100%",
        #    'height':f'{45.5 *30}px'
           }
)




############################# Full names Grid ####################################################
data_fullname = pd.read_csv('db/skt/fullname.csv')
fullname_df = pd.DataFrame(data_fullname)

modal_fullname_column = [
   
     {"headerName": "Abbreviation", 
     "field": "Abbreviation",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     },

     {"headerName": "Treatment", 
     "field": "Treatment",
     "suppressHeaderMenuButton": True,
     "editable": False,
     "resizable": False,
     'cellStyle': {
        'background-color': '#ffecb3',
        }
     }
]



modal_fullname_grid = dag.AgGrid(
    id="modal_fullname",
    # className="ag-theme-alpine color-fonts",
    enableEnterpriseModules=True,
    licenseKey=os.environ["AG_GRID_KEY"],
    columnDefs=modal_fullname_column,
    rowData = fullname_df.to_dict("records"),
    dangerously_allow_code=True,
    dashGridOptions = {"rowHeight": 60},
    suppressDragLeaveHidesColumns=False,
    defaultColDef={
                    'filter':True,
                    "floatingFilter": False,
                    "resizable": False,
                    "wrapText": True, 
                    # 'autoHeight': True,
                    "enableRowGroup": False,
                    "enableValue": False,
                    "enablePivot": False,
                    'cellStyle': {'white-space': 'pre',
                                  'display': 'grid',
                                  'text-align': 'center',
                                  'align-items': 'center',
                                  'line-height': 'normal'
                                  },
                    "animateRows": False,
                    # "tooltipComponent": "CustomTooltip"
                    },
    columnSize="autoSize", 
    getRowId='params.data.studlab', 
    style={ 
        # "width": "100%",
        #    'height':f'{45.5 *30}px'
           }
)

