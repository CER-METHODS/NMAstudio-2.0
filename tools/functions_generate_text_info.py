import pandas as pd
import numpy as np
import dash_core_components as dcc
from dash import html
import dash_bootstrap_components as dbc

def __generate_text_info__(nodedata, edgedata):
    # Default message
    text = dbc.Toast(
        [
        dcc.Upload(
                    html.A('Upload treatments instructions',
                           className = 'treat-instruct'),
                id='treat-instruction-upload', 
                multiple=False,
                style={'display': 'inline-block', 
                       'font-size': '12px', 
                       'padding-top': '12px', 
                       'margin-right': '-30px'}),
        html.Br(),
        html.Span('First, upload a CSV file with two columns: one for the treatment name and one for the treatment description. Then you can click a node to see the treatment details. You can also view the comparison info by clicking an edge without uploading a file.')
        ],
        style={
            'justify-items': 'center',
            'align-items': 'center',
            'text-align': 'center',
            'font-weight': 'bold'
        }
    )

    # ---- NODE INFO ----
    if nodedata:
        selected_id = nodedata[0]["id"]

        df = pd.read_csv("db/psoriasis_wide_complete1.csv")
        n_rct = df[(df["treat1"] == selected_id) | (df["treat2"] == selected_id)]
        num_RCT = f"Randomized controlled trials: {len(n_rct)}"

        fullname_df = pd.read_csv('db/skt/fullname.csv')
        fullname = fullname_df.loc[
            fullname_df['Abbreviation'] == selected_id, 'Treatment'
        ].iloc[0]

        describ_df = pd.read_csv('db/skt/instruction.csv')
        des_treat = describ_df .loc[
            describ_df ['treat'] == selected_id, 'describ'
        ].iloc[0]

        treat_info = html.Span(
            selected_id + f' ({fullname})',
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )
        numRCT_info = html.Span(
            num_RCT,
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )
        treat_desc = html.Span(
            des_treat,
            style={'display': 'grid', 'margin': '2%'}
        )

        text = dbc.Toast([treat_info, numRCT_info, treat_desc])

    # ---- EDGE INFO ----
    if edgedata:
        source = edgedata[0]['source']
        target = edgedata[0]['target']

        df_n_rct = pd.read_csv('db/skt/final_all.csv')
        n_rct = df_n_rct.loc[
            ((df_n_rct['Treatment'] == source) & (df_n_rct['Reference'] == target) | (df_n_rct['Treatment'] == target) & (df_n_rct['Reference'] == source)),
            'k'
        ]
        n_rct_value = n_rct.iloc[0] if not n_rct.empty else np.nan
        num_RCT = f'Randomized controlled trials: {n_rct_value}'

        df_total = pd.read_csv('db/psoriasis_wide_complete1.csv')
        pair_set = {(source, target), (target, source)}

        dat_extract = df_total[
            df_total.apply(lambda row: (row['treat1'], row['treat2']) in pair_set, axis=1)
        ]

        n_total = dat_extract['n11'].sum() + dat_extract['n21'].sum()
        num_sample = f'Total participants: {n_total}'

        mean_age = round(dat_extract['age'].mean(), 2)
        mean_gender = round(
            (dat_extract['male'] / (dat_extract['n11'] + dat_extract['n21'])).mean(),
            2
        )

        comp_info = html.Span(
            f"Treatment: {source}, Comparator: {target}",
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )

        numRCT_info = html.Span(
            num_RCT,
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )
        sample_info = html.Span(
            num_sample,
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )

        mod_title = html.Span(
            'Potential Modifiers Info',
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )

        modifiers_info = html.Span(
            f"Mean age: {mean_age}\nMean male percentage: {mean_gender}",
            style={'display': 'grid', 
                   'text-align': 'center',
                   'white-space': 'pre'
                   }
        )

        text = dbc.Toast([comp_info, numRCT_info, sample_info, html.Br(),mod_title, modifiers_info])

    return text