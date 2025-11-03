import plotly.express as px, plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc, dash_html_components as html
import numpy as np

def display_modal_barplot(cell, value, rowdata):
    # print(cell)
    if cell is None or len(cell) == 0: 
        fig = go.Figure(data=[], layout={})
        header = html.P("") 
        return fig, header
    
    rowdata = pd.DataFrame(rowdata)
    if ('colId' in cell and (cell['colId'] == "RR" or cell['colId'] == "RR_out2")):
        first_part = cell['value'].split('\n')[0]
        rr = float(first_part)
        row_idx = cell['rowIndex']
        treatment = rowdata.loc[row_idx, 'Treatment']
        compare = rowdata.loc[row_idx, 'Reference']
        header = html.P(f"{treatment} VS {compare}")
    else: 
        fig = go.Figure(data=[], layout={})
        header = html.P("") 
        return fig, header

    annotations = []

    if value:
        value = int(value)
        ab_treat = int(rr*value)
        x_data = [ab_treat, value]
        y_data = [treatment, compare]
        y_value_dict = {category: index for index, category in enumerate(y_data)}
        fig = go.Figure(go.Bar(
            x=x_data,
            y=y_data,
            marker_color=['rgb(241,197,13)', ' rgb(128, 191, 69)'],
            orientation='h'))
        for yd, xd in zip(y_data, x_data):
            yd_position = y_value_dict[yd]
            annotations.append(dict(xref='x', yref='y',
                                        x=xd/2, y=yd_position+0.5,
                                        text=str(xd) + ' per 1000',
                                        font=dict(family='Arial', size=14,
                                                color='black'),
                                        showarrow=False))
        
    else:
        ab_treat = int(rr*20)
        x_data = [ab_treat, 20]
        y_data = [treatment, compare]
        y_value_dict = {category: index for index, category in enumerate(y_data)}
        fig = go.Figure(go.Bar(
            x=x_data,
            y=y_data,
            marker_color=['rgb(241,197,13)', ' rgb(128, 191, 69)'],
            orientation='h'))
        for yd, xd in zip(y_data, x_data):
            yd_position = y_value_dict[yd]
            annotations.append(dict(xref='x', yref='y',
                                        x=xd/2, y=yd_position+0.5,
                                        text=str(xd) + ' per 1000',
                                        font=dict(family='Arial', size=14,
                                                color='black'),
                                        showarrow=False))
    
    fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=20, b=20),
            width = 350,
            height = 150,
            autosize=True,
            bargap=0.3,
            bargroupgap=0.2,
            annotations=annotations,
            xaxis=dict(showgrid=False,
                        showline=False,
                        showticklabels=False,
                        zeroline=False,)
        )
    
   
    return fig, header


def display_modal_text(cell,value,rowdata):
    if cell is None or len(cell) == 0: 
        # risk_range = html.P("") 
        info_col = html.Span('')
        return info_col
    
    rowdata = pd.DataFrame(rowdata)
    if ('colId' in cell and (cell['colId'] == "RR"or cell['colId'] == "RR_out2")):
        row_idx = cell['rowIndex']
        
        if value:
            value = int(value)
        else:
            value = 20
        
        if cell['colId'] == "RR":
            out = 'PASI90'
            rr_low = rowdata.loc[row_idx, 'CI_lower']
            rr_up = rowdata.loc[row_idx, 'CI_upper']
        else:
            out = 'SAE'
            rr_low = rowdata.loc[row_idx, 'CI_lower_out2']
            rr_up = rowdata.loc[row_idx, 'CI_upper_out2']
        
        first_part = cell['value'].split('\n')[0]
        rr = float(first_part)

        treatment = rowdata.loc[row_idx, 'Treatment']
        compare = rowdata.loc[row_idx, 'Reference']
        
        ab_treat = int(rr*value)
        ab_diff = ab_treat-value
        span_diff = f"{ab_diff} more per 1000" if ab_diff > 0 else f"{abs(ab_diff)} less per 1000"
        
        ab_diff_low = int(rr_low*value)-value
        span_diff_low = f"{ab_diff_low} more" if ab_diff_low > 0 else f"{abs(ab_diff_low)} less"

        ab_diff_up = int(rr_up*value)-value
        span_diff_up = f"{ab_diff_up} more" if ab_diff_up > 0 else f"{abs(ab_diff_up)} less"
    
    else:
        return ''
    
    span1 = html.Span(f"Outcome: {out}", className="skt_span_info2", id="treat_comp")
    span2 = html.Span(f"Treatment: {treatment}", className="skt_span_info2", id="num_RCT")
    span3 = html.Span(f"Comparator: {compare}", className="skt_span_info2", id="num_RCT")
    span4 = html.Span(
                        f"Absolute difference: {span_diff}", 
                        className="skt_span_info2", 
                        id="num_sample"
                    )
    span5 = html.Span(
                       f"CI: {span_diff_low} to {span_diff_up}",
                        className="skt_span_info2",
                        id="mean_modif"
                        )
    children = [span1, span2, span3, span4, span5]

    return children

