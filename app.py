# Title     :  Dash NMA app
# Objective :  visualisation of network meta-analysis based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
import secrets
# --------------------------------------------------------------------------------------------------------------------#
import warnings
warnings.filterwarnings("ignore")
# --------------------------------------------------------------------------------------------------------------------#
import dash
import time
import itertools
import json
import dash_core_components as dcc
from dash import clientside_callback
from dash.dependencies import Input, Output, State, ALL
from dash_extensions.snippets import send_file
from tools.utils import *
from tools.PATHS import SESSION_PICKLE, get_session_pickle_path, TODAY, SESSION_TYPE, get_new_session_id
from tools.layouts import *
from tools.skt_layout import *
from tools.functions_modal_SUBMIT_data import __modal_SUBMIT_button_new, __data_modal, __data_trans
from tools.functions_NMA_runs import __modal_submit_checks_DATACHECKS,__modal_submit_checks_NMA_new,__modal_submit_checks_PAIRWISE_new, __modal_submit_checks_LT_new, __modal_submit_checks_FUNNEL_new
from tools.functions_handle_nma_processing import __handle_nma_processing__
from tools.functions_ranking_plots import __ranking_plot
from tools.functions_funnel_plot import __Tap_funnelplot, __Tap_funnelplot_normal
from tools.functions_nmaforest_plot import __TapNodeData_fig, __TapNodeData_fig_bidim
from tools.functions_pairwise_plots import __update_forest_pairwise
from tools.functions_boxplots import __update_boxplot, __update_scatter
from tools.functions_project_setup import __update_options, __second_options, __effect_modifier_options,__selectbox1_options, __outcomes_type,__variable_selection,__primaryout_selection
from tools.functions_netsplit import __netsplit
from tools.functions_build_league_data_table import  __update_output_new,__update_output_bothout
from tools.functions_generate_stylesheet import __generate_stylesheet
from tools.functions_export import __generate_xlsx_netsplit, __generate_xlsx_league, __generate_csv_consistency
from tools.functions_show_forest_plot import __show_forest_plot
from tools.functions_skt_boxplot import __show_boxplot
from tools.functions_skt_others import __generate_skt_stylesheet, __generate_skt_stylesheet2
from dash import ctx, no_update
# --------------------------------------------------------------------------------------------------------------------#
# create_sessions_folders()
# clean_sessions_folders()

# Load extra layouts
cyto.load_extra_layouts()
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 5000)


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                # external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
# app.config.suppress_callback_exceptions = True
# app.scripts.append_script({'external_url':'https://NMAstudio.com/assets/gtag.js'})
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y7P5T0R3ML"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-Y7P5T0R3ML');
        </script>
        {%metas%}
        <title>NMAstudio</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div></div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
