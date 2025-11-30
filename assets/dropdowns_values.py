####### contains all lists of values (except for data variables) for the app dropdowns #######
from assets.modal_values import *


Dropdown_nodesize = dbc.DropdownMenu(
    label="Node size", direction="right", size="md",
    children=[dbc.DropdownMenuItem("Default", id='dd_nds_default'),
              dbc.DropdownMenuItem("Tot randomized", id='dd_nds_tot_rnd'),
              html.Div(id='dd_nds', style={'display': 'none'}),
              ],
)


Dropdown_nodecolor = dbc.DropdownMenu(
    label="Node colour", direction="right",size="md",
    children=[dbc.DropdownMenuItem("Default", id='dd_nclr_default'),
              dbc.DropdownMenuItem("Risk of Bias", id='dd_nclr_rob'),
              dbc.DropdownMenuItem("By class", id='dd_nclr_class'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_dd_nclr_input'), # Calls up Modal
              html.Div(id='dd_nclr', style={'display': 'none'}),
              ]
)


Dropdown_edgecolor = dbc.DropdownMenu(
    label="Edge colour", direction="right", size="md",
    children=[dbc.DropdownMenuItem("Default", id='dd_edge_default'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_dd_eclr_input'), # Calls up Modal
              dbc.DropdownMenuItem("Add label", id='dd_edge_label'),
              html.Div(id='dd_eclr', style={'display': 'none'}),
              ]
)


Dropdown_graphlayout_inner = dbc.DropdownMenu(
    label="Graph Layout",size="md",
    children=[
        dbc.DropdownMenuItem(item, id=f'dd_ngl_{item.lower()}')
        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                      'Dagre', 'Klay']
             ] + [html.Div(id='graph-layout-dropdown', style={'display': 'none'})
             ],
    direction="right",
)

Dropdown_edgesize = dbc.DropdownMenu(
    label="Edge size", direction="right",size="md",
    children=[
        dbc.DropdownMenuItem("Number of studies", id='dd_egs_tot_rnd'),
        dbc.DropdownMenuItem("No size", id='dd_egs_default'),
        html.Div(id='dd_egs', style={'display': 'none'}),
    ],
)

Dropdown_export = dbc.DropdownMenu(
    label="Export options", direction="right",size="md",
    children=[
        dbc.DropdownMenuItem("as svg", id='svg-option'),
        dbc.DropdownMenuItem("as png", id='png-option'),
        dbc.DropdownMenuItem("as jpeg", id='jpeg-option'),  ##default option

        html.Div(id='exp-options', style={'display': 'none'}),
    ],
)
Dropdown_graphlayout = dbc.DropdownMenu(
    label="Graph Options",
    children=[Dropdown_graphlayout_inner, Dropdown_export, Dropdown_edgesize, Dropdown_nodesize, Dropdown_nodecolor, Dropdown_edgecolor],
    toggle_style={'background-color':'#00ab9c','color':'white'},
)





################################# KT TOOL GRAPH OPTIONS #############################################

KT_Dropdown_nodesize = dbc.DropdownMenu(
    label="Node size", direction="right", size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt_nds_default'),
              dbc.DropdownMenuItem("Tot randomized", id='kt_nds_tot_rnd'),
              html.Div(id='kt_nds', style={'display': 'none'}),
              ],
)


KT_Dropdown_nodecolor = dbc.DropdownMenu(
    label="Node colour", direction="right",size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt_nclr_default'),
              dbc.DropdownMenuItem("Risk of Bias", id='kt_nclr_rob'),
              dbc.DropdownMenuItem("By class", id='kt_nclr_class'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_kt_nclr_input'), # Calls up Modal
              html.Div(id='kt_nclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


KT_Dropdown_edgecolor = dbc.DropdownMenu(
    label="Edge colour", direction="right", size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt_edge_default'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_kt_eclr_input'), # Calls up Modal
              dbc.DropdownMenuItem("Add label", id='kt_edge_label'),
              html.Div(id='kt_eclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


KT_Dropdown_graphlayout_inner = dbc.DropdownMenu(
    label="Graph Layout",size="sm",
    children=[
        dbc.DropdownMenuItem(item, id=f'kt_ngl_{item.lower()}')
        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                      'Dagre', 'Klay']
             ] + [html.Div(id='kt-graph-layout-dropdown', style={'display': 'none'})
             ],
    direction="right",
)

KT_Dropdown_edgesize = dbc.DropdownMenu(
    label="Edge size", direction="right",size="sm",
    children=[
        dbc.DropdownMenuItem("Number of studies", id='kt_egs_tot_rnd'),
        dbc.DropdownMenuItem("No size", id='kt_egs_default'),
        html.Div(id='kt_egs', style={'display': 'none'}),
    ],
)


KT_Dropdown_graphlayout = dbc.DropdownMenu(
    label="Graph Options",
    children=[KT_Dropdown_graphlayout_inner, KT_Dropdown_edgesize, KT_Dropdown_nodesize, KT_Dropdown_nodecolor, KT_Dropdown_edgecolor],
    toggle_style={'background-color':'#00ab9c','color':'white'},
)


################################# KT TOOL - Advacnded GRAPH OPTIONS #############################################

KT2_Dropdown_nodesize = dbc.DropdownMenu(
    label="Node size", direction="right", size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt2_nds_default'),
              dbc.DropdownMenuItem("Tot randomized", id='kt2_nds_tot_rnd'),
              html.Div(id='kt2_nds', style={'display': 'none'}),
              ],
)


KT2_Dropdown_nodecolor = dbc.DropdownMenu(
    label="Node colour", direction="right",size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt2_nclr_default'),
              dbc.DropdownMenuItem("Risk of Bias", id='kt2_nclr_rob'),
              dbc.DropdownMenuItem("By class", id='kt2_nclr_class'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_kt2_nclr_input'), # Calls up Modal
              html.Div(id='kt2_nclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


KT2_Dropdown_edgecolor = dbc.DropdownMenu(
    label="Edge colour", direction="right", size="sm",
    children=[dbc.DropdownMenuItem("Default", id='kt2_edge_default'),
              dbc.DropdownMenuItem("Custom selection", id='open_modal_kt2_eclr_input'), # Calls up Modal
              dbc.DropdownMenuItem("Add label", id='kt2_edge_label'),
              html.Div(id='kt2_eclr', style={'display': 'none'}),
              ], style={'display': 'inline-block',}
)


KT2_Dropdown_graphlayout_inner = dbc.DropdownMenu(
    label="Graph Layout",size="sm",
    children=[
        dbc.DropdownMenuItem(item, id=f'kt2_ngl_{item.lower()}')
        for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                      'Dagre', 'Klay']
             ] + [html.Div(id='kt2-graph-layout-dropdown', style={'display': 'none'})
             ],
    direction="right",
)

KT2_Dropdown_edgesize = dbc.DropdownMenu(
    label="Edge size", direction="right",size="sm",
    children=[
        dbc.DropdownMenuItem("Number of studies", id='kt2_egs_tot_rnd'),
        dbc.DropdownMenuItem("No size", id='kt2_egs_default'),
        html.Div(id='kt2_egs', style={'display': 'none'}),
    ],
)


KT2_Dropdown_graphlayout = dbc.DropdownMenu(
    label="Graph Options",
    children=[KT2_Dropdown_graphlayout_inner, KT2_Dropdown_edgesize, KT2_Dropdown_nodesize, KT2_Dropdown_nodecolor, KT2_Dropdown_edgecolor],
    toggle_style={'background-color':'#00ab9c','color':'white', 'height':'30px'},
)

