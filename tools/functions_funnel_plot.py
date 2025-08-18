import pandas as pd, numpy as np
import plotly.express as px


def __Tap_funnelplot(node, outcome_idx, funnel_data):
    EMPTY_DF = pd.DataFrame([],
                            columns=[ 'index', 'studlab', 'treat1', 'treat2', '',
                            'TE_direct', 'TE_adj', 'seTE', 'Comparison'])
    if node:

        treatment = node[0]['label']
        funnel_data = pd.read_json(funnel_data[outcome_idx if outcome_idx else 0], orient='split')
        # funnel_data_out2 = pd.read_json(funnel_data_out2, orient='split') if outcome2 else None #TODO: change when include dataselectors for var names
        # df = funnel_data_out2[funnel_data_out2.treat2 == treatment].copy() if outcome2 else funnel_data[funnel_data.treat2 == treatment].copy()
        df = funnel_data[funnel_data.treat2 == treatment].copy()

        df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)

        #remove comparisons with one study only
        df = df[df['Comparison'].map(df['Comparison'].value_counts()) > 1]
        effect_size = df.columns[3]
        df = df.sort_values(by='seTE', ascending=False)

    else:
        effect_size = ''
        df = EMPTY_DF

    max_y = df.seTE.max()+0.2 if not np.isnan(df.seTE.max()) else 0.2
    range_x = [min(df.TE_adj)-3, max(df.TE_adj)+3] if not np.isnan(df.TE_adj.max()) else None

    fig = px.scatter(df,
                     x="TE_adj", y="seTE", #log_x=xlog,
                     range_x=range_x,
                     range_y=[0.01, max_y+10],
                     symbol="Comparison", color="Comparison",
                     color_discrete_sequence = px.colors.qualitative.Light24)

    fig.update_traces(marker=dict(size=6, # #symbol='circle',
                      line=dict(width=1, color='black')),
                       )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')

    if node:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          coloraxis_showscale=False,
                          showlegend=True,
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0.5)'),
                          autosize=True,
                          margin=dict(l=10, r=5, t=20, b=60),
                          xaxis=dict(showgrid=False, autorange=False, zeroline=False,
                                     title='',showline=True, linewidth=1, linecolor='black'),
                          yaxis=dict(showgrid=False, autorange=False, title='Standard Error',
                                     showline=True, linewidth=1, linecolor='black',
                                     zeroline=False,
                                     ),
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False,
                                        text= 'Log' f'{effect_size} ' ' centered at comparison-specific pooled effect' if effect_size in ['OR','RR'] else f'{effect_size}' ' centered at comparison-specific pooled effect'
                                            )],

                          )
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=0, x1=0,
                      line=dict(color="black", width=1), layer='below')

        fig.add_shape(type='line', y0=max_y, x0= -1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 1.96 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= -2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= 2.58 * max_y, y1=0, x1=0,
                      line=dict(color="black", dash='dot', width=1.5))

        fig.update_yaxes(autorange="reversed", range=[max_y,0])


    if not node:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zeroline=False, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          coloraxis_showscale=False,
                          showlegend=False,
                          modebar = dict(orientation='h', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig



def __Tap_funnelplot_normal(edge, outcome_idx, net_data, pw_data):
    outcome_idx = int(outcome_idx)+1 if outcome_idx else 1
    EMPTY_DF = pd.DataFrame([],
                            columns=[ 'index', 'studlab', 'treat1', 'treat2', '',
                            f'TE{outcome_idx}', f'seTE{outcome_idx}', 'Comparison'])
    if edge and len(edge) == 1:
        slctd_edgs = set(e['source'] + e['target'] for e in edge)
        net_data = pd.read_json(net_data[0], orient='split')

        df = net_data[(net_data.treat1 + net_data.treat2).isin(slctd_edgs)].copy()
        df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)

        # remove comparisons with one study only
        df = df[df['Comparison'].map(df['Comparison'].value_counts()) > 1]

        if df.empty:
            effect_size = ''
            df = EMPTY_DF
        else:
            effect_size = df.iloc[0][f"effect_size{outcome_idx}"]
            df = df.sort_values(by=f'seTE{outcome_idx}', ascending=False)

            pw_data = pd.read_json(pw_data[outcome_idx - 1], orient='split')

            # get the unique treat1-treat2 combination from df
            t1, t2 = df.iloc[0][['treat1', 'treat2']]

            # find matching TE_diamond from pw_data
            diamond = pw_data.loc[
                (pw_data['treat1'] == t1) & (pw_data['treat2'] == t2),
                'TE_diamond'
            ].iloc[0]

            diamond = np.log(diamond)

    else:   
        effect_size = ''
        df = EMPTY_DF

    max_y = df[f'seTE{outcome_idx}'].max()+0.2 if not np.isnan(df[f'seTE{outcome_idx}'].max()) else 0.2
    range_x = [min(df[f'TE{outcome_idx}'])-3, max(df[f'TE{outcome_idx}'])+3] if not np.isnan(df[f'TE{outcome_idx}'].max()) else None

    fig = px.scatter(df,
                     x=f'TE{outcome_idx}', y=f'seTE{outcome_idx}', #log_x=xlog,
                     range_x=range_x,
                     range_y=[0.01, max_y+10],
                     symbol="Comparison", color="Comparison",
                     color_discrete_sequence = px.colors.qualitative.Light24)

    fig.update_traces(marker=dict(size=6, # #symbol='circle',
                      line=dict(width=1, color='black')),
                       )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
                      plot_bgcolor='rgba(0,0,0,0)')

    if edge and not df.empty:
        fig.update_layout(clickmode='event+select',
                          font_color="black",
                          coloraxis_showscale=False,
                          showlegend=True,
                          modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0.5)'),
                          autosize=True,
                          margin=dict(l=10, r=5, t=20, b=60),
                          xaxis=dict(showgrid=False, autorange=False, zeroline=False,
                                     title='',showline=True, linewidth=1, linecolor='black'),
                          yaxis=dict(showgrid=False, autorange=False, title='Standard Error',
                                     showline=True, linewidth=1, linecolor='black',
                                     zeroline=False,
                                     ),
                          annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
                                        showarrow=False,
                                        text= 'Log' f'{effect_size} ' ' centered at comparison-specific pooled effect' if effect_size in ['OR','RR'] else f'{effect_size}' ' centered at comparison-specific pooled effect'
                                            )],

                          )
        fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0= diamond, x1=diamond,
                      line=dict(color="black", width=1), layer='below')

        fig.add_shape(type='line', y0=max_y, x0= diamond -1.96 * max_y, y1=0, x1=diamond,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= diamond + 1.96 * max_y, y1=0, x1=diamond,
                      line=dict(color="black", dash='dashdot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= diamond -2.58 * max_y, y1=0, x1=diamond,
                      line=dict(color="black", dash='dot', width=1.5))
        fig.add_shape(type='line', y0=max_y, x0= diamond + 2.58 * max_y, y1=0, x1=diamond,
                      line=dict(color="black", dash='dot', width=1.5))

        fig.update_yaxes(autorange="reversed", range=[max_y,0])


    if not edge and df.empty:
        fig.update_shapes(dict(xref='x', yref='y'))
        fig.update_xaxes(zeroline=False, title='', visible=False)
        fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
        fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
                          coloraxis_showscale=False,
                          showlegend=False,
                          modebar = dict(orientation='h', bgcolor='rgba(0,0,0,0)'))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig





# def __Tap_funnelplot(node, edge, outcome_idx, funnel_data):
#     EMPTY_DF = pd.DataFrame([],
#                             columns=[ 'index', 'studlab', 'treat1', 'treat2', '',
#                             'TE_direct', 'TE_adj', 'seTE', 'Comparison'])
#     if node or edge:
#         if node:
#             treatment = node[0]['label']
#             funnel_data = pd.read_json(funnel_data[outcome_idx if outcome_idx else 0], orient='split')
#             df = funnel_data[funnel_data.treat2 == treatment].copy()

#         else:
#             slctd_edgs = set(e['source'] + e['target'] for e in edge) if edge else set()
#             funnel_data = pd.read_json(funnel_data[outcome_idx if outcome_idx else 0], orient='split')
#             df = funnel_data[(funnel_data.treat1 + funnel_data.treat2).isin(slctd_edgs)].copy()
        
#         df['Comparison'] = (df['treat1'] + ' vs ' + df['treat2']).astype(str)
#         #remove comparisons with one study only
#         df = df[df['Comparison'].map(df['Comparison'].value_counts()) > 1]
#         effect_size = df.columns[3]
#         df = df.sort_values(by='seTE', ascending=False)

#     else:
#         effect_size = ''
#         df = EMPTY_DF

#     max_y = df.seTE.max()+0.2 if not np.isnan(df.seTE.max()) else 0.2
#     range_x = [min(df.TE_adj)-3, max(df.TE_adj)+3] if not np.isnan(df.TE_adj.max()) else None

#     fig = px.scatter(df,
#                      x="TE_adj", y="seTE", #log_x=xlog,
#                      range_x=range_x,
#                      range_y=[0.01, max_y+10],
#                      symbol="Comparison", color="Comparison",
#                      color_discrete_sequence = px.colors.qualitative.Light24)

#     fig.update_traces(marker=dict(size=6, # #symbol='circle',
#                       line=dict(width=1, color='black')),
#                        )
#     fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
#                       plot_bgcolor='rgba(0,0,0,0)')

#     if node or edge:
#         fig.update_layout(clickmode='event+select',
#                           font_color="black",
#                           coloraxis_showscale=False,
#                           showlegend=True,
#                           modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0.5)'),
#                           autosize=True,
#                           margin=dict(l=10, r=5, t=20, b=60),
#                           xaxis=dict(showgrid=False, autorange=False, zeroline=False,
#                                      title='',showline=True, linewidth=1, linecolor='black'),
#                           yaxis=dict(showgrid=False, autorange=False, title='Standard Error',
#                                      showline=True, linewidth=1, linecolor='black',
#                                      zeroline=False,
#                                      ),
#                           annotations=[dict(x=0, ax=0, y=-0.12, ay=-0.1, xref='x', axref='x', yref='paper',
#                                         showarrow=False,
#                                         text= 'Log' f'{effect_size} ' ' centered at comparison-specific pooled effect' if effect_size in ['OR','RR'] else f'{effect_size}' ' centered at comparison-specific pooled effect'
#                                             )],

#                           )
#         fig.add_shape(type='line', yref='paper', y0=0, y1=1, xref='x', x0=0, x1=0,
#                       line=dict(color="black", width=1), layer='below')

#         fig.add_shape(type='line', y0=max_y, x0= -1.96 * max_y, y1=0, x1=0,
#                       line=dict(color="black", dash='dashdot', width=1.5))
#         fig.add_shape(type='line', y0=max_y, x0= 1.96 * max_y, y1=0, x1=0,
#                       line=dict(color="black", dash='dashdot', width=1.5))
#         fig.add_shape(type='line', y0=max_y, x0= -2.58 * max_y, y1=0, x1=0,
#                       line=dict(color="black", dash='dot', width=1.5))
#         fig.add_shape(type='line', y0=max_y, x0= 2.58 * max_y, y1=0, x1=0,
#                       line=dict(color="black", dash='dot', width=1.5))

#         fig.update_yaxes(autorange="reversed", range=[max_y,0])


#     if not (node or edge):
#         fig.update_shapes(dict(xref='x', yref='y'))
#         fig.update_xaxes(zeroline=False, title='', visible=False)
#         fig.update_yaxes(tickvals=[], ticktext=[], visible=False)
#         fig.update_layout(margin=dict(l=100, r=100, t=12, b=80),
#                           coloraxis_showscale=False,
#                           showlegend=False,
#                           modebar = dict(orientation='h', bgcolor='rgba(0,0,0,0)'))
#         fig.update_traces(hoverinfo='skip', hovertemplate=None)

#     return fig