'''

def get_new_layout():
    SESSION_ID = get_new_session_id()
    return html.Div([dcc.Location(id='url', refresh=False),
                     dcc.Interval(
                            id='nma-task-poller',
                            interval=2000,  # milliseconds, e.g., 2 seconds
                            n_intervals=0,
                            disabled=False  # you can start with polling disabled if needed
                        ),
                     html.Div(id='page-content', style={
                         'background-color':'#fff'
                        #  'background-color':'#5c7780'
                         }),
                     dcc.Store(id='consts_STORAGE',  data={'today': TODAY, 'session_ID': SESSION_ID},
                               storage_type='memory',
                               ),
                    dcc.Store(id='nma-task-store', storage_type='memory')
                     ])
server = app.server
app.layout = get_new_layout()


# ------------------------------ app interactivity ----------------------------------#

#####################################################################################
################################ MULTIPAGE CALLBACKS ################################
#####################################################################################

HOMEPAGE = Homepage()
RealHomepage = realHomepage()
SKTPAGE = Sktpage()

# SKT = Sktpage()



# Update the index

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/home':  return RealHomepage
    elif pathname == '/results':  return HOMEPAGE
    # elif pathname == '/skt': return SKTPAGE,
    # elif pathname == '/doc': return doc_layout
    # elif pathname == '/news': return news_layout

    else:  return RealHomepage


# @app.callback(
#     Output('skt_page_content','children'),
#     Input('expert_profile','n_clicks'),
#     Input('nonexpert_profile','n_clicks'),
#     State('skt_page_content','children'),
# )
# def clear_treat(click_expert,click_nonexpert,children):
#     if click_expert:
#         children = [Navbar(), skt_layout()]
#         return children
#     elif click_nonexpert:
#         children = [Navbar(), skt_nonexpert()]
#         return children
#     else:
#         return children

@app.callback(
     Output('skt_sub_content','children'),
    Input('toggle_grid_select','value'),
    State('skt_sub_content','children')
)
def display_grid(value, children):
    if value:
        children = [skt_layout()]
    
    else:
        children = [skt_nonexpert()]
    return children


# @app.callback(
#     Output('skt_profile_page','style'),
#     Output('sky_expert_page','style'),
#     Output('skt_nonexpert_page','style'),
#     Input('expert_profile','n_clicks'),
#     Input('nonexpert_profile','n_clicks'),
# )
# def clear_treat(click_expert,click_nonexpert):
#     style_display = {'display':'block'}
#     style_nondisplay = {'display':'none'}
#     if click_expert:
#         return style_nondisplay,style_display, style_nondisplay
#     elif click_nonexpert:
#         return style_nondisplay,style_nondisplay,style_display
#     else:
#         return style_display,style_nondisplay, style_nondisplay


# @app.callback(
#     Output('pass_model','is_open'),
#     Output('skt_page_content','children'),
#     Input('password_ok','n_clicks'),
#     Input('password','value'),
#     State('pass_model','is_open'),
#     State('skt_page_content','children'),
# )
# def clear_treat(click, password, pass_model, children):
#     if password =='777' and click:
#         children = [Navbar(), skt_home(), skt_layout(), skt_nonexpert()]
#         return not pass_model, children
#     else:
#         return pass_model, children





@app.callback([Output('result_page', 'style'),
              Output('upload_page', 'style'),],
              [Input('test_upload', 'n_clicks_timestamp'),
               Input('back_plot', 'n_clicks_timestamp'),
               Input('submit_modal_data','n_clicks_timestamp')
               ]
               )
def result_page(click, click_back,click_trans):
    if ctx.triggered_id == "back_plot":
        return {'display':'grid'}, {'display':'none'}

    if ctx.triggered_id == "test_upload":
        return {'display':'none'}, {'display':'grid'}
    
    if ctx.triggered_id == "submit_modal_data":
        return {'display':'grid'}, {'display':'none'}

    return no_update, no_update





@app.callback(Output('homepage-link', 'active'),
              [Input('url', 'pathname')])
def set_homepage_active(pathname):
    return pathname == '/home'

@app.callback(Output('docpage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/doc'

@app.callback(Output('newspage-link', 'active'), [Input('url', 'pathname')])
def set_docpage_active(pathname):
    return pathname == '/news'



#####################################################################################
#####################################################################################
################## -------- ALL PLOTS/TABLES CALLBACKS --------- ####################
#####################################################################################
#####################################################################################

### ---------------- PROJECT SETUP --------------- ###
@app.callback(Output("second-selection", "children"),
              [Input("dropdown-format", "value"),
               Input("dropdown-outcome1", "value"),
               Input("dropdown-outcome2", "value")],
              [State('datatable-upload', 'contents'),
              State('datatable-upload', 'filename')]
             )
def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
    return __update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)

@app.callback([Output("upload_selection_second", "children"),
              Output("arrow_step2", "style")
              ],
              [Input("radio-format", "value"),
               Input("radio-outcome1", "value"),
               Input("radio-outcome2", "value")],
              [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename):
    return __second_options(search_value_format, search_value_outcome1, search_value_outcome2, contents, filename)



@app.callback([Output("outcomes_primary", "children"),
              Output("arrow_step_4", "style"),
              Output("select-out-primary", "style")
              ],
              [Input("number-outcomes", "value"),
               Input("num_outcomes_button", "n_clicks"),
               ]
             )
def update_options(number_outcomes, click):
    return __primaryout_selection(number_outcomes,click)



@app.callback([Output("outcomes_type", "children"),
              Output("arrow_step_primary", "style"),
              Output("select-out-type", "style")
              ],
              [Input("number-outcomes", "value"),
               Input({'type': 'outcomeprimary', 'index': ALL}, "value"),
               Input({'type': 'noprimary', 'index': ALL}, "value"),
               ]
             )
def update_options(number_outcomes, primary_out, noprimary):
    return __outcomes_type(number_outcomes,primary_out, noprimary)







@app.callback([Output("variable_selection", "children"),
              Output("arrow_step_5", "style"),
              Output("select_variables", "style"),
              ],
              [Input("number-outcomes", "value"),
               Input({'type': 'outcometype', 'index': ALL}, "value"),
               Input('radio-format', 'value')
               ],
               [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(number_outcomes, outcometype, data_format, contents, filename):
    return __variable_selection(number_outcomes,outcometype,data_format,contents, filename)






@app.callback(
    [Output({'type': 'outcomebutton', 'index': ALL}, "disabled")],
    [
        Input("number-outcomes", "value"),
        Input({'type': 'effectselectors', 'index': ALL}, "value"),
        Input({'type': 'directionselectors', 'index': ALL}, "value"),
        Input({'type': 'variableselectors', 'index': ALL}, "value")
    ]
)
def next_outcome(number_outcomes, effect, direction, variables):
    if number_outcomes and effect:
        number_outcomes = int(number_outcomes)
        disables = [True] * (number_outcomes)  # Initialize with True for all outcomes
        for i in range(number_outcomes):
            if effect[i] and direction[i] and variables[i]:
                disables[i] = False  # Enable the outcome button if all conditions are met
        disables[number_outcomes-1]= True
        return [disables]
    return [[True] * number_outcomes]
                
             




@app.callback(
    [Output({'type': 'displayvariable', 'index': ALL}, "style")],
    [Input("number-outcomes", "value"),
     Input({'type': 'outcomebutton', 'index': ALL}, "n_clicks"),
     Input({'type': 'outcomeprevious', 'index': ALL}, "n_clicks")
     ],
    [State({'type': 'displayvariable', 'index': ALL}, "style")]
)
def next_outcome(number_outcomes, click, click_previous,style):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if number_outcomes:
        number_outcomes = int(number_outcomes)
        if number_outcomes > 0:
            style = [{'display': 'grid' if i==0 else 'none'} for i in range(number_outcomes)]
            for i in range(number_outcomes-1):    
                if click[i]>0 and "outcomebutton" in changed_id and f'{i}' in changed_id:
                    style = [{'display': 'none'} for _ in range(number_outcomes)]
                    style[i]= {'display': 'none'}
                    style[i+1] = {'display': 'grid'}
            
            for i in range(1,number_outcomes):
                if click_previous[i]>0 and "outcomeprevious" in changed_id and f'{i}' in changed_id:
                    style = [{'display': 'none'} for _ in range(number_outcomes)]
                    style[i-1]= {'display': 'grid'}
                    style[i] = {'display': 'none'}
            return [style]
    
    return style




@app.callback([Output("select-box-1", "children"),
              Output("arrow_step_2", "style"),
              Output("select-overall", "style")],
              [Input("radio-format", "value")],
              [State('datatable-upload2', 'contents'),
              State('datatable-upload2', 'filename')]
             )
def update_options(search_value_format, contents, filename):
    return __selectbox1_options(search_value_format,contents, filename)


@app.callback([Output("number-outcomes-input", "style"),
              Output("arrow_step_3", "style")],
              Input("radio-format", "value"),
              Input({'type': 'dataselectors_1', 'index': ALL}, 'value')
              )
def modal_ENABLE_UPLOAD_button(format,dataselectors):
    if format == 'long':
        idx = 2
    else: idx = 3
    
    show_style = {'display': 'grid', 'justify-content': 'center'}
    hide_style = {'display': 'none', 'justify-content': 'center'}

    filtered_values = [val for i,val in enumerate(dataselectors) if i != idx]
    
    if len(filtered_values):
        if all(filtered_values):
            return show_style, show_style
        else:
            return hide_style, hide_style
    else:
        return hide_style, hide_style





@app.callback(
        Output('num_outcomes_button', 'disabled'),
        Input('number-outcomes', 'value')
)
def enable(value):
    if value:
        return False
    return True



@app.callback(Output("select_effect_modifier", "children"),
            #   [Input("radio-format", "value")],
              [Input('datatable-upload2', 'contents'),
              Input('datatable-upload2', 'filename')]
             )
def update_options(contents, filename):
    return __effect_modifier_options(contents, filename)






######## second instruction icon showup############
@app.callback(Output("queryicon-studlb","style"),
              Output("queryicon-year","style"),
              Output("queryicon-rob","style"),
              Input("dropdown-format", "value"),
              Input("dropdown-outcome1", "value"))

def is_secondicon_show(search_value_format,search_value_outcome1):
    show_studlb={'display': 'block'}
    donotshow_studlb={'display': 'none'}
    if search_value_format and search_value_outcome1 is not None:
        return show_studlb, show_studlb, show_studlb
    else:
        return donotshow_studlb, donotshow_studlb, donotshow_studlb




#update filename DIV and Store filename in Session
# @app.callback([Output("queryicon-outcome2", "style"),
#                Output("dropdowns-DIV", "style"),
#                Output("uploaded_datafile", "children"),
#                Output("datatable-filename-upload","data"),
#                ],
#                [Input('datatable-upload', 'filename')]
#               )
# def is_data_file_uploaded(filename):
#     show_outcome2_icon = {'display': 'block'}
#     show_DIV_style = {'display': 'inline-block', 'margin-bottom': '0px'}
#     donot_show_DIV_style = {'display': 'none', 'margin-bottom': '0px'}
#     donotshow_outcome2_icon = {'display': 'none'}
#     if filename:
#         return show_outcome2_icon, show_DIV_style, filename or '', filename
#     else:
#         return donotshow_outcome2_icon, donot_show_DIV_style, '', filename

@app.callback(
        Output('protocol_link_button', 'disabled'),
        Input('protocol-link', 'value')
)
def enable(value):
    if value:
        return False
    return True



@app.callback(
    [
        Output("upload_original_data", "style"),
        Output("arrow_protocol", "style")
    ],
    [
        Input("protocol-link", "value"),
        Input("protocol_link_button", "n_clicks"),
        Input("skip_link_button", "n_clicks")
    ]
)
def toggle_upload_display(value, link_clicks, skip_clicks):
    show_style = {'display': 'grid', 'justify-content': 'center'}
    hide_style = {'display': 'none', 'justify-content': 'center'}
  
    if (value and link_clicks) or (skip_clicks):
        return show_style, show_style
    else:
        return hide_style, hide_style



@app.callback(
               Output("show_protocol_link", "href"),
               Input('protocol-link', 'value'),
               Input('submit_modal_data', 'n_clicks'),
               State("show_protocol_link", "href"),   
              )
def is_data_file_uploaded(value,click, link):
    if not click:
        return link
    elif value and click:
        return value
    else: 
        return 'not provided'


@app.callback(
    Output("warning_message", "children"),
    [
        Input('protocol-link', 'value'),
        Input('submit_modal_data', 'n_clicks'),
        Input("radio-format", "value"),
        Input({'type': 'dataselectors_1', 'index': ALL}, 'value'),
    ],
    State('no_effect_modifier', 'value'),
    prevent_initial_call=True
)
def is_data_file_uploaded(protocol_value, click, format, variables, no_modifier):
    if not click:
        return ''

    idx = 2 if format == 'long' else 3
    rob = variables[idx]
    
    style = {
        'justify-self': 'center',
        'align-self': 'center',
        'white-space': 'pre',
        'font-size': 'medium',
        'color': 'red'
    }

    messages = []

    if not rob:
        messages.append('The risk of bias information is not provided.')

    if not protocol_value:
        messages.append('The protocol link is not provided.')

    if no_modifier:
        messages.append('The potential modifiers are not provided. The boxplots cannot be generated for transitivity check.')

    if messages:
        return html.Span(f"Warning!\n" + "\n".join(messages), style=style)
    
    return ''






@app.callback([
               Output("dropdowns-DIV2", "style"),
               Output("uploaded_datafile2", "children"),
               Output("arrow_step1", "style"),
               Output("datatable-filename-upload","data"),
               ],
               [Input('datatable-upload2', 'filename')]
              )
def is_data_file_uploaded(filename):
    show_DIV_style = {'display': 'grid', 'justify-content': 'center'}
    donot_show_DIV_style = {'display': 'none', 'justify-content': 'center'}
    arrow1_show={'display':'grid', 'justify-content': 'center'}
    arrow1_notshow={'display':'none', 'justify-content': 'center'}

    if filename:
        return  show_DIV_style, filename or '', arrow1_show, filename
    else:
        return  donot_show_DIV_style, '', arrow1_notshow, filename


### -------------------------- ALL CYTOSCAPE CALLBACKS  ------------------------------- ###

# @app.callback(Output("forest_outcome_select", "options"),
#               Output("forestpaire_outcome_select", "options"),
#               Output("league_outcome_select", "options"),
#               Output("consistency_outcome_select", "options"),
#               Output("funnel_outcome_select", "options"),
#               Output("biforest_outcome_select1", "options"),
#               Output("biforest_outcome_select2", "options"),
#               Output("ranking_outcome_select1", "options"),
#               Output("ranking_outcome_select2", "options"),
#               Input("number-outcomes", "value"),
#               Input({'type': 'nameoutcomes', 'index': ALL}, "value"),
#               State("forest_outcome_select", "options")
#              )

# def update_options(number_outcomes, nameoutcomes, options_var):
#     out_names = ['PASI90',"Death"]
#     if not nameoutcomes or not all(nameoutcomes):
#         if number_outcomes:
#             number_outcomes = int(number_outcomes)
#             options_var = [{'label': f'outcome{i+1}', 'value': i} for i in range(number_outcomes)]
#             return (options_var,) * 9
#         options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
#         return (options_var,) * 9
    
#     if number_outcomes:
#         number_outcomes = int(number_outcomes)
#         options_var = [{'label': f'{nameoutcomes[i]}', 'value': i} for i in range(number_outcomes)]
#         return (options_var,) * 9
    
#     options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
#     return (options_var,) * 9

@app.callback(
              Output("_outcome_select", "options"),
            #   Output("biforest_outcome_select1", "options"),
              Output("biforest_outcome_select2", "options"),
            #   Output("ranking_outcome_select1", "options"),
              Output("ranking_outcome_select2", "options"),
              Input("number-outcomes", "value"),
              Input({'type': 'nameoutcomes', 'index': ALL}, "value"),
              State("_outcome_select", "options")
             )

def update_options(number_outcomes, nameoutcomes, options_var):
    out_names = ['PASI90',"SAE"]
    if not nameoutcomes or not all(nameoutcomes):
        if number_outcomes:
            number_outcomes = int(number_outcomes)
            options_var = [{'label': f'outcome{i+1}', 'value': i} for i in range(number_outcomes)]
            return (options_var,) * 3
        options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
        return (options_var,) * 3
    
    if number_outcomes:
        number_outcomes = int(number_outcomes)
        options_var = [{'label': f'{nameoutcomes[i]}', 'value': i} for i in range(number_outcomes)]
        return (options_var,) * 3
    
    options_var = [{'label': f'{out_names[i]}', 'value': i} for i in range(2)]
    return (options_var,) * 3


### --- update graph layout with dropdown: graph layout --- ###
@app.callback([Output('cytoscape', 'layout'),
               Output('modal-cytoscape', 'layout')],
              [Input('graph-layout-dropdown', 'children'),],
              prevent_initial_call=False)
def update_cytoscape_layout(layout):
    ctx = dash.callback_context
    if layout:
       return {'name': layout.lower(),'fit':True },{'name': layout.lower(), 'fit':True}
    
    return {'name': 'circle','fit':True },{'name': 'circle', 'fit':True}

### ----- update graph layout on node click ------ ###
@app.callback([Output('cytoscape', 'stylesheet'),
               Output('modal-cytoscape', 'stylesheet'),
               Output("net_download_activation", "data")
               ],
              [Input('cytoscape', 'tapNode'),
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'elements'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('dd_nclr', 'children'),
               Input('dd_eclr', 'children'),
               Input('node_color_input', 'value'),
               Input('edge_color_input', 'value'),
               Input('label_size_input', 'value'),
               Input('treat_name_input', 'value'),
               Input('dd_nds', 'children'),
               Input('dd_egs', 'children'),
               Input("btn-get-png", "n_clicks"),
               Input("btn-get-png-modal", "n_clicks"),
               Input("net_download_activation", "data")
               ]
              )
def generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, label_size,treat_name,dd_nds, dd_egs,
                        dwld_button, dwld_button2,net_download_activation):
    return __generate_stylesheet(node, slct_nodesdata, elements, slct_edgedata,
                        dd_nclr, dd_eclr, custom_nd_clr, custom_edg_clr, label_size,treat_name,dd_nds, dd_egs,
                        dwld_button, dwld_button2,net_download_activation)

### ----- save network plot as png ------ ###
@app.callback([Output("cytoscape", "generateImage"),
               Output("modal-cytoscape", "generateImage")],
               Input("net_download_activation", "data"),
               State('exp-options', 'children'),
               prevent_initial_call=True)
def get_image(net_download_activation, export):
    action = 'store'
    export_selection = export or 'as png'
    if net_download_activation:
        action = "download"
    return {'type': 'jpeg' if export_selection=='as jpeg' else ('png' if export_selection=='as png' else 'svg'),
            'action': action,
            'options': {  # 'bg':'#40515e',
            'scale': 3}}, {'type': 'jpeg' if export_selection=='as jpeg' else ('png' if export_selection=='as png' else 'svg'),
            'action': action,
            'options': {  # 'bg':'#40515e',
            'scale': 3}}

# ## ----- Update layout with slider ------ ###

@app.callback([Output('cytoscape', 'elements'),
               Output('modal-cytoscape', 'elements'),],
              [
               Input('net_data_STORAGE', 'data'),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('slider-year', 'value'),
               Input('_outcome_select', 'value'),
               Input('reset_project', 'n_clicks'),
            #    Input('node_size_input', 'value'),
               ])
def update_layout_year_slider(net_data, pw_data, slider_year, out_fun,reset_btn):
    
    YEARS_DEFAULT = np.array([1963, 1990, 1997, 2001, 2003, 2004, 2005, 2006, 2007, 2008, 2010,
                              2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
    years_dft_max = YEARS_DEFAULT.max()


    reset_btn_triggered = False
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    if 'reset_project.n_clicks' in triggered: reset_btn_triggered = True

    try:
        net_datajs = pd.read_json(net_data[0], orient='split')
    except:
        net_datajs = pd.read_json(net_data[0], orient='split', encoding = 'utf-8')
    
    outcome = out_fun 
    if outcome:
        outcome = int(outcome)
        net_data = pd.read_json(net_data[0], orient='split')
        net_datajs2 = net_data[net_data.year <= slider_year] if not reset_btn_triggered else net_data[net_data.year <= years_dft_max]
        elements = get_network_new(df=net_datajs2,i = outcome )

    else:
        net_datajs = net_datajs[net_datajs.year <= slider_year] if not reset_btn_triggered else net_datajs[net_datajs.year <= years_dft_max]
        elements = get_network_new(df=net_datajs, i = 0)


    return elements, elements

### ---------------------------------- FOREST PLOTS CALLBACKS ---------------------------------- ###

### ----- update node info on NMA forest plot  ------ ###
@app.callback(Output('tapNodeData-info', 'children'),
              [Input('cytoscape', 'selectedNodeData')])
def TapNodeData_info(data):
    if data:
        return 'Reference treatment: ', data[0]['label']
    else:
        return 'Click on a node to choose reference'


### ----- update node info on bidim forest plot  ------ ###
@app.callback(Output('tapNodeData-info-bidim', 'children'),
              [Input('cytoscape', 'selectedNodeData')],
              # prevent_initial_call=True
              )
def TapNodeData_info(data):
    if data:
        return 'Reference treatment selected: ', data[0]['label']
    else:
        return 'Click on a node to choose reference'

# @app.callback(Output('queryicon-forest', 'style'),
#               Input('cytoscape', 'selectedNodeData'))
# def showquer_forest(data):
#     if data:
#         return {'display': 'inline'}
#     else:
#         return {'display': 'none'}



### ----- update edge information on pairwise plot ------ ###
@app.callback(Output('tapEdgeData-info', 'children'),
              Input('cytoscape', 'selectedEdgeData'))
def TapEdgeData_info(data):
    if data:
        return 'Selected comparison: ', f"{data[0]['source'].upper()} vs {data[0]['target'].upper()}"
    else:
        return 'Click on an edge to display the associated  plot'


### - display information box - ###
@app.callback(Output('cytoscape-mouseTapEdgeData-output', 'children'),
              [Input('cytoscape', 'selectedEdgeData')])
def TapEdgeData(edge):
    if edge:
        n_studies = edge[0]['weight_lab']
        studies_str = f"{n_studies}" + (' studies' if n_studies > 1 else ' study')
        return f"{edge[0]['source'].upper()} vs {edge[0]['target'].upper()}: {studies_str}"
    else:
        return "Click on an edge to get information."


### ----- display forest plot on node click ------ ###
# @app.callback(Output('tapNodeData-fig', 'figure'),
#               Output('tapNodeData-fig', 'style'),
#               [Input('cytoscape', 'selectedNodeData'),
#                Input("toggle_forest_outcome", "value"),
#                Input("forest_data_STORAGE", "data"),
#                Input("forest_data_out2_STORAGE", "data"),
#                Input('tapNodeData-fig', 'style')
#                ],
#               State("net_data_STORAGE", "data")
#               )
# def TapNodeData_fig(data, outcome, forest_data, forest_data_out2,style,net_storage):
#     return __TapNodeData_fig(data, outcome, forest_data, forest_data_out2,style,net_storage)



@app.callback(Output('tapNodeData-fig', 'figure'),
              Output('tapNodeData-fig', 'style'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('_outcome_select', 'value'),
               Input("forest_data_STORAGE", "data"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('tapNodeData-fig', 'style'),
               Input('add_pi', 'value'),
               Input('add_tau2', 'value'),
               ],
              State("net_data_STORAGE", "data")
              )
def TapNodeData_fig(data, outcome_idx, forest_data, pw_forest_data, style, pi, add_tau, net_storage):
    return __TapNodeData_fig(data, outcome_idx, forest_data, pw_forest_data, style, pi, add_tau, net_storage)


### ----- display dibim forest plot on node click ------ ###
@app.callback(Output('tapNodeData-fig-bidim', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input('forest_data_STORAGE', 'data'),
               Input('_outcome_select', 'value'),
               Input('biforest_outcome_select2', 'value'),
               Input('_outcome_select', 'options'),
               Input({'type': 'directionselectors', 'index': ALL}, "value")
               ]
              )
def TapNodeData_fig_bidim(data, forest_data_store, out_idx1, out_idx2, options,directions):
    return __TapNodeData_fig_bidim(data, forest_data_store, out_idx1, out_idx2, options, directions)


### - figures on edge click: pairwise forest plots  - ###
@app.callback([Output('tapEdgeData-fig-pairwise', 'figure'),
              Output('tapEdgeData-fig-pairwise', 'style')],
              [Input('cytoscape', 'selectedEdgeData'),
               Input("_outcome_select", "value"),
               Input('forest_data_prws_STORAGE', 'data'),
               Input('tapEdgeData-fig-pairwise', 'style')],
              State("net_data_STORAGE", "data")
              )

def  update_forest_pairwise(edge, outcome_idx, forest_data_prws, style_pair, net_storage):
    return __update_forest_pairwise(edge, outcome_idx, forest_data_prws,style_pair,net_storage)



### ----------------------------------  TRANSITIVITY CALLBACK ---------------------------------- ###


@app.callback(Output('tapEdgeData-fig', 'figure'),
              [Input('box_vs_scatter', 'value'),
               Input('dropdown-effectmod', 'value'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE','data')])
def update_boxplot(scatter, value, edges, net_data):
    if scatter:
        return __update_scatter(value, edges, net_data)
    return __update_boxplot(value, edges, net_data)


### ----------------------------------  DATA TABLE, LEAGUE TABLE CALLBACKS ---------------------------------- ###


@app.callback([Output('datatable-upload-container', 'data'),
               Output('datatable-upload-container', 'columns'),
               Output('datatable-upload-container-expanded', 'data'),
               Output('datatable-upload-container-expanded', 'columns'),
               Output('league_table', 'children'),
               Output('modal_league_table_data', 'children'),
               Output('league_table_legend', 'children'),
               Output('modal_league_table_legend', 'children'),
               Output('rob_vs_cinema', 'value'),
               Output('rob_vs_cinema_modal', 'value'),
               Output('slider-year', 'min'),
               Output('slider-year', 'max'),
               Output('slider-year', 'marks'),
               Output('data_and_league_table_DATA', 'data'),
               Output('datatable-raw-container', 'data'),
               Output('datatable-raw-container', 'columns')
               ],
              [               
               Input('slider-year', 'value'),
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('net_data_STORAGE', 'data'),
               Input('raw_data_STORAGE', 'data'),
               Input('rob_vs_cinema', 'value'),
               Input('rob_vs_cinema_modal', 'value'),
               Input('league_table_data_STORAGE', 'data'),
               Input('cinema_net_data_STORAGE', 'data'),
               Input('data_and_league_table_DATA', 'data'),
               Input("forest_data_STORAGE", "data"),
               Input('reset_project', 'n_clicks'),
            #    Input('ranking_data_STORAGE','data'),
               Input('_outcome_select','value'),
                ],
               State('net_data_STORAGE', 'data'),
               State('raw_data_STORAGE', 'data'),
              prevent_initial_call=True)
def update_output(slider_value, store_node,store_edge,net_data, raw_data,toggle_cinema, toggle_cinema_modal,
                  league_table_data, cinema_net_data, data_and_league_table_DATA,
                  forest_data,  reset_btn,  outcome_idx, net_storage, raw_storage):
    return __update_output_new(slider_value, store_node,store_edge,net_data,raw_data, toggle_cinema, toggle_cinema_modal,
                  league_table_data, cinema_net_data, data_and_league_table_DATA,
                  forest_data,  reset_btn,  outcome_idx, net_storage,raw_storage)







@app.callback([
               Output('league_table_both', 'children'),
               Output('league_table_legend_both', 'children'),
               Output('rob_vs_cinema-both', 'value'),
               ],
              [               
               Input('cytoscape', 'selectedNodeData'),
               Input('cytoscape', 'selectedEdgeData'),
               Input('rob_vs_cinema-both', 'value'),
               Input('league_table_data_STORAGE', 'data'),
               Input('cinema_net_data_STORAGE2', 'data'),
               Input("forest_data_STORAGE", "data"),
               Input('reset_project', 'n_clicks'),
               Input({'type': 'outcomeprimary', 'index': ALL}, "value"),
                ],
               [State('net_data_STORAGE', 'data'),
               State('datatable-secondfile-upload-2', 'filename')],
              prevent_initial_call=True)
def update_output( store_node,store_edge,toggle_cinema,
                  league_table_data, cinema_net_data,
                  forest_data,  reset_btn,  outcome_idx,net_storage,filename_cinema2):
    return __update_output_bothout( store_node,store_edge,toggle_cinema,
                  league_table_data, cinema_net_data, forest_data,  reset_btn,  outcome_idx,net_storage,filename_cinema2)


### ---------------------------------- FUNNEL, CONSISTENCY, RANKING  CALLBACKS ---------------------------------- ###


#### ----- consistency table and netsplit table ----- ####

@app.callback([Output('netsplit_table-container', 'data'),
              Output('netsplit_table-container', 'columns'),
               Output('consistency-table', 'data'),
               Output('consistency-table', 'columns')],
              [Input('cytoscape', 'selectedEdgeData'),
               Input("_outcome_select", "value"),
               Input('net_split_data_STORAGE', 'data'),
               Input('consistency_data_STORAGE', 'data'),]
              )
def netsplit(edges, outcome_idx, net_split_data, consistency_data):
   return __netsplit(edges, outcome_idx, net_split_data, consistency_data)




### ----- upload CINeMA data file 1 ------ ###
# @app.callback([Output("cinema_net_data_STORAGE", "data"),
#                Output("file2-list", "children"),
#                ],
#               [Input('datatable-secondfile-upload', 'contents'),
#                Input('cinema_net_data_STORAGE', 'data')],
#               [State('datatable-secondfile-upload', 'filename')])
# def get_new_data_cinema1(contents, cinema_net_data, filename):
#     if contents is None:
#         # print(cinema_net_data[0])
#         cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
#         cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')

#         # print(cinema_net_data)
#     else:
#         cinema_net_data = parse_contents(contents, filename)
#     if filename is not None:
#         return [cinema_net_data.to_json(orient='split')], 'loaded'
#     else:
#         return [cinema_net_data1.to_json(orient='split'),cinema_net_data2.to_json(orient='split')], ''


@app.callback(
    [
        Output("cinema_net_data_STORAGE", "data"),
        Output("file2-list", "children"),
    ],
    [
        Input('datatable-secondfile-upload', 'contents'),
        Input('cinema_net_data_STORAGE', 'data')
    ],
    [State('datatable-secondfile-upload', 'filename')]
)
def get_new_data_cinema1(contents, cinema_net_data, filename):
    # Case 1: If no file is uploaded, use existing cinema_net_data
    if contents is None:
        try:
            # Ensure cinema_net_data exists and contains valid JSON
            if isinstance(cinema_net_data, list) and len(cinema_net_data) >= 2:
                cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
                cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')
                return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], ''
            else:
                return [], 'No valid data found in storage.'
        except Exception as e:
            return [], f"Error loading stored data: {str(e)}"
    
    # Case 2: If a file is uploaded, parse the contents
    else:
        try:
            cinema_net_data = parse_contents(contents, filename)
            return [cinema_net_data.to_json(orient='split')], 'File successfully loaded'
        except Exception as e:
            return [], f"Error processing uploaded file: {str(e)}"



@app.callback(
    [
        Output("cinema_net_data_STORAGE2", "data"),
        Output("file-list-out2", "children"),
    ],
    [
        Input('datatable-secondfile-upload-1', 'contents'),
        Input('datatable-secondfile-upload-2', 'contents'),
        Input('cinema_net_data_STORAGE2', 'data')
    ],
    [
        State('datatable-secondfile-upload-1', 'filename'),
        State('datatable-secondfile-upload-2', 'filename')
    ]
)
def get_new_data_cinema1(contents1, contents2, cinema_net_data, filename1, filename2):
    # Case 1: If no file is uploaded, use existing cinema_net_data
    if contents1 is None and contents2 is None:
        try:
            # Ensure cinema_net_data exists and contains valid JSON
            if isinstance(cinema_net_data, list) and len(cinema_net_data) >= 2:
                cinema_net_data1 = pd.read_json(cinema_net_data[0], orient='split')
                cinema_net_data2 = pd.read_json(cinema_net_data[1], orient='split')
                return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], ''
            else:
                return [], 'No valid data found in storage.'
        except Exception as e:
            return [], f"Error loading stored data: {str(e)}"
    
    # Case 2: If one file is uploaded and the other is not
    elif contents1 is not None and contents2 is None:
        try:
            cinema_net_data = parse_contents(contents1, filename1)
            return [cinema_net_data.to_json(orient='split')], 'File1 successfully loaded'
        except Exception as e:
            return [], f"Error processing uploaded file: {str(e)}"
    elif contents2 is not None and contents1 is None:
        try:
            cinema_net_data = parse_contents(contents2, filename2)
            return [cinema_net_data.to_json(orient='split')], 'File2 successfully loaded'
        except Exception as e:
            return [], f"Error processing uploaded file: {str(e)}"
    
    # Case 3: If both files are uploaded
    else:
        try:
            cinema_net_data1 = parse_contents(contents1, filename1)
            cinema_net_data2 = parse_contents(contents2, filename2)
            return [cinema_net_data1.to_json(orient='split'), cinema_net_data2.to_json(orient='split')], 'Files successfully loaded'
        except Exception as e:
            return [], f"Error processing uploaded files: {str(e)}"


### ----- update node info on funnel plot  ------ ###
@app.callback(Output('tapNodeData-info-funnel', 'children'),
              [Input('cytoscape', 'tapNodeData')],
              # prevent_initial_call=True
              )
def TapNodeData_info(data):
    if data: return 'Reference treatment selected: ', data['label']
    else:    return 'Click on a node to choose reference treatment'


############ - Funnel plot  - ###############
@app.callback(Output('funnel-fig', 'figure'),
              [Input('cytoscape', 'selectedNodeData'),
               Input("_outcome_select", "value"),
               Input("funnel_data_STORAGE", "data")]
               )
def Tap_funnelplot(node, outcome_idx, funnel_data):
    return __Tap_funnelplot(node, outcome_idx, funnel_data)

@app.callback(Output('funnel-fig-normal', 'figure'),
              [Input('cytoscape', 'selectedEdgeData'),
               Input("_outcome_select", "value"),
               Input("net_data_STORAGE", "data"),
               Input("forest_data_prws_STORAGE", "data")
               ]
               )
def Tap_funnelplot(edge, outcome_idx, net_data, pw_data):
    return __Tap_funnelplot_normal(edge, outcome_idx, net_data, pw_data)


############ - Ranking plots  - ###############
@app.callback([Output('tab-rank1', 'figure'),
              Output('tab-rank2', 'figure')],
              Input('ranking_data_STORAGE', 'data'),
              Input('number-outcomes', 'value'),
            #   Input("submit_modal_data", "n_clicks_timestamp"),
              Input("_outcome_select", "value"),
              Input("_outcome_select", "options"),
              Input("ranking_outcome_select2", "value"),
              State('net_data_STORAGE', 'data'))
def ranking_plot(ranking_data, out_number, out_idx1, options, out_idx2,net_data):
    return __ranking_plot(ranking_data, out_number, out_idx1, options, out_idx2,net_data)

###############################################################################
################### Bootstrap Dropdowns callbacks #############################
###############################################################################

@app.callback([Output('dd_nds', 'children')],
              [Input('dd_nds_default', 'n_clicks_timestamp'), Input('dd_nds_default', 'children'),
               Input('dd_nds_tot_rnd', 'n_clicks_timestamp'), Input('dd_nds_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, tot_rnd_t, tot_rnd_v):
    values = [default_v, tot_rnd_v]
    dd_nds = [default_t or 0, tot_rnd_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('exp-options', 'children')],
              [Input('jpeg-option', 'n_clicks_timestamp'), Input('jpeg-option', 'children'),
               Input('png-option', 'n_clicks_timestamp'), Input('png-option', 'children'),
               Input('svg-option', 'n_clicks_timestamp'), Input('svg-option', 'children'),],
              prevent_initial_call=True)
def which_dd_export(default_t, default_v, png_t, png_v, svg_t, svg_v):
    values = [default_v, png_v, svg_v]
    dd_nds = [default_t or 0, png_t or 0, svg_t or 0]
    which = dd_nds.index(max(dd_nds))
    return [values[which]]

@app.callback([Output('dd_egs', 'children')],
              [Input('dd_egs_default', 'n_clicks_timestamp'), Input('dd_egs_default', 'children'),
               Input('dd_egs_tot_rnd', 'n_clicks_timestamp'), Input('dd_egs_tot_rnd', 'children')],
              prevent_initial_call=True)
def which_dd_egs(default_t, default_v, nstud_t, nstud_v):
    values = [default_v, nstud_v]
    dd_egs = [default_t or 0, nstud_t or 0]
    which = dd_egs.index(max(dd_egs))
    return [values[which]]


@app.callback([Output('dd_nclr', 'children'), Output('close_modal_dd_nclr_input', 'n_clicks'),
               Output("open_modal_dd_nclr_input", "n_clicks")],
              [Input('dd_nclr_default', 'n_clicks_timestamp'), Input('dd_nclr_default', 'children'),
               Input('dd_nclr_rob', 'n_clicks_timestamp'), Input('dd_nclr_rob', 'children'),
               Input('dd_nclr_class', 'n_clicks_timestamp'), Input('dd_nclr_class', 'children'),
               Input('close_modal_dd_nclr_input', 'n_clicks'),
               ],
              prevent_initial_call=True)
def which_dd_nds(default_t, default_v, rob_t, rob_v, class_t, class_v, closing_modal):
    values = [default_v, rob_v, class_v]
    dd_nclr = [default_t or 0, rob_t or 0, class_t or 0]
    which = dd_nclr.index(max(dd_nclr))
    return values[which] if not closing_modal else None, None, None


@app.callback([Output('dd_eclr', 'children'), Output('close_modal_dd_eclr_input', 'n_clicks'),
               Output("open_modal_dd_eclr_input", "n_clicks")],
              [Input('dd_edge_default', 'n_clicks_timestamp'), Input('dd_edge_default', 'children'),
               Input('dd_edge_label', 'n_clicks_timestamp'), Input('dd_edge_label', 'children'),
               Input('close_modal_dd_eclr_input', 'n_clicks'),
               ],
              prevent_initial_call=True)
def which_dd_edges(default_t, default_v, eclr_t, eclr_v,closing_modal):
    values = [default_v, eclr_v]
    dd_eclr = [default_t or 0, eclr_t or 0]
    which = dd_eclr.index(max(dd_eclr))
    return values[which] if not closing_modal else None, None, None


flatten = lambda t: [item for sublist in t for item in sublist]

@app.callback([Output('graph-layout-dropdown', 'children')],
              flatten([[Input(f'dd_ngl_{item.lower()}', 'n_clicks_timestamp'),
                        Input(f'dd_ngl_{item.lower()}', 'children')]
                       for item in ['Circle', 'Breadthfirst', 'Grid', 'Spread', 'Cose', 'Cola',
                                    'Dagre', 'Klay']
                       ]), prevent_initial_call=True)
def which_dd_nds(circle_t, circle_v, breadthfirst_t, breadthfirst_v,
                 grid_t, grid_v, spread_t, spread_v, cose_t, cose_v,
                 cola_t, cola_v, dagre_t, dagre_v, klay_t, klay_v):
    values =  [circle_v, breadthfirst_v, grid_v, spread_v, cose_v, cola_v, dagre_v, klay_v]
    times  =  [circle_t, breadthfirst_t, grid_t, spread_t, cose_t, cola_t, dagre_t, klay_t]
    dd_ngl =  [t or 0 for t in times]
    which  =  dd_ngl.index(max(dd_ngl))
    return [values[which]]


#################################################################
############### Bootstrap MODALS callbacks ######################
#################################################################

# ----- node color modal -----#
@app.callback(Output("modal", "is_open"),
              [Input("open_modal_dd_nclr_input", "n_clicks"),
               Input("close_modal_dd_nclr_input", "n_clicks")],
              )
def toggle_modal(open_t, close):
    if open_t: return True
    if close: return False
    return False

# ----- edge color modal -----#
@app.callback(Output("modal_edge", "is_open"),
              [Input("open_modal_dd_eclr_input", "n_clicks"),
               Input("close_modal_dd_eclr_input", "n_clicks")],
              )
def toggle_modal_edge(open_t, close):
    if open_t: return True
    if close: return False
    return False

#---------------------------------- INITIAL DATA SELECTION and ALL NMA RUNS (in MODALS) ---------------------------------------#



@app.callback([
            #   Output("modal_data", "is_open"),
            #    Output("modal_transitivity", "is_open"),
               Output("modal_data_checks", "is_open"),
               Output("TEMP_raw_data_STORAGE", "data"),
               Output("TEMP_net_data_STORAGE", "data"),
               Output("uploaded_datafile_to_disable_cinema", "data"),
               Output('Rconsole-error-data', 'children'),
               Output('R-alert-data', 'is_open'),
               Output('dropdown-intervention', 'options'),
               ],
              [
            #    Input('trans_to_results', 'n_clicks_timestamp'),
               Input("upload_modal_data2", "n_clicks_timestamp"),
               Input('uploaded_datafile_to_disable_cinema','data'),
               Input("submit_modal_data", "n_clicks_timestamp")
               ],
              [
               State("radio-format", "value"),
               State({'type': 'dataselectors_1', 'index':ALL}, "value"),
               State('number-outcomes', "value"),
               State({'type': 'outcometype', 'index': ALL}, 'value'),
               State({'type': 'effectselectors', 'index': ALL}, 'value'),
               State({'type': 'directionselectors', 'index': ALL}, 'value'),
               State({'type': 'variableselectors', 'index': ALL}, 'value'),
            #    State("modal_transitivity", "is_open"),
               State("modal_data_checks", "is_open"),
               State('datatable-upload2', 'contents'),
               State('datatable-upload2', 'filename'),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_raw_data_STORAGE", "data")
               ]
              )
def data_trans( 
            #  trans_to_results,
              upload, filename2,
              submit,
               search_value_format, overall_variables, number_outcomes, outcome_type,
               effectselectors, directionselectors, variableselectors,
               modal_data_checks_is_open,
               contents, filename, 
               TEMP_net_data_STORAGE,
               TEMP_raw_data_STORAGE
               ):
    return __data_trans( 
        #  trans_to_results,
              upload,  filename2,
              submit,
               search_value_format, overall_variables, number_outcomes,outcome_type,
               effectselectors, directionselectors, variableselectors,
               modal_data_checks_is_open,
               contents, filename, 
               TEMP_net_data_STORAGE,
               TEMP_raw_data_STORAGE
               )



@app.callback([Output("select_effect_modifier", "style"),
              Output("arrow_step3", "style"),
              Output("effect_modifier_select", "style")
              ],
              Input({'type': 'variableselectors', 'index': ALL}, 'value'),
              )
def modal_ENABLE_UPLOAD_button(variableselectors):
    if len(variableselectors):
        if all(variableselectors):
            return {"display": 'grid', 'justify-content': 'center'}, {'display':'grid', 'justify-content': 'center'},{'display':'grid', 'justify-content': 'center'}
        else:
            return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}
    else:
        return {"display": 'none'}, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}





@app.callback([Output("upload_modal_data2", "disabled"),
               Output("run_button", "style"),
               Output("arrow_step4", "style")],
               [Input('effect_modifier_checkbox', 'value'),
                Input('no_effect_modifier', 'value')]
)
def modal_ENABLE_UPLOAD_button(effect_mod, no_effect_mod):
    if effect_mod or no_effect_mod:
        return False, {'display':'grid', 'justify-content': 'center'}, {'display':'grid', 'justify-content': 'center'}
    else:
        return True, {'display':'none', 'justify-content': 'center'}, {'display':'none', 'justify-content': 'center'}






from assets.storage import DEFAULT_DATA
OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())[:-2]
# OUTPUTS_STORAGE_IDS = list(DEFAULT_DATA.keys())


@app.callback([Output(id, 'data') for id in OUTPUTS_STORAGE_IDS] + [Output('token-not-found-alert','children'),
                                                                    Output("output_username", "children"),
                                                                    Output("output_token", "children"),
                                                                    Output('button-token','disabled')],
              [Input("submit_modal_data", "n_clicks"),
               Input('reset_project','n_clicks'),
            #    Input("username-token-upload", "data"),
               Input("button-token", "n_clicks"),
               Input("input-token-load", "value"),
               Input("load-project", "n_clicks"),
               Input("datatable-filename-upload", "data"),
               ],
              [ State("input-username", "value")]+[State('TEMP_'+id, 'data') for id in OUTPUTS_STORAGE_IDS]+[State('number-outcomes', 'value')],
              prevent_initial_call=True
              )
def modal_SUBMIT_button(submit, reset_btn,
                        # token_data, 
                        token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        input_token,
                        TEMP_raw_data_STORAGE,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        # TEMP_user_elements_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        num_out
                        ):
    return __modal_SUBMIT_button_new(submit, reset_btn,
                        # token_data, 
                        token_btn,
                        token_data_load, token_load_btn,
                        filename,
                        input_token,
                        TEMP_raw_data_STORAGE,
                        TEMP_net_data_STORAGE,
                        TEMP_consistency_data_STORAGE,
                        # TEMP_user_elements_STORAGE,
                        TEMP_forest_data_STORAGE,
                        TEMP_forest_data_prws_STORAGE,
                        TEMP_ranking_data_STORAGE,
                        TEMP_funnel_data_STORAGE,
                        TEMP_league_table_data_STORAGE,
                        TEMP_net_split_data_STORAGE,
                        TEMP_net_split_ALL_data_STORAGE,
                        num_out
                        )




@app.callback(Output('number-outcomes', 'value'),
               Input("input-token-load", "value"),
               Input("load-project", "n_clicks"),
              [State('number-outcomes', 'value')],
              prevent_initial_call=True
              )
def modal_SUBMIT_button(
                        input_load,
                        load_trigger,
                        num_out
                        ):
    triggered = [tr['prop_id'] for tr in dash.callback_context.triggered]
    load_btn_triggered = False
    if 'load-project.n_clicks' in triggered: load_btn_triggered = True
    if load_btn_triggered:
        usr_token_load_ = input_load
        # parent_dir_load = "USR_DATASETS/"
        # directory_load = f"{usr_token_load_}"
        # path = os.path.join(parent_dir_load, directory_load)
        token_outnum = usr_token_load_.split('_')
        out_num = int(token_outnum[1])
        return out_num
    return num_out




@app.callback(Output("dropdown-effectmod", "options"),
              [Input("effect_modifier_checkbox", "value"),
              Input("no_effect_modifier", "value")],
              State("dropdown-effectmod", "options")
              )
def update_dropdown_effect_mod(effect_modifier, no_effect_modifier, origin_effctm):
    if effect_modifier:
        options_modifier = [{'label': '{}'.format(modifier), 'value': modifier} 
                                for modifier in effect_modifier]
        return options_modifier
    if no_effect_modifier:

        return []
    return origin_effctm
    

##################bugs
@app.callback([Output("para-check-data", "children"),
               Output('para-check-data', 'data')],
              Input("modal_data_checks", "is_open"),
              [State('number-outcomes', "value"),
              State("TEMP_net_data_STORAGE", "data")],
              )
def modal_submit_checks_DATACHECKS(modal_data_checks_is_open, num_outcomes,TEMP_net_data_STORAGE):
    return __modal_submit_checks_DATACHECKS(modal_data_checks_is_open, num_outcomes,TEMP_net_data_STORAGE)



# @app.callback([Output('R-alert-nma', 'is_open'),
#                Output('Rconsole-error-nma', 'children'),
#                Output("para-anls-data", "children"),
#                Output('para-anls-data', 'data'),
#                Output("TEMP_forest_data_STORAGE", "data"),
#             #    Output("TEMP_user_elements_STORAGE", "data")
#                ],
#                Input("modal_data_checks", "is_open"),
#                [State('number-outcomes', "value"),
#                State("TEMP_net_data_STORAGE", "data"),
#                State("TEMP_forest_data_STORAGE", "data")]
#               )
# def modal_submit_checks_NMA_new(modal_data_checks_is_open,num_outcome, TEMP_net_data_STORAGE,
#                             TEMP_forest_data_STORAGE):
#     return __modal_submit_checks_NMA_new(modal_data_checks_is_open, num_outcome,TEMP_net_data_STORAGE,
#                             TEMP_forest_data_STORAGE)




@app.callback(
    [Output('R-alert-nma', 'is_open'),
     Output('Rconsole-error-nma', 'children'),
     Output('para-anls-data', 'children'),
     Output('para-anls-data', 'data'),
     Output('nma-task-store', 'data'),
     Output("TEMP_forest_data_STORAGE", "data"),
     Output('nma-task-poller', 'disabled')],
    [Input("modal_data_checks", "is_open"),
     Input('nma-task-poller', 'n_intervals')],
    [State('number-outcomes', "value"),
     State("TEMP_net_data_STORAGE", "data"),
     State("TEMP_forest_data_STORAGE", "data"),
     State('nma-task-store', 'data')],
    prevent_initial_call=True
)
def handle_nma_processing(modal_open, n_intervals, num_outcome, net_data_storage, 
                         forest_data_storage, task_store_data):
    return __handle_nma_processing__(modal_open, n_intervals, num_outcome, net_data_storage, 
                         forest_data_storage, task_store_data)






@app.callback([Output('R-alert-pair', 'is_open'),
               Output('Rconsole-error-pw', 'children'),
               Output("para-pairwise-data", "children"),
               Output('para-pairwise-data', 'data'),
               Output("TEMP_forest_data_prws_STORAGE", "data")],
               Input('TEMP_forest_data_STORAGE', 'modified_timestamp'),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State("TEMP_forest_data_prws_STORAGE", "data")
              )
def modal_submit_checks_PAIRWISE(nma_data_ts, num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE):
    return __modal_submit_checks_PAIRWISE_new(nma_data_ts, num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, TEMP_forest_data_prws_STORAGE)



@app.callback([Output('R-alert-league', 'is_open'),
               Output('Rconsole-error-league', 'children'),
               Output("para-LT-data", "children"),
               Output('para-LT-data', 'data'),
               Output('TEMP_league_table_data_STORAGE', 'data'),
               Output('TEMP_ranking_data_STORAGE', 'data'),
               Output('TEMP_consistency_data_STORAGE', 'data'),
               Output('TEMP_net_split_data_STORAGE', 'data'),
               Output('TEMP_net_split_ALL_data_STORAGE', 'data')
               ],
               Input('TEMP_forest_data_prws_STORAGE', 'modified_timestamp'),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_league_table_data_STORAGE', 'data'),
               State('TEMP_ranking_data_STORAGE', 'data'),
               State('TEMP_consistency_data_STORAGE', 'data'),
               State('TEMP_net_split_data_STORAGE', 'data'),
               State('TEMP_net_split_ALL_data_STORAGE', 'data'),
               State({'type': 'outcomeprimary', 'index': ALL}, "value"),
              )
def modal_submit_checks_LT(pw_data_ts, num_outcome,modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data,
                           netsplit_all,outcome_index):
    return  __modal_submit_checks_LT_new(pw_data_ts,num_outcome, modal_data_checks_is_open,
                           TEMP_net_data_STORAGE, LEAGUETABLE_data,
                           ranking_data, consistency_data, net_split_data,
                           netsplit_all,outcome_index)



@app.callback([Output('R-alert-funnel', 'is_open'),
               Output('Rconsole-error-funnel', 'children'),
               Output("para-FA-data", "children"),
               Output('para-FA-data', 'data'),
               Output('TEMP_funnel_data_STORAGE', 'data')],
               Input("TEMP_league_table_data_STORAGE", "modified_timestamp"),
               State('number-outcomes', "value"),
               State("modal_data_checks", "is_open"),
               State("TEMP_net_data_STORAGE", "data"),
               State('TEMP_funnel_data_STORAGE', 'data')

              )
def modal_submit_checks_FUNNEL(lt_data_ts, num_outcome,modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data):
    return __modal_submit_checks_FUNNEL_new(lt_data_ts,num_outcome, modal_data_checks_is_open, TEMP_net_data_STORAGE, FUNNEL_data)





@app.callback(Output("submit_modal_data", "disabled"),
              [Input(id, 'data') for id in ['para-check-data','para-anls-data','para-pairwise-data',
                                            'para-LT-data', 'para-FA-data']])
def modal_submit_button(para_check_data_DATA, para_anls_data_DATA, para_prw_data_DATA, para_LT_data_DATA, para_FA_data_DATA):
    return not (para_check_data_DATA==para_anls_data_DATA==para_prw_data_DATA==para_LT_data_DATA==para_FA_data_DATA=='__Para_Done__')



### -------------------------------------------- EXPAND CALLBACKS ----------------------------------------------- ###

# ----- data expand modal -----#


@app.callback(
    Output("one-half-1", "style"),
    Output("one-half-2", "style"),
    Output('data-expand', 'style'),
    Output('data-zoomout', 'style'),
    Output('data-expand1', 'style'),
    Output('data-zoomout1', 'style'),
    Output('network-expand', 'style'),
    Output('network-zoomout', 'style'),
    Output("one-half-3", "style"),
    Output("cytoscape", "style"),
    Input("data-expand", "n_clicks_timestamp"),
    Input("data-zoomout", "n_clicks_timestamp"),
    Input("data-expand1", "n_clicks_timestamp"),
    Input("data-zoomout1", "n_clicks_timestamp"),
    Input("network-expand", "n_clicks_timestamp"),
    Input("network-zoomout", "n_clicks_timestamp"),

)
def toggle_modal(expand, zoomout, expand1, zoomout1, expand_plot, zoomout_plot):
    style_display = {'display': 'block'}
    style_no_display = {'display': 'none'}
    style_expand_width = {'width': '93.4%', 'margin-left': '3.3%'}
    style_width = {'width': '50.6%'}
    style = {"display": "inline-block"}
    style_no = {"display": "none"}
    style_height = {'display': 'block','height': '100%'}
    style_neplot={
            'height': '75vh', 'width': '100%', 
                'margin-top': '10px',
                'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}
    style_neplot_expand={
            'height': '75vh', 'width': '100%', 
                'margin-top': '10px',
                'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
                'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}
    style_neplot_down={
        'height': '95%', 'width': '100%', 
            'margin-top': '10px',
            'margin-left': '-10px','margin-right': '-10px',  'z-index': '999',
            'padding-left': '-10px', 'border-right': '3px solid rgb(165 74 97)'}

    if not ctx.triggered_id:
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width,style_neplot

    triggered_button_id = ctx.triggered_id.split(".")[0]
    if triggered_button_id =='network-expand':
        return style_expand_width, style_no_display, style, style_no, style_no, style, style_no, style, style_expand_width,style_neplot_expand
    
    if triggered_button_id =='network-zoomout':
        return style_display, style_width, style, style_no, style_no, style, style, style_no, style_expand_width,style_neplot
    
    if triggered_button_id =='data-expand':
        return style_no_display, style_expand_width, style_no, style, style_no, style_no, style, style_no,style_expand_width,style_neplot
    
    elif triggered_button_id =='data-zoomout':
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width,style_neplot
    
    elif triggered_button_id =='data-zoomout1':
        return style_height, style_width, style, style_no, style, style_no, style, style_no,style_width, style_neplot_down 
    elif triggered_button_id =='data-expand1':
        return style_display, style_width, style, style_no, style_no, style, style, style_no,style_expand_width, style_neplot





@app.callback(
    Output("modal_info", "is_open"),
    [Input("info_icon", "n_clicks"),
     Input("close_modal_info", "n_clicks")],
    [State("modal_info", "is_open")],
)
def toggle_modal(open, close, is_open):
    if open or close:
        return not is_open
    return is_open

###############################################################################
################### EXPORT TO CSV ON CLICK BUTTON ############################
###############################################################################

@app.callback(Output("download_datatable", "data"),
              [Input('data-export', "n_clicks"),
               State('datatable-upload-container', 'data')],
               prevent_initial_call=True)
def generate_csv(n_nlicks, data):
    df = pd.DataFrame(data)
    return dash.dcc.send_data_frame(df.to_csv, filename="data_wide.csv")


@app.callback(Output("download_consistency_all", "data"),
              [Input('btn-netsplit-all', "n_clicks"),
               Input('consistency_outcome_select','value'),
               State("net_split_ALL_data_STORAGE", "data")],
               prevent_initial_call=True)
def generate_csv_consistency(n_nlicks, outcome_idx, consistencydata_all):
    return __generate_csv_consistency(n_nlicks, outcome_idx, consistencydata_all)

#### xlsx colors netsplit table
@app.callback(Output("download_consistency", "data"),
              [Input('consistency-export', "n_clicks"),
               State("netsplit_table-container", "data")],
               prevent_initial_call=True)
def generate_xlsx_netsplit(n_nlicks, consistencydata):
    return __generate_xlsx_netsplit(n_nlicks, consistencydata)

#### xlsx colors league table
@app.callback(Output("download_leaguetable", "data"),
              [Input('league-export', "n_clicks"),
               State("league_table", "children")],
               prevent_initial_call=True)
def generate_xlsx_league(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)

@app.callback(Output("download_leaguetable_both", "data"),
              [Input('league-export-both', "n_clicks"),
               State("league_table_both", "children")],
               prevent_initial_call=True)
def generate_xlsx_league(n_clicks, leaguedata):
    return __generate_xlsx_league(n_clicks, leaguedata)

#############################################################################
############################# TOGGLE SECTION ################################
#############################################################################



### -------------- toggle switch league table ---------------- ###
@app.callback([Output("cinemaswitchlabel1", "style"),
               Output("cinemaswitchlabel2", "style")],
              [Input("rob_vs_cinema", "value")])
def color_leaguetable_toggle(toggle_value):
    style1 = {'color': '#808484' if toggle_value else '#5a87c4', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '10px'}
    style2 = {'color': '#5a87c4' if toggle_value else '#808484', 'font-size': '12px',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '0px', }
    return style1, style2

### -------------- toggle switch funnel plot ---------------- ###
@app.callback([Output("funnelswitchlabel1", "style"),
               Output("funnelswitchlabel2", "style")],
              [Input("toggle_funnel_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#5a87c4',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#5a87c4' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2

### -------------- toggle switch consistency ---------------- ###
@app.callback([Output("consistencyswitchlabel1", "style"),
               Output("consistencyswitchlabel2", "style")],
              [Input("toggle_consistency_direction", "value")])
def color_funnel_toggle(toggle_value):
    style1 = {'color': 'gray' if toggle_value else '#5a87c4',
              'display': 'inline-block', 'margin': 'auto', 'padding-left': '20px', 'font-size':'11px'}
    style2 = {'color': '#5a87c4' if toggle_value else 'gray',
              'display': 'inline-block', 'margin': 'auto', 'padding-right': '20px', 'font-size':'11px'}
    return style1, style2


#############################################################################
######################### DISABLE TOGGLE SWITCHES ###########################
#############################################################################

## disable cinema coloring toggle if no cinema files are passed
@app.callback([Output('rob_vs_cinema', 'disabled'),
              Output('rob_vs_cinema_modal', 'disabled')],
              [Input('datatable-secondfile-upload', 'filename'),
               Input("uploaded_datafile_to_disable_cinema", "data"),
               ]
              )
def disable_cinema_toggle(filename_cinema1, filename_data):

    if filename_cinema1 is None and filename_data: return True, True
    else: return False, False

@app.callback(Output('rob_vs_cinema-both', 'disabled'),
              [Input('datatable-secondfile-upload-1', 'filename'),
              Input('datatable-secondfile-upload-2', 'filename'),
               Input("uploaded_datafile_to_disable_cinema", "data"),
               ]
              )
def disable_cinema_toggle(filename_cinema1, filename_cinema2,file_data):

    if (filename_cinema1 is None or filename_cinema2 is None) and file_data: return True
    else: return False



#### download pdfs ####
@app.callback(Output("download-demodata", "data"),
              Input("demodata", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("db/psoriasis_long_complete.csv")

@app.callback(Output("download-tuto", "data"),
              Input("full-tuto-pdf", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")

@app.callback(Output("download-guide", "data"),
              Input("full-docu-pdf", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/NMAstudio_tutorial.pdf")

@app.callback(Output("download-data-explain", "data"),
              Input("data_explain", "n_clicks"),
              prevent_initial_call=True)
def func(n_clicks):
     return send_file("Documentation/variables_explain.pdf")


#################### save project/generate token/laod project ###################

#modal Save/Load Project
@app.callback(
    Output("modal_saveload", "is_open"),
    [Input("open_saveload", "n_clicks"),
     Input("close_saveload", "n_clicks"),
     Input("close_saveload_2", "n_clicks")
     ],
    [State("modal_saveload", "is_open")],
)
def toggle_modal(n1, n2, n2_close, is_open):
    if n1 or n2 or n2_close:
        return not is_open
    return is_open


###############overall information##################

@app.callback([Output('numstudies', 'children'),
              Output('numtreat', 'children'),
              Output('numcompar', 'children'),
              Output('numcom_without', 'children')],
              Input('net_data_STORAGE', 'data'))
def infor_overall(data):
    net_data = pd.read_json(data[0], orient='split').round(3)
    n_studies = len(net_data.studlab.unique())
    num_study = f"Number of studies: {n_studies}"

    combined_treats = pd.concat([net_data['treat1'], net_data['treat2']])
    n_treat= combined_treats.nunique()
    num_treat = f"Number of treatments: {n_treat}"

    unique_combinations = list(itertools.combinations(combined_treats.unique(), 2))
    num_unique_combinations = len(unique_combinations)

    net_data['treat_combine'] = list(zip(net_data['treat1'], net_data['treat2']))
    unique_combinations = set(net_data['treat_combine'])
    n_com = len(unique_combinations)

    num_com = f"Number of comparisons with direct evidence: {n_com}"

    n_com_without = num_unique_combinations - n_com
    num_com_without = f"Number of comparisons without direct evidence: {n_com_without}"

    return [num_study],[num_treat],[num_com],[num_com_without]

###########################results selection###########################################
@app.callback([
              Output('data_tab', 'style'),
              Output('trans_tab', 'style'),
              Output('forest_tab', 'style'),
              Output('tab2', 'style'),
              Output('league_tab', 'style'),
              Output('league_tab_both', 'style'),
              Output('consis_tab', 'style'),
              Output('funnel_tab', 'style'),
              Output('ranking_tab', 'style'),
              Output('results_tabs', 'value'),
              Output('results_tabs2', 'value')
              ],
              Input('result_selected', 'value'))
def results_display(selected):
    style_display = {'color':'grey','display': 'flex', 'justify-content':'center', 'align-items':'center'}
    style_no_display = {'color':'grey','display': 'none', 'justify-content':'center', 'align-items':'center'}

    if selected == 0:
        return [style_display] * 2 + [style_no_display] * 7 +['data_tab']+['trans_tab']
    if selected == 1:
        return [style_no_display]*2 + [style_display]*2 + [style_no_display]*5 +['forest_tab']+['tab2']
    if selected == 2:
        return [style_no_display]*4 + [style_display]*2 + [style_no_display]*3+['league_tab']+['league_tab_both']
    if selected == 3:
        return [style_no_display]*8 + [style_display]+['ranking_tab']+['']
    if selected == 4:
        return [style_no_display]*6 + [style_display]*2 + [style_no_display]+['consis_tab']+['funnel_tab']


## -------------------------------------------- INFOBOXES CALLBACKS TO MIGRATE------------------------------------ ##

### -------------------------------------------- FUNNEL CALLBACKS ----------------------------------------------- ###

#GRAPH INFO
@app.callback(
    Output("modal-body-graph", "is_open"),
    [
        Input("open-body-graph", "n_clicks"),
        Input("close-body-graph", "n_clicks"),
    ],
    [State("modal-body-graph", "is_open")],
)
def toggle_modal_graph(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#DATA INFO
@app.callback(
    Output("modal-body-expand", "is_open"),
    [
        Input("open-body-expand", "n_clicks"),
        Input("close-body-expand", "n_clicks"),
    ],
    [State("modal-body-expand", "is_open")],
)
def toggle_modal_expand(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-body-year", "is_open"),
    [
        Input("open-body-year", "n_clicks"),
        Input("close-body-year", "n_clicks"),
    ],
    [State("modal-body-year", "is_open")],
)
def toggle_modal_year(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


#SCATTER INFO
@app.callback(
    Output("modal-body-scatter", "is_open"),
    [
        Input("open-body-scatter", "n_clicks"),
        Input("close-body-scatter", "n_clicks"),
    ],
    [State("modal-body-scatter", "is_open")],
)
def toggle_modal_scatter(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



#FUNNEL INFO
@app.callback(
    Output("modal-body-funnel", "is_open"),
    [
        Input("open-body-funnel", "n_clicks"),
        Input("close-body-funnel", "n_clicks"),
    ],
    [State("modal-body-funnel", "is_open")],
)
def toggle_modal_funnel(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


#FOREST INFO
@app.callback(
    Output("modal-body-forest", "is_open"),
    [
        Input("open-body-forest", "n_clicks"),
        Input("close-body-forest", "n_clicks"),
    ],
    [State("modal-body-forest", "is_open")],
)
def toggle_modal_forest(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-body-forest2", "is_open"),
    [
        Input("open-body-forest2", "n_clicks"),
        Input("close-body-forest2", "n_clicks"),
    ],
    [State("modal-body-forest2", "is_open")],
)
def toggle_modal_forest2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#INCONS INFOG
@app.callback(
    Output("modal-body-incons", "is_open"),
    [
        Input("open-body-incons", "n_clicks"),
        Input("close-body-incons", "n_clicks"),
    ],
    [State("modal-body-incons", "is_open")],
)
def toggle_modal_incons(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#LEAGUE INFO
@app.callback(
    Output("modal-body-league1", "is_open"),
    [
        Input("open-body-league1", "n_clicks"),
        Input("close-body-league1", "n_clicks"),
    ],
    [State("modal-body-league1", "is_open")],
)
def toggle_modal_league1(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-body-league2", "is_open"),
    [
        Input("open-body-league2", "n_clicks"),
        Input("close-body-league2", "n_clicks"),
    ],
    [State("modal-body-league2", "is_open")],
)
def toggle_modal_league2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-body-RoB", "is_open"),
    [
        Input("open-body-RoB", "n_clicks"),
        Input("close-body-RoB", "n_clicks"),
    ],
    [State("modal-body-RoB", "is_open")],
)
def toggle_modal_RoB(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("modal-body-cinema", "is_open"),
    [
        Input("open-body-cinema", "n_clicks"),
        Input("close-body-cinema", "n_clicks"),
    ],
    [State("modal-body-cinema", "is_open")],
)
def toggle_modal_cinema(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#RANKING INFO
@app.callback(
    Output("modal-body-rank", "is_open"),
    [
        Input("open-body-rank", "n_clicks"),
        Input("close-body-rank", "n_clicks"),
    ],
    [State("modal-body-rank", "is_open")],
)
def toggle_modal_rank(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
## -------------------------------------------- END INFOBOXES CALLBACKS ----------------------------------------------- ##


   

####################################################################
####################################################################
############################ SKT TOOL ##############################


from tools.functions_skt_abs_forest import __Change_Abs

@app.callback(
    Output("quickstart-grid", "rowData"),
    # Output("quickstart-grid", "style"),
    # Input("nomal_vs_log", "value"),
    Input("checklist_effects", "value"),
    Input("quickstart-grid", "cellValueChanged"),
    Input("range_lower", "value"),
    # Input("range_upper", "value"),
    State("quickstart-grid", "rowData"),
)

def selected(value_effect, value_change,lower,rowData):
    return __Change_Abs(value_effect, value_change,lower,rowData)



app.clientside_callback(
    """(id) => {
        dash_ag_grid.getApiAsync(id).then((grid) => {
            grid.addEventListener('rowGroupOpened', (em) => {
                if (em.node.detailNode && em.expanded) {
                    gridDetail = em.node.detailNode.detailGridInfo
                    gridDetail.api.addEventListener('cellClicked', 
                    (ed) => {
                    const newChange = {...ed, node: {id:`${gridDetail.id} - ${ed.node.id}`}}
                    em.api.getGridOption('onCellClicked')(newChange)
                    })
                }
            })
        })
        return window.dash_clientside.no_update
    }""",
    Output('forest-fig-pairwise', 'id'),
    Input('quickstart-grid', 'id')
)


@app.callback(
    Output("modal_forest", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_forest", "n_clicks"),
)

def display_forestplot(cell, _):
    if ctx.triggered_id == "close_forest":
        return False
    if cell is not None and len(cell) != 0 and 'colId' in cell and cell['colId'] == "direct" and cell['value'] is not None and cell['value']!= '':
        return True
    return no_update


@app.callback(
   [ Output('forest-fig-pairwise', 'figure'),
    Output('forest-fig-pairwise', 'style')],
    [Input("quickstart-grid", "cellClicked"),
    Input('forest-fig-pairwise', 'style')]
)

def show_forest_plot(cell, style_pair):
    # print(cell)
    return __show_forest_plot(cell, style_pair)


@app.callback(
    Output("treat_comp", "children"),
    Output("num_RCT", "children"), 
    Output("num_sample", "children"),
    Output("mean_modif", "children"), 
    Input("quickstart-grid", "cellClicked"),
)

def display_sktinfo(cell):
    treat_comp, num_RCT, num_sample, mean_modif = '','','',''
    if  cell is not None and len(cell) != 0 and 'colId' in cell and cell['colId'] == "Treatment" and cell['value'] is not None and cell['value']!= '':
        df_n_rct = pd.read_csv('db/skt/final_all.csv')
        dic_data =cell
        treat = dic_data['value']
        # idx = dic_data['rowIndex']
        refer = dic_data['rowId'].split('_')[1].split(' ')[0]
        treat_comp = f'Treatment: {treat}, Comparator: {refer}'
        
        n_rct = df_n_rct.loc[(df_n_rct['Treatment'] == treat) & (df_n_rct['Reference'] == refer), 'k']
        # print(n_rct)
        n_rct_value = n_rct.iloc[0] if not n_rct.empty else np.NAN
        num_RCT = f'Randomize controlled trials: {n_rct_value}'

        df_n_total = pd.read_csv('db/psoriasis_wide_complete1.csv')
        set1 = {(treat, refer), (refer, treat)}

        # Extract relevant rows from the DataFrame
        dat_extract = df_n_total[
            df_n_total.apply(lambda row: (row['treat1'], row['treat2']) in set1, axis=1)
        ]
        # Calculate the total
        n_total = dat_extract['n11'].sum() + dat_extract['n21'].sum()
        num_sample = f'Total participants: {n_total}'

        mean_age = round(dat_extract['age'].mean(), 2)
        mean_gender = round((dat_extract['male'] / (dat_extract['n11'] + dat_extract['n21'])).mean(), 2)


        mean_modif = f'Mean age: {mean_age}\nMean male percentage: {mean_gender}'



    return treat_comp, num_RCT, num_sample, mean_modif




@app.callback(
    Output("modal_transitivity", "is_open"), 
    Input("trans_button", "n_clicks"),
    Input("close_trans", "n_clicks"),
)

def display_forestplot(cell, _):
    if ctx.triggered_id == "close_trans":
        return False
    if ctx.triggered_id == "trans_button":
        return True
    return no_update


@app.callback(Output('boxplot_skt', 'figure'),
              Input('ddskt-trans', 'value'),)
def update_boxplot(value):
    return __show_boxplot(value)


@app.callback([Output('cytoscape_skt', 'stylesheet'),
               Output('trigger_info', 'children')],
              [Input('cytoscape_skt', 'tapNode'),
               Input('cytoscape_skt', 'selectedNodeData'),
               Input('cytoscape_skt', 'elements'),
               Input('cytoscape_skt', 'selectedEdgeData')
               ]
              )
def generate_skt_stylesheet(node, slct_nodesdata, elements, slct_edgedata ):
    return __generate_skt_stylesheet(node, slct_nodesdata, elements, slct_edgedata)




@app.callback(Output('cytoscape_skt2', 'stylesheet'),
              [Input('cytoscape_skt2', 'tapNode'),
               Input('cytoscape_skt2', 'selectedNodeData'),
               Input('cytoscape_skt2', 'elements'),
               Input('cytoscape_skt2', 'selectedEdgeData')
               ]
              )
def generate_skt_stylesheet2(node, slct_nodesdata, elements, slct_edgedata ):
    return __generate_skt_stylesheet2(node, slct_nodesdata, elements, slct_edgedata)





@app.callback(
    Output("skt_modal_copareinfo", "is_open"), 
    Input("quickstart-grid", "cellClicked"),
    Input("close_compare", "n_clicks"),
)

def display_sktinfo(cell, _):
    if ctx.triggered_id == "close_compare":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if ('colId' in cell and cell['colId'] == "Treatment" and cell['value']is not None):
            return True
    return no_update


@app.callback([Output('routine', 'style'),
               Output('cont', 'style'),
               Output('side', 'style'),
               Output('visit', 'style'),
               Output('cost', 'style'),],
              [
            #    Input('routine', 'style'),
            #    Input('cont', 'style'),
            #    Input('side', 'style'),
            #    Input('visit', 'style'),
            #    Input('cost', 'style'),
               Input('routine', 'n_clicks'),
               Input('cont', 'n_clicks'),
               Input('side', 'n_clicks'),
               Input('visit', 'n_clicks'),
               Input('cost', 'n_clicks'),
               ]
              )
def image_color_change(style_routine, style_count,style_side,style_visit,style_cost):
    style_selected = {'justify-self':'center', "filter":'drop-shadow(2px 4px 6px red)'}
    style_unselected = {'justify-self':'center', "filter":'grayscale(1)'}
    defalut_style = {'justify-self':'center'}
    if ctx.triggered_id == "routine":
        return [style_selected]+[style_unselected]*4
    if ctx.triggered_id == "cont":
        return [style_unselected]+[style_selected]+[style_unselected]*3
    if ctx.triggered_id == "side":
        return [style_unselected]*2+[style_selected]+[style_unselected]*2
    if ctx.triggered_id == "visit":
        return [style_unselected]*3+[style_selected]+[style_unselected]
    if ctx.triggered_id == "cost":
        return [style_unselected]*4+[style_selected]
    else:
        return [defalut_style]*5


#########unitil here#############

# @app.callback(
#     [Output('grid_type', 'children'),
#      Output('treatment_toast', 'children')],
#     Input('toggle_grid_select','value')
# )
# def display_grid(value):
#     if value:
#         return [grid2],[checklist, button_clear]
#     return [grid, model_skt_stand1, model_skt_stand2],display_treatment


# @app.callback(
#     Output('checklist_treat','value'),
#     Input('clear-val','n_clicks'),
#     State('checklist_treat','value')
# )
# def clear_treat(click, orig_value):
#     if click:
#         value = df_league.columns[1:].values
#     else:
#         value = orig_value
#     return value



# @app.callback(
#     [Output('grid2', 'rowData'),
#     Output('grid2', 'columnDefs'),
#     Output("grid2", "style")],
#     [Input('checklist_treat','value'),
#     Input("base_risk_input", "value")]
# )
# def display_only_selected(values, absolute_risk):
#     values = sorted(values)
#     absolute_risk = int(absolute_risk)
#     values_t = ['Treatment'] + values
#     df_league_c = df_league.copy()
#     df_league_c = df_league_c[df_league_c['Treatment'].isin (values)]
#     df_league_c =df_league_c[values_t]
#     # df_league_c =df_league_c.sort_index(axis=1)
#     n_row2 = len(values)
#     column_update = df_league_c.columns.tolist()

#     for idx, column in enumerate(column_update):
#         if idx < 2:
#             pass   
#         for row_idx in range(idx-1):
#             treat1 = column
#             treat2 = df_league_c['Treatment'].iloc[row_idx]
#             absolute_info = df[(df['Treatment'] == treat2) & (df['Reference'] == treat1)]
#             absolute_risk = int(absolute_risk)
#             absolute = int(absolute_info['RR'].iloc[0]*absolute_risk)-20
#             text_ab1 = f"{treat2} VS. {treat1} \n{absolute} more per 1000" if absolute > 0 else f"{treat2} VS. {treat1} \n{abs(absolute)} less per 1000"
#             text_ab2 = "\n Randomize control studies: 3\n Total participants in arm: xxx \n Mean age: xxx \nMean male percentage: XXX"
#             text_ab = text_ab1 + text_ab2
#             df_league_c.iloc[row_idx,idx] = text_ab
            

#     column1 = ['ADA','ADA', 'BIME']
#     column2 = ['ETA', 'FUM', 'GUSEL']

#     column_low1 = ['PBO','PBO', 'SECU']
#     column_low2 = ['RISAN', 'IFX', 'IFX']

#     # # # Number of pairs to select (in this case, 6 pairs)
    
#     treatments_list = df_league_c['Treatment'].tolist()


#     columnDefs=[
#     {"field": "Treatment", 
#     "headerName": "Treatment",
#      "tooltipField": 'ticker',
#      "tooltipComponentParams": { "color": '#d8f0d3' },
#     "sortable": False,
#     "filter": True, 
#     'cellStyle': {'font-weight':'bold',
#                     'background-color':'#B85042','color':'white','font-size':'12px', **default_style}}  
#     ]+[{"field": i,
#         "cellRenderer": "DCC_GraphClickData",
#         "maxWidth": 500,
#         "minWidth": 300,
#         "tooltipField": 'ticker',
#         "tooltipComponentParams": { "color": '#d8f0d3' },
#         'cellStyle': {"styleConditions":[{"condition": f"params.value === '{i}'", 
#                                     "style": {"backgroundColor": "antiquewhite", **default_style}},
#                                     {
#                                     "condition": f"{column1}.includes('{i}') &&" 
#                                     f"{[treatments_list.index(column2[index]) if (i in column1) and (column2[index] in treatments_list) else -1 for index, item in enumerate(column1)]}.includes(params.rowIndex)",
#                                     "style": {"backgroundColor": "rgb(0, 128, 0, 0.5)", **default_style}
#                                     },

#                                     {
#                                     "condition": f"{column2}.includes('{i}') &&" 
#                                     f"{[treatments_list.index(column1[index]) if (i in column2) and (column1[index] in treatments_list) else -1 for index, item in enumerate(column2)]}.includes(params.rowIndex)",
#                                     "style": {"backgroundColor": "rgb(0, 128, 0, 0.5)", **default_style}
#                                     },

#                                     {
#                                     "condition": f"{column_low1}.includes('{i}') &&" 
#                                     f"{[treatments_list.index(column_low2[index]) if (i in column_low1) and (column_low2[index] in treatments_list) else -1 for index, item in enumerate(column_low1)]}.includes(params.rowIndex)",
#                                     "style": {"backgroundColor": "rgb(184, 80, 66, 0.5)", **default_style}
#                                     },

#                                     {
#                                     "condition": f"{column_low2}.includes('{i}') &&" 
#                                     f"{[treatments_list.index(column_low1[index]) if (i in column_low2) and (column_low1[index] in treatments_list) else -1 for index, item in enumerate(column_low2)]}.includes(params.rowIndex)",
#                                     "style": {"backgroundColor": "rgb(184, 80, 66, 0.5)", **default_style}
#                                     },

#                                     {"condition": f"params.value !== '{i}'", 
#                                     "style": {**default_style}},
#                                     ]},}  for i in values]
#     style={'width': '1200px','height': f'{48 + 163 * n_row2}px'}


#     return df_league_c.to_dict("records"), columnDefs, style


# @app.callback(
#     Output('pass_model','is_open'),
#     Output('skt_all','style'),
#     Input('password_ok','n_clicks'),
#     Input('password','value'),
#     State('pass_model','is_open'),
#     State('skt_all','style'),
# )
# def clear_treat(click, password, pass_model, skt_style):
#     if password =='777' and click:
#         skt_style = {'diaplay': 'block'}
#         return not pass_model, skt_style
#     else:
#         return pass_model, skt_style

# clientside_callback(
#     """function (n) {
#         if (n) {
#             dash_ag_grid.getApi("quickstart-grid").exportDataAsExcel();
#         }
#         return dash_clientside.no_update
#     }""",
#     Output("btn-excel-export", "n_clicks"),
#     Input("btn-excel-export", "n_clicks"),
#     prevent_initial_call=True
# )


# @app.callback(
#     Output("grid_treat_compare", "rowData"),
#     Input("grid_absolute", "cellValueChanged"),
#     State("grid_treat_compare", "rowData"),
# )
# def Change_absolute(value_change, rawdat):
#     rawdat = pd.DataFrame(rawdat)

#     if value_change is not None:
#         col_id = value_change[0]['colId']
#         value = value_change[0]['value']

#         # Check for valid input
#         if value is not None and value != 'Enter a value' and col_id in ['Outcome 1', 'Outcome 2']:
#             value_risk = int(value)
#             # rawdat['ab_out1'] = value_risk
#             # Determine the correct RR value based on Outcome
#             if col_id == 'Outcome 1':
#                 rr_column = 'RR'
#                 ab_column = 'ab_out1'
#             elif col_id == 'Outcome 2':
#                 rr_column = 'RR_out2'
#                 ab_column = 'ab_out2'
            
#             # Calculate the risk treatment and the absolute risk
#             risk_treat = value_risk * rawdat[rr_column]
#             risk_treat = risk_treat.astype(int)  # Ensure it's an integer
#             abrisk = risk_treat - value_risk

#             rawdat[ab_column] = [
#                     f"{ab} more \nper 1000" if ab > 0 else f"{abs(ab)} less \nper 1000"
#                     for ab in abrisk
#                 ]
#             # Update the absolute risk column with appropriate text
#             # for i in range(rawdat.shape[0]):
#             #     rawdat.loc[i,'ab_out1'] = f"{i} more per 1000" if abrisk[i] > 0 else f"{abs(abrisk[i])} less per 1000"

#     return rawdat.to_dict("records")

# from tools.skt_table import df_origin

# @app.callback(Output("grid_treat_compare", "rowData"),
#               [Input('cytoscape_skt2', 'selectedNodeData'),
#               Input('cytoscape_skt2', 'selectedEdgeData')
#                ],
#             #   State("grid_treat_compare", "rowData")
#               )
# def filter_data(node_data, edge_data):
#     rowdata = df_origin

#     if node_data or edge_data:
#         slctd_nods = {n['id'] for n in node_data} if node_data else set()
#         slctd_edgs = [e['source'] + e['target'] for e in edge_data] if edge_data else []
#         rowdata = rowdata[(rowdata.Treatment.isin(slctd_nods) & rowdata.Reference.isin(slctd_nods))
#                     | ((rowdata.Treatment + rowdata.Reference).isin(slctd_edgs) | (rowdata.Reference + rowdata.Treatment).isin(slctd_edgs))]

#     return rowdata.to_dict("records")

#########unitil here#############

@app.callback(
    Output("skt_modal_compare_simple", "is_open"), 
    Input("grid_treat_compare", "cellClicked"),
    Input("close_compare_simple", "n_clicks"),
)

def display_sktinfo(cell, _):
    if ctx.triggered_id == "close_compare_simple":
        return False
    if cell is None or len(cell) == 0:  
        return False
    else:
        if ('colId' in cell and (cell['colId'] == "RR"or cell['colId'] == "RR_out2") and cell['value']is not None):
            return True
    return no_update



from tools.functions_modal_info import display_modal_barplot

@app.callback(
    Output("barplot_compare", "figure"),
    Output("modal_info_head", "children"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData')
)

def display_sktinfo(cell,value,rowdata):
    return display_modal_barplot(cell,value,rowdata)



from tools.functions_modal_info import display_modal_text
@app.callback(
    # Output("risk_range", "children"),
    Output("text_info_col", "children"),
    Input("grid_treat_compare", "cellClicked"), 
    Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData')
)

def display_textinfo(cell,value,rowdata):
    return display_modal_text(cell,value,rowdata)

from tools.functions_modal_info import display_modal_data

@app.callback(
    Output("modal_treat_compare", "rowData"),
    Input("grid_treat_compare", "cellClicked"), 
    # Input("simple_abvalue", "value"),
    State('grid_treat_compare','rowData'),
    State('modal_treat_compare','rowData')
)

def display_modaldata(cell,rowdata,rowdata_modal):
    return display_modal_data(cell,rowdata,rowdata_modal)



@app.callback(
    Output("quickstart-grid", "dashGridOptions"),
    Input("grid-printer-layout-btn", "n_clicks"),
    Input("grid-regular-layout-btn", "n_clicks"),
    State("quickstart-grid", "dashGridOptions")
)
def toggle_layout(print, regular, options): 
    if ctx.triggered_id == "grid-printer-layout-btn":
        options['domLayout']="print"
        return  options
    options['domLayout']=None
    return  options


#####################chatbot#######################################################

# from tools.functions_chatbot import *

# @app.callback(
#     Output(component_id="display-conversation", component_property="children"), 
#     Input(component_id="store-conversation", component_property="data")
# )
# def update_display(chat_history):
#     return [
#         render_textbox(x, box="human") if i % 2 == 0 else render_textbox(x, box="AI")
#         for i, x in enumerate(chat_history.split("<split>")[:-1])
#     ]

# @app.callback(
#     Output(component_id="user-input", component_property="value"),
#     Input(component_id="submit", component_property="n_clicks"), 
#     Input(component_id="user-input", component_property="n_submit"),
# )
# def clear_input(n_clicks, n_submit):
#     return ""

# @app.callback(
#     Output(component_id="store-conversation", component_property="data"), 
#     Output(component_id="loading-component", component_property="children"),
#     Input(component_id="submit", component_property="n_clicks"), 
#     Input(component_id="user-input", component_property="n_submit"),
#     State(component_id="user-input", component_property="value"), 
#     State(component_id="store-conversation", component_property="data"),
# )
# def run_chatbot(n_clicks, n_submit, user_input, chat_history):
#     if n_clicks == 0 and n_submit is None:
#         return "", None

#     if user_input is None or user_input == "":
#         return chat_history, None
    
#     chat_history += f"Human: {user_input}<split>ChatBot: "
#     # result_ai = conversation.predict(input=user_input)
#     # model_output = result_ai.strip()
#     result_ai = chain.invoke({"text": f"base on {chat_history},{user_input}. Please generate less than 100 words (20-50 wloud be good) and be concise and clear. avoiding the use of bullet points, asterisks (*), or any special formatting."})
#     model_output = result_ai.content
#     chat_history += f"{model_output}<split>"
#     return chat_history, None






####################################################################
####################################################################
############################ MAIN ##################################
####################################################################
####################################################################


if __name__ == '__main__':
    # app._favicon = ("assets/favicon.ico")
    # app.title = 'NMAstudio' #TODO: title works fine locally, does not on Heroku
    # context = generate_ssl_perm_and_key(cert_name='cert.pem', key_name='key.pem')
    # app.run_server(debug=False, ssl_context=context)
    app.run_server(port=8080, debug=True) #change port or remove if needed
    # app.run_server(host="macas.lan", port=8080, debug=True) #change port or remove if needed