def display_modal_data(cell, rowdata, rowdata_modal):
    # Convert rowdata to DataFrame
    rowdata = pd.DataFrame(rowdata)
    rowdata_modal = pd.DataFrame(rowdata_modal)

    
    # Return original rowdata if no cell or invalid cell
    if not cell or len(cell) == 0:
        return rowdata_modal.to_dict("records")
    
    # Load modal data
    df_modal = pd.read_csv('db/psoriasis_wide_complete1.csv')

    # Check if the column is 'RR'
    if (cell.get('colId') == "RR" or cell.get('colId') == "RR_out2"):
        # Extract relative risk (RR) value from the cell's value
        rr = float(cell['value'].split('\n')[0])
        row_idx = cell['rowIndex']
        treatment = rowdata.loc[row_idx, 'Treatment']
        compare = rowdata.loc[row_idx, 'Reference']
        
        # Filter df_modal based on selected treatments and comparisons
        filtered_df = df_modal[
            ((df_modal['treat1'] == treatment) & (df_modal['treat2'] == compare)) |
            ((df_modal['treat1'] == compare) & (df_modal['treat2'] == treatment))
        ]
        
        if cell.get('colId') == "RR":
        # Filter out rows with missing TE1 values
            filtered_df = filtered_df[filtered_df['TE1'].notna()]
            
            # Calculate TE1 and RR values
            filtered_df['TE_up'] = filtered_df['TE1'] + 1.96 * filtered_df['seTE1']
            filtered_df['TE_low'] = filtered_df['TE1'] - 1.96 * filtered_df['seTE1']  # Correction for low bound
            filtered_df['RR'] = np.exp(filtered_df['TE1'])
        
        else:
            filtered_df = filtered_df[filtered_df['TE2'].notna()]
            
            # Calculate TE1 and RR values
            filtered_df['TE_up'] = filtered_df['TE2'] + 1.96 * filtered_df['seTE2']
            filtered_df['TE_low'] = filtered_df['TE2'] - 1.96 * filtered_df['seTE2']  # Correction for low bound
            filtered_df['RR'] = np.exp(filtered_df['TE2'])
        
        
        filtered_df['RR_up'] = np.exp(filtered_df['TE_up'])
        filtered_df['RR_low'] = np.exp(filtered_df['TE_low'])

        # Adjust rows where 'treat1' and 'treat2' need to be swapped
        mask = (filtered_df['treat1'] == compare) & (filtered_df['treat2'] == treatment)
        filtered_df.loc[mask, ['treat1', 'treat2']] = filtered_df.loc[mask, ['treat2', 'treat1']].values
        # Invert the RR and associated values for swapped treatments
        for col in ['TE1', 'TE_up', 'TE_low', 'RR', 'RR_up', 'RR_low']:
            filtered_df.loc[mask, col] = 1 / filtered_df.loc[mask, col]
        filtered_df.loc[mask, ['RR_up', 'RR_low']] = filtered_df.loc[mask, ['RR_low', 'RR_up']].values
        # if value:
        #     value = int(value)
        #     abrisk = (value * filtered_df['RR'] - value).astype(int)
        # else:
        #     abrisk = (20 * filtered_df['RR'] - 20).astype(int)
        

    else:
        # If not the 'RR' column, return original rowdata
        return rowdata_modal.to_dict("records")
    
    # filtered_df['ab_diff'] = abrisk.apply(lambda x: f"{x} more per 1000" if x > 0 else f"{abs(x)} less per 1000")
    
    if not filtered_df.empty:
        filtered_df['RR_ci'] = filtered_df.apply(
            lambda row: f"{round(row['RR'], 2)}\n({round(row['RR_low'], 2)} to {round(row['RR_up'], 2)})", 
            axis=1
        )
    else:
        # Add an empty column 'RR_ci' since the DataFrame is empty
        filtered_df['RR_ci'] = pd.Series(dtype='str')
     # Replace 'bias' values with descriptive terms
    filtered_df['bias'] = filtered_df['bias'].replace({'L': 'Low', 'M': 'Moderate', 'H': 'High'})

    # Add 'ntc' and 'link' columns
    filtered_df['ntc'] = 'NTC00001'
    filtered_df['link'] = 'https://www.nejm.org/doi/10.1056/NEJMoa1314258?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%20%200www.ncbi.nlm.nih.gov'

    # Return the filtered DataFrame as a dictionary
    return filtered_df.to_dict("records")
