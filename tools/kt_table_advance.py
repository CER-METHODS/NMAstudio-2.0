import dash_ag_grid as dag
import os
import pandas as pd
import numpy as np
from tools.functions_skt_forestplot import __skt_options_forstplot, __skt_mix_forstplot

df_standard = pd.DataFrame(
    {
        "Reference": [],
        "pscore": [],
        "risk_range": [],
        "risk": [],
        "rationality": [],
        "Scale_lower": [],
        "Scale_upper": []
    }
)

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
    rowData = df_standard.to_dict("records"),
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