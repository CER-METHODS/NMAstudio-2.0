import pandas as pd
import numpy as np
import dash_core_components as dcc
from dash import html
import dash_bootstrap_components as dbc
import base64
import io

# def __generate_text_info__(nodedata, edgedata,  contents, filename, out_idx, net_data, effect_modifiers):
#     # Default message
#     text = dbc.Toast("Select a node or edge to see more information.")
#     # ---- NODE INFO ----
#     if nodedata:
#         selected_id = nodedata[0]["id"]
#         from tools.utils import get_net_data_json
#         df_net = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
#         # Count number of RCTs for this comparison
#         n_rct = df_net[
#             ((df_net['treat1'] == selected_id) or (df_net['treat2'] == selected_id)) 
#         ]
#         num_RCT = f"Randomized controlled trials: {len(n_rct)}"

#         # fullname_df = pd.read_csv('db/skt/fullname.csv')
#         # fullname = fullname_df.loc[
#         #     fullname_df['Abbreviation'] == selected_id, 'Treatment'
#         # ].iloc[0]
#          # decode
        
#         if contents is None or not filename.lower().endswith(".csv"):
#             treat_desc = None
        
#         else:
#             content_type, content_string = contents.split(",")
#             decoded = base64.b64decode(content_string)

#             # read csv into dataframe
#             describ_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

#             des_treat = describ_df .loc[
#                 describ_df ['treat'] == selected_id, 'describ'
#             ].iloc[0]
            
#             treat_desc = html.Span(
#                 des_treat,
#                 style={'display': 'grid', 'margin': '2%'}
#             )

#         treat_info = html.Span(
#             selected_id,
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )
#         numRCT_info = html.Span(
#             num_RCT,
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )
        

#         text = dbc.Toast([treat_info, numRCT_info, treat_desc])

#     # ---- EDGE INFO ----
#     if edgedata:
#         source = edgedata[0]['source']
#         target = edgedata[0]['target']

#         from tools.utils import get_net_data_json
#         df_net = pd.read_json(get_net_data_json(net_data), orient="split").round(3)
#         # Count number of RCTs for this comparison
#         n_rct = df_net[
#             ((df_net['treat1'] == source) & (df_net['treat2'] == target)) |
#             ((df_net['treat2'] == source) & (df_net['treat1'] == target))
#         ]

#         num_RCT = f'Randomized controlled trials: {n_rct}'

#         idx = out_idx+1 if out_idx is not None else 1
#         pair_set = {(source, target), (target, source)}

#         dat_extract = df_net[
#             df_net.apply(lambda row: (row['treat1'], row['treat2']) in pair_set, axis=1)
#         ]

#         n_total = dat_extract[f'n1{idx}'].sum() + dat_extract[f'n2{idx}'].sum()
#         num_sample = f'Total participants: {n_total}'
#         text_info = ''
#         for modif in effect_modifiers or []:
#             modif_op = modif + '1'
#             if modif or modif_op in dat_extract.columns:
#                 modif = modif_op if modif_op in dat_extract.columns else modif
#                 median_val = round(dat_extract[modif].median(), 2)
#                 text_info += f'{modif}: {median_val}\n'
        

#         modifiers_info = html.Span(
#                 text_info,
#                 style={'display': 'grid', 
#                     'text-align': 'center',
#                     'white-space': 'pre'
#                     }
#             )
        
#         comp_info = html.Span(
#             f"Treatment: {source}, Comparator: {target}",
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )

#         numRCT_info = html.Span(
#             num_RCT,
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )
#         sample_info = html.Span(
#             num_sample,
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )

#         mod_title = html.Span(
#             'Potential Modifiers Info',
#             style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
#         )

        

#         text = dbc.Toast([comp_info, numRCT_info, sample_info, html.Br(),mod_title, modifiers_info])

#     return text



def __generate_text_info__(nodedata, edgedata, instruct_data, out_idx, net_data, effect_modifiers):

    # default
    text = dbc.Toast("Select a node or edge to see more information.",
                     style={'display': 'grid', 
                            'text-align': 'center', 
                            'color':'#B85042',
                            'font-weight': 'bold'})

    # ---- READ CSV ONCE ----
    describ_df = None
    if isinstance(instruct_data, list) and len(instruct_data) > 0:
        describ_df = pd.DataFrame(instruct_data)

    from tools.utils import get_net_data_json
    df_net = pd.read_json(get_net_data_json(net_data), orient="split").round(3)

    # ---- NODE INFO ----
    if nodedata:
        selected_id = nodedata[0]["id"]

        n_rct = df_net[
            (df_net['treat1'] == selected_id) |
            (df_net['treat2'] == selected_id)
        ]

        num_RCT = f"Randomized controlled trials: {len(n_rct)}"

        treat_desc = None
        if describ_df is not None and len(describ_df) > 0:
            describ_df_clean = describ_df.copy()
            describ_df_clean.columns = [str(col).strip().lower() for col in describ_df_clean.columns]

            treatment_col = 'treatment' if 'treatment' in describ_df_clean.columns else ('treat' if 'treat' in describ_df_clean.columns else None)
            description_col = 'description' if 'description' in describ_df_clean.columns else ('describ' if 'describ' in describ_df_clean.columns else None)

            if treatment_col and description_col:
                row = describ_df_clean.loc[
                    describ_df_clean[treatment_col].astype(str).str.strip() == str(selected_id).strip(),
                    description_col,
                ]
                if not row.empty and pd.notna(row.iloc[0]):
                    treat_desc = html.Span(
                        str(row.iloc[0]),
                        style={'display': 'grid', 'margin': '2%'}
                    )

        treat_info = html.Span(
            selected_id,
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )
        numRCT_info = html.Span(
            num_RCT,
            style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
        )

        text = dbc.Toast([treat_info, numRCT_info, treat_desc])

    # ---- EDGE INFO ----
    if edgedata:
        source = edgedata[0]['source']
        target = edgedata[0]['target']

        n_rct = df_net[
            ((df_net['treat1'] == source) & (df_net['treat2'] == target)) |
            ((df_net['treat2'] == source) & (df_net['treat1'] == target))
        ]

        num_RCT = f"Randomized controlled trials: {len(n_rct)}"

        idx = (out_idx or 0) + 1
        pair_set = {(source, target), (target, source)}

        dat_extract = df_net[
            df_net.apply(lambda r: (r['treat1'], r['treat2']) in pair_set, axis=1)
        ]

        n_total = int(
            dat_extract.get(f'n1{idx}', 0).sum() +
            dat_extract.get(f'n2{idx}', 0).sum()
        )
        num_sample = f'Total participants: {n_total}'

        text_info = ""
        for modif in effect_modifiers or []:
            col = modif + '1' if modif + '1' in dat_extract.columns else modif
            if col in dat_extract.columns:
                median_val = round(dat_extract[col].median(), 2)
                text_info += f'{col}: {median_val}\n'

        modifiers_info = html.Span(
            text_info,
            style={'display': 'grid', 'text-align': 'center', 'white-space': 'pre'}
        )

        text = dbc.Toast([
            html.Span(
                f"Treatment: {source}, Comparator: {target}",
                style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
            ),
            html.Span(
                num_RCT,
                style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
            ),
            html.Span(
                num_sample,
                style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
            ),
            html.Br(),
            html.Span(
                'Potential Modifiers Info',
                style={'display': 'grid', 'text-align': 'center', 'font-weight': 'bold'}
            ),
            modifiers_info
        ])

    return text