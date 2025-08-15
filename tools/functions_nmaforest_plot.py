import numpy as np, pandas as pd
import plotly.express as px, plotly.graph_objects as go
from plotly.colors import qualitative

def __TapNodeData_fig(data, outcome_idx, forest_data,  pw_forest_data, style, pi, add_tau, net_storage):


    if data:
        treatment = data[0]['label']
        if outcome_idx:
             i = int(outcome_idx)
            #  forest_data = forest_data[i]
             forest_data = pd.read_json(forest_data[i], orient='split')
             pw_forest_data = pd.read_json(pw_forest_data[i], orient='split')

        else:          
            i = 0
            forest_data = pd.read_json(forest_data[i], orient='split')
            pw_forest_data = pd.read_json(pw_forest_data[i], orient='split')

        df = forest_data[forest_data.Reference == treatment]
        # Step 1: Create sorted keys for both dataframes
        df["key"] = df.apply(lambda x: tuple(sorted([x["Treatment"], x["Reference"]])), axis=1)
        pw_forest_data["key"] = pw_forest_data.apply(lambda x: tuple(sorted([x["treat1"], x["treat2"]])), axis=1)

        # Step 2: Drop duplicates in data2 since tau2 is same for each pair
        pw_forest_unique = pw_forest_data.drop_duplicates(subset=["key"])[["key", "tau2"]].rename(columns={"tau2": "tau2_pw"})

        # Step 3: Merge
        df = df.merge(pw_forest_unique, on="key", how="left").drop(columns="key")
        net_data = pd.read_json(net_storage[0], orient='split')
        outcome_direction_data = net_data[f'outcome{i+1}_direction'].iloc[1]
        outcome_direction = False if outcome_direction_data == 'beneficial' else True
        effect_size = df.columns[1]
        tau2 = round(df['tau2'].iloc[1], 2)
        df['Treatment'] += ' ' * 23
        df['CI_width'] = (df.CI_upper - df.CI_lower)/2
        df['lower_error'] = df[effect_size] - df.CI_lower
        df['CI_width_hf'] = df.CI_upper - df[effect_size] 

        df['pre_width'] = (df.pre_upper - df.pre_lower)/2
        df['lower_error_pre'] = df[effect_size] - df.pre_lower
        df['pre_width_hf'] = df.pre_upper - df[effect_size]
        # df['CI_width_hf'] = df['CI_width'] / 2
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format),
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        pre_lower, pre_upper = df["pre_lower"].map('{:,.2f}'.format), df["pre_upper"].map('{:,.2f}'.format)
        df['PI'] = '(' + pre_lower.astype(str) + ', ' + pre_upper.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
        n = len(df)
        FOREST_ANNOTATION = ('<b>RE model:</b>'
                             + u"\u03C4" + '<sup>2</sup>='
                             + f"{'NA' if np.isnan(tau2) else tau2}")
        LEN_FOREST_ANNOT = 25 + len(str(tau2))
        style.update({'height': 200+16*(n-2)})

    else:
        effect_size = ''
        outcome_direction = False
        df = pd.DataFrame([[0] * 10], columns=['Treatment', effect_size, 'tau2_pw', 'CI_lower', 'CI_upper', 'WEIGHT',
                                              'CI_width', 'CI_width_hf','pre_width', 'pre_width_hf'])
        FOREST_ANNOTATION = ''
        LEN_FOREST_ANNOT = 0
        style.update({'height': '100%'})


    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    # up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    # low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None
    # print(up_rng, low_rng)
    # up_rng = np.log10(up_rng)
    # low_rng = np.log10(low_rng)
    # print(up_rng, low_rng)
   

    if data:
        fig=px.scatter(df, x=effect_size, y="Treatment",
                        # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                    error_x_minus='lower_error_pre' if xlog and pi else None,
                    error_x= ('pre_width_hf' if xlog else 'pre_width' )if pi else None,
                    log_x=xlog,
                    size_max=5,
                    range_x=[min(max(low_rng-0.2, 0.1), 0.9), up_rng+2] if xlog else None,
                    range_y=[-1, len(df.Treatment)],
                    size=df.WEIGHT)
        if pi:
            fig.update_traces(marker=dict(color='red'),  # Set points to black
                        error_x=dict(color='red'))

        fig.add_trace(go.Scatter(
            x=df[effect_size],  # All RR values from the dataframe
            y=df['Treatment'],  # All Treatment values from the dataframe
            error_x=dict(
                type='data',
                color='#313539',
                array=df['CI_width_hf'] if xlog else df['CI_width'],  # Apply pre_width_hf or pre_width to all points
                arrayminus=df['lower_error'] if xlog else None,  # Apply lower_error_pre if xlog is True
                visible=True
            ),
            marker=dict(color='green',opacity=0.8 if data else 0, size=8),  # Red marker with size 8 for all points
            mode='markers',  # Ensures it's a scatter plot with points
            showlegend=False
        ))

        if xlog:
            fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=1, x1=1,
                        line=dict(color="black", width=1), layer='below')
    
    else:
        fig = go.Figure()

    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                        plot_bgcolor='rgba(0,0,0,0)')

    # fig.update_traces(marker=dict(symbol='circle',
    #                               opacity=0.8 if data else 0,
    #                             #   line=dict(color='DarkSlateGrey'),
    #                               color='green'),
    #                   error_x=dict(thickness=2.1, color='#313539')  # '#ef563b' nice orange trace
    #                   )
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black',tickformat=".1f",
                     ticklen=5,
                     categoryorder='category descending' if outcome_direction else 'category ascending',
                     # dtick=1,
                     autorange=False,
                     showline=True, linewidth=1, linecolor='black',
                     zeroline=True, zerolinecolor='black')

    if data:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0.5)'),
                          autosize=True,
                        #   width=1500,
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False, autorange=False,
                                     #tick0=0, # TODO: JUST EXPLAIN IT!!!
                                     title=''),
                          yaxis=dict(showgrid=False, title=''),
                          annotations=[dict(x=0, ax=0, y=0, ay=-0.1, xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-40,
                                             showarrow=False, text=effect_size),
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1))) if xlog else df.CI_lower.min(),
                                            ax=0, y=0, ay=-0.1,
                                            xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-45,
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='green' if outcome_direction else 'black'),
                                       dict(x= np.floor(np.log10(max([up_rng, 10]))) if xlog else abs(df.CI_upper).max(),
                                            ax=0, y=0, ay=-0.1,
                                            xref='x', axref='x', yref='paper',yanchor='bottom',yshift=-45,
                                            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.8,
                                            arrowcolor='black' if outcome_direction else 'green'),  #'#751225'
                                       dict(x=np.floor(np.log10(min(low_rng, 0.1)))/2 if xlog else df.CI_lower.min()/2,
                                            y=0,  xref='x', yref='paper',yanchor='bottom',yshift=-65,
                                            text='Favours treatment' if outcome_direction else f'Favours {treatment}',
                                            showarrow=False),
                                       dict(x=np.floor(np.log10(max([up_rng, 10])))/2 if xlog else abs(df.CI_upper).max()/2,
                                            y=0,
                                            xref='x', yref='paper',yanchor='bottom',yshift=-65,
                                            text=f'Favours {treatment}'if outcome_direction else 'Favours treatment',
                                            showarrow=False),
                                       dict(x=-0.47, y=1, align='center',
                                            xref='paper', yref='paper',
                                            text='<b>Treatment</b>',
                                            showarrow=False),
                                       dict(x=-0.52, y=0, align='center',
                                            xref='paper', yref='paper',
                                            text=FOREST_ANNOTATION, #'<b>RE model:</b> ' u"\u03C4" '<sup>2</sup>=' f'{tau2}',
                                            showarrow=False),
                                 ]
                          )


        fig.add_trace(go.Scatter(x=[], y=[],
                                 marker=dict(opacity=0),
                                 showlegend=False, mode='markers',
                                 yaxis="y2"))

        if pi:
            if add_tau:
                ticktext = [
                    f" {x:.2f}   {y:<17} {z:<17} {w:.2f}"
                    for x, y, z, w in zip(df[effect_size], df["CI"], df["PI"], df["tau2_pw"])
                ]
            else:
                ticktext = [
                    f" {x:.2f}   {y:<17} {z:<17}"
                    for x, y, z in zip(df[effect_size], df["CI"], df["PI"])
                ]
        else:
            if add_tau:
                ticktext = [
                    f" {x:.2f}   {y:<17} {w:.2f}"
                    for x, y, w in zip(df[effect_size], df["CI"], df["tau2_pw"])
                ]
            else:
                ticktext = [
                    f" {x:.2f}   {y:<17}"
                    for x, y in zip(df[effect_size], df["CI"])
                ]

        fig.update_layout(
            autosize=True,
            width=1500,
            yaxis2=dict(tickvals = [*range(df.shape[0])],
                        ticktext = ticktext,
                        showgrid = False,  zeroline=False,
                        titlefont=dict(color='black'),
                        tickfont=dict(color='black'),
                        type='category',
                        range=[-1.4, df.shape[0]+1],
                        anchor="x", overlaying="y",
                        side="right"),
        ),

        fig.update_layout(yaxis_range=[-1.4, len(df["Treatment"])+1])

        fig.add_annotation(x=1.19, y=1, align='center',
             xref='paper', yref='y domain',
             text=f'<b>{effect_size}</b>',
             showarrow=False)


        fig.add_annotation(x=1.22, y=1, align='center',
                           xref='paper', yref='y2 domain',
                           text='<b>95% CI</b>',
                           showarrow=False)
        if add_tau:
            fig.add_annotation(x=1.33, y=1, align='center',
                            xref='paper', yref='y2 domain',
                            text='<b>tau2</b>',
                            showarrow=False)
        if pi:
            fig.add_annotation(x=1.32, y=1, align='center',
                            xref='paper', yref='y2 domain',
                            text='<b>95% PI</b>',
                            showarrow=False)

    else:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          margin=dict(l=5, r=10, t=12, b=80),
                          xaxis=dict(showgrid=False, tick0=0, title=''),
                          yaxis=dict(showgrid=False, title=''),
                          title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                          annotations=[]
                          )

    if not data:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          modebar= dict(orientation = 'v', bgcolor = 'rgba(0,0,0,0.5)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig, style





###### BIDIMENSIONAL PLOT

def __TapNodeData_fig_bidim(data, forest_data_store,out_idx1, out_idx2,options, directions):
    """If click on node uses node as reference to produce both forest plots."""
    ##  ranking data used to check if second outcome is present (easier to check than using dataselectors)
    # df_ranking = pd.read_json(ranking_data, orient='split')
    # df_ranking = df_ranking.loc[:, ~df_ranking.columns.str.contains('^Unnamed')]  # Remove unnamed columns
    if not out_idx1:
         out_idx1 =0
    if not out_idx2:
         out_idx2 = 0

    directions = directions if directions else ['beneficial', 'harmful']
   

    direct1 = directions[out_idx1]
    direct2 = directions[out_idx2] if out_idx2 < len(directions) else directions[out_idx1]
   

    label1 = options[out_idx1]['label']
    label2 = options[out_idx2]['label'] if out_idx2 < len(options) else options[out_idx1]['label']

    if data:
        # if "pscore2" in df_ranking.columns:

        forest_data  = pd.read_json(forest_data_store[out_idx1], orient='split')
        forest_data_out2 = pd.read_json(forest_data_store[out_idx2], orient='split')
        treatment = data[0]['label']
        df = forest_data[forest_data.Reference == treatment]
        
        effect_size = df.columns[1]
        df['lower_error_1'] = df[effect_size] - df.CI_lower
        df['CI_width'] = (df.CI_upper - df.CI_lower)/2
        df['CI_width_hf'] = df.CI_upper - df[effect_size] 
        df['WEIGHT'] = round(df['WEIGHT'], 3)
        CI_lower, CI_upper = df["CI_lower"].map('{:,.2f}'.format), df["CI_upper"].map('{:,.2f}'.format),
        df['CI'] = '(' + CI_lower.astype(str) + ', ' + CI_upper.astype(str) + ')'
        df = df.sort_values(by=effect_size, ascending=False)
        
        #second outcome
        df_second = forest_data_out2[forest_data_out2.Reference == treatment]
        effect_size_2 = df_second.columns[1]
        df_second['CI_width'] = df_second.CI_upper - df_second.CI_lower
        df_second['lower_error_2'] = df_second[effect_size] - df_second.CI_lower
        df_second['CI_width_hf'] = df_second['CI_width'] / 2
        CI_lower2, CI_upper2 = df_second["CI_lower"].map('{:,.2f}'.format), df_second["CI_upper"].map('{:,.2f}'.format),
        df_second['CI'] = '(' + CI_lower2.astype(str) + ', ' + CI_upper2.astype(str) + ')'
        # else:
        #     effect_size = effect_size_2 = ''
        #     df = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
        #                                           'CI_width', 'CI_width_hf'])
        #     df_second = pd.DataFrame([[0] * 7], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
        #                                                  'CI_width', 'CI_width_hf'])
    else:
            effect_size = effect_size_2 = ''
            df = pd.DataFrame([[0] * 8], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                                  'CI_width', 'CI_width_hf', 'CI'])
            df_second = pd.DataFrame([[0] * 8], columns=['Treatment', effect_size, 'CI_lower', 'CI_upper', 'WEIGHT',
                                                         'CI_width', 'CI_width_hf', 'CI'])

    xlog = effect_size in ('RR', 'OR')
    up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
    up_rng = 10**np.floor(np.log10(up_rng)) if xlog else None
    low_rng = 10 ** np.floor(np.log10(low_rng)) if xlog else None
    # if len(df_second.Treatment) > len(df.Treatment):
    #     trts_rmd = set(df_second.Treatment).difference(df.Treatment)
    #     df_second[df_second['Treatment'].isin(trts_rmd) == False]
    # else:
    #     trts_rmd = set(df.Treatment).difference(df_second.Treatment)
    #     df[df['Treatment'].isin(trts_rmd) == False]
    common_treatments = set(df.Treatment).intersection(df_second.Treatment)
    # Filter each dataset to keep only the common treatments
    df = df[df['Treatment'].isin(common_treatments)]
    df_second = df_second[df_second['Treatment'].isin(common_treatments)]
    df = df.sort_values(by='Treatment')
    df_second = df_second.sort_values(by='Treatment')
    df['size'] = df.Treatment.astype("category").cat.codes


    df['label1'] = [label1] * len(df)
    df['label2'] = [label2] * len(df)
    df['value1'] = ['' + '{:.2f} {:<17}'.format(x, y) 
                    for x, y in zip(df[effect_size].values, df['CI'].values)]
    df['value2'] = ['' + '{:.2f} {:<17}'.format(x, y) 
                    for x, y in zip(df_second[effect_size].values, df_second['CI'].values)]

    # Calculate number of unique treatments
    n_treatments = df['Treatment'].nunique()

    # Combine multiple qualitative color sequences to cover more treatments
    color_sequences = [
        qualitative.Plotly, qualitative.Dark24, qualitative.Light24,
        qualitative.Alphabet, qualitative.Bold, qualitative.Pastel,
        qualitative.Prism, qualitative.Safe, qualitative.Vivid,
        qualitative.Set1, qualitative.Set2, qualitative.Set3,
        qualitative.D3, qualitative.G10, qualitative.T10
    ]
    long_color_list = []
    for seq in color_sequences:
        long_color_list.extend(seq)

    # Generate distinct colors (recycle if needed)
    if n_treatments <= len(long_color_list):
        distinct_colors = long_color_list[:n_treatments]
    else:
        # Generate a rainbow spectrum as fallback
        distinct_colors = [f'hsl({int(360*i/n_treatments)}, 85%, 50%)' 
                        for i in range(n_treatments)]
        
    fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2],
                 color=df.Treatment,
                 error_x_minus=df['lower_error_1'] if xlog else None,
                 error_x='CI_width_hf' if xlog else 'CI_width' if data else None,
                 error_y_minus=df_second['lower_error_2'] if xlog else None,
                 error_y=df_second.CI_width_hf if xlog else df_second.CI_width if data else None,
                 log_x=xlog,
                 log_y=xlog,
                 size_max = 10,
                 color_discrete_sequence=distinct_colors,
                 custom_data=['Treatment','label1', 'label2', 'value1', 'value2'] if data else None, 
                 range_x=([max([up_rng, 10]), min(low_rng, 0.1)] if xlog else None) if direct1 == 'harmful' 
                         else ([min(low_rng, 0.1), max([up_rng, 10])] if xlog else None),
                 range_y=([max(df_second[effect_size_2]), min(df_second[effect_size_2])] if direct2 == 'harmful'
                         else None)
                 )
    if data:
         fig.update_traces(
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>" +  # Use color dimension for Treatment name
                    "%{customdata[1]}: %{customdata[3]}<br>" +
                    "%{customdata[2]}: %{customdata[4]}<extra></extra>"
                )
            )
    
#    # Compute first occurrence indices for each treatment
#     first_occurrence = df.reset_index().groupby('Treatment')['index'].first().to_dict()

#     color_mapping = {}

#     # Define distinct blue and red palettes for treatments
#     blue_palettes = [
#         "#0253e8",  # Strong Blue
#         "#afb1b3",  # Steel Blue
#         "#89eef0",  # Soft Cyan
#         "#05591d",  # Slate Blue
#         "#07ed6b",  # Vibrant Sea Green
#         "#20B2AA",  # Light Sea Green
#     ]

#     red_palettes = [
#         "#f5a795",  # Soft Red
#         "#FFA500",  # Vibrant Orange
#         "#7d4301",  # Brown
#         "#FF69B4",  # Hot Pink
#         "#DC143C",  # Deep Crimson
#         "#f03ad7",  # Bright Magenta
#     ]

#    # Get sorted lists of treatments grouped by type
#     single_treatments = sorted([t for t in df['Treatment'].unique() if '+' not in t])
#     combination_treatments = sorted([t for t in df['Treatment'].unique() if '+' in t])

#     color_mapping = {}

#     # Assign colors using within-group ordering
#     for idx, treatment in enumerate(single_treatments):
#         color_mapping[treatment] = blue_palettes[idx % len(blue_palettes)]

#     for idx, treatment in enumerate(combination_treatments):
#         color_mapping[treatment] = red_palettes[idx % len(red_palettes)]


#     # Assign colors and size to the DataFrame
#     df['color'] = df['Treatment'].map(color_mapping)
#     df['size'] = df['Treatment'].astype("category").cat.codes
 
#     # Example data (replace with your actual data)
#     x_min, x_max = min(df['CI_lower']), max(df['CI_upper'])
#     y_min, y_max = min(df_second['CI_lower']), max(df_second['CI_upper'])

#     # Create log-spaced ticks starting from 1 and including 1
#     # x_ticks = np.logspace(np.log10(x_min), np.log10(x_max), 10)  # 10 ticks from 1 to x_max
#     # y_ticks = np.logspace(np.log10(y_min), np.log10(y_max), 10)  # 10 ticks from 1 to y_max
#     value = [-1, -0.9, -0.8,-0.7,-0.6,-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]
#     # value = [-1.2, -0.9, -0.6, -0.3, 0, 0.3]

#     x_ticks = np.exp(value) 
#     value_y = [-0.9, -0.8,-0.7,-0.6,-0.5,-0.4, -0.3, -0.2,-0.1, 0.0, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5,0.6]
#     # value_y = [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6]
 
#     y_ticks = np.exp(value_y)
#     # # Ensure that 1 is included as the first tick
#     # if 1 not in x_ticks:
#     #     x_ticks = np.insert(x_ticks, 0, 1)

