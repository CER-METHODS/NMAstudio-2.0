import dash_ag_grid as dag
import os
import pandas as pd
import itertools
import numpy as np
import dash_iconify
import json
import dash_ag_grid as dag
import os
# Get AG Grid license key with fallback for development
AG_GRID_KEY = os.environ.get("AG_GRID_KEY", "")


# Empty placeholder DataFrames for initial layout
# Real data will be populated from STORAGE via callbacks
# df = pd.DataFrame(
#     {
#         "Treatment": [],
#         "Reference": [],
#         "RR": [],
#         "CI_lower": [],
#         "CI_upper": [],
#         "RR_out2": [],
#         "CI_lower_out2": [],
#         "CI_upper_out2": [],
#         "Certainty_out1": [],
#         "Certainty_out2": [],
#         "switch": [],
#         "index": [],
#     }
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
df = np.round(df,2)

df['RR'] = df.apply(lambda row: f"{row['RR']}\n({row['CI_lower']} to {row['CI_upper']})", axis=1)

df['RR_out2'] = df.apply(lambda row: f"{row['RR_out2']}\n({row['CI_lower_out2']} to {row['CI_upper_out2']})", axis=1)


df_origin = df.copy()

style_certainty = {
    "white-space": "pre",
    "display": "grid",
    "text-align": "center",
    "alignItems": "center",
    "border-left": "solid 0.8px",
}

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
                    'suppressHeaderMenuButton': True,
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

# Empty placeholder DataFrame for modal grid
# Real data will be populated from STORAGE via callbacks
filtered_df = pd.DataFrame(
    {
        "studlab": [],
        "RR_ci": [],
        "sample_size": [],
        "age": [],
        "bmi": [],
        "weight": [],
        "bias": [],
        "link": [],
        "ntc": [],
    }
)

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
# Empty placeholder DataFrame for fullname grid
# Real data will be populated from STORAGE via callbacks
fullname_df = pd.DataFrame(
    {
        "Abbreviation": [],
        "Treatment": [],
    }
)

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