#     # if 1 not in y_ticks:
#     #     y_ticks = np.insert(y_ticks, 0, 1)

#     # Format the ticks for better readability
#     x_ticktext = [f'{val:.2f}' for val in x_ticks]
#     y_ticktext = [f'{val:.2f}' for val in y_ticks]

#     import plotly.graph_objects as go
#     # Prepare the scatter plot with individual traces for each data point
#     fig = go.Figure()
    
#     # Add a temporary column to identify treatments with '+'
#     df['is_plus'] = df['Treatment'].str.contains(r'\+').astype(int)

#     # Sort the DataFrame: treatments without '+' first, then those with '+'
#     df = df.sort_values(by='is_plus').drop(columns='is_plus')
    
#     # After sorting the DataFrame, create ordered treatment list
#     treatment_order = df['Treatment'].unique()  # Gets treatments in sorted order

#     # Then group with sort=False
#     grouped = df.groupby('Treatment', sort=False)  # <-- Add sort=False here

  
#     for treatment in treatment_order:
#         group = grouped.get_group(treatment)  # Get group for this treatment
#         color = color_mapping[treatment]
#         if df_second.loc[df_second['Treatment'] == treatment, effect_size_2].empty:
#             continue
#         # Add a single trace for all points in this treatment group
#         fig.add_trace(
#             go.Scatter(
#                 x=group[effect_size],
#                 y = df_second.loc[df_second['Treatment'] == treatment, effect_size_2],  # Ensure alignment with df_second
#                 error_x=dict(
#                     type='data',
#                     symmetric=False,
#                     array=group['CI_width_hf'] if xlog else group['CI_width'] if data else None,
#                     arrayminus=group['lower_error_1'] if xlog else None,
#                     color=color,
#                 ),
#                 error_y=dict(
#                     type='data',
#                     symmetric=False,
#                     array=df_second.loc[df_second['Treatment'] == treatment, 'CI_width_hf'] if xlog else df_second.loc[df_second['Treatment'] == treatment, 'CI_width'] if data else None,
#                     arrayminus=df_second.loc[df_second['Treatment'] == treatment, 'lower_error_2'] if xlog else None,
#                     color=color,
#                 ),
#                 mode='markers',
#                 marker=dict(
#                     size=10,
#                     color=color,
#                 ),
#                 name=treatment,  # Name the trace (appears in legend)
#                 showlegend=True  # Ensure legend is shown for this trace
#             )
#         )

#     # Update axes to match log scale if required
#     fig.update_layout(
#         xaxis=dict(
#             type="log" if xlog else "linear",
#             tickvals=x_ticks,
#             ticktext=x_ticktext,
#         ),
#         yaxis=dict(
#             type="log" if xlog else "linear",
#             tickvals=y_ticks,
#             ticktext=y_ticktext,
#         )
#     )

        
    
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                  plot_bgcolor='rgba(0,0,0,0)',
                  autosize=True,
                  modebar=dict(orientation='v', bgcolor='rgba(0,0,0,0.5)'),
                  legend=dict(itemsizing='trace', itemclick="toggle",
                              itemdoubleclick="toggleothers", # orientation='v', xanchor='auto',
                              traceorder='normal',
                              orientation='h', y=1.25, xanchor='auto',
                              font=dict(size=10)) if df['Treatment'].unique().size > 10 else
                                        dict(itemsizing='trace', itemclick="toggle", itemdoubleclick="toggleothers", orientation='v',
                      font=dict(size=10))
                  )
    if xlog:
            fig.add_hline(y=1,line=dict(color="black", width=1, dash='dashdot'))
            fig.add_vline(x=1,line=dict(color="black", width=1, dash='dashdot'))
    fig.update_traces(marker=dict(symbol='circle',
                              size=9,
                              opacity=1 if data else 0,
                              line=dict(color='black'),
                              ),
                  error_y=dict(thickness=1.3),
                  error_x=dict(thickness=1.3), ),
    fig.update_xaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                 autorange=True, showline=True, linewidth=1, linecolor='black',
                 zeroline=True, zerolinecolor='gray', zerolinewidth=1),
    fig.update_yaxes(ticks="outside", tickwidth=2, tickcolor='black', ticklen=5, dtick=1,
                 autorange=True, showline=True, linewidth=1, linecolor='black',
                 zeroline=True, zerolinecolor='gray', zerolinewidth=1),
    fig.update_layout(clickmode='event+select',
                  font_color="black",
                  margin=dict(l=10, r=10, t=12, b=80),
                  xaxis=dict(showgrid=False, tick0=0, title=f'{label1} ({effect_size})'),
                  yaxis=dict(showgrid=False, title=f'{label2} ({effect_size_2})'),
                  title_text='  ', title_x=0.02, title_y=.98, title_font_size=14,
                  )
    if not data:
            fig.update_shapes(dict(xref='x', yref='y'))
            fig.update_xaxes(zerolinecolor='black', zerolinewidth=1, title='', visible=False)
            fig.update_yaxes(tickvals=[], ticktext=[], title='', visible=False)
            fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                             coloraxis_showscale=False)  ## remove visible=False to show initial axes
            fig.update_traces(hoverinfo='skip', hovertemplate=None)
    # if data and  "pscore2" not in df_ranking.columns:
    #         fig = px.scatter(df, x=df[effect_size], y=df_second[effect_size_2])
    #         fig.update_shapes(dict(xref='x', yref='y'))
    #         fig.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
    #         fig.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
    #         fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
    #                            xaxis=dict(showgrid=False, title=''),
    #                            modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0.5)'),
    #                            yaxis=dict(showgrid=False, title=''),
    #                            showlegend=False,
    #                            coloraxis_showscale=False,
    #                            paper_bgcolor='rgba(0,0,0,0)',
    #                            plot_bgcolor='rgba(0,0,0,0)',
    #                            autosize=True,
    #                            annotations=[
    #                                {"text": "Please provide a second outcome in data upload to display bi-dimensional plot",
    #                                 "font": {"size": 15, "color": "black", 'family': 'sans-serif'},
    #                                 "xref": "paper", "yref": "paper",
    #                                 "showarrow": False},
    #                                ]
    #                            ),
    #         fig.update_annotations(align="center")
    #         fig.update_traces(hoverinfo='skip', hovertemplate=None)
    return fig