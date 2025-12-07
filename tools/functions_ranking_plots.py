import numpy as np, pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# Conditional sklearn import to handle scipy compatibility issues
try:
    from sklearn.cluster import KMeans

    SKLEARN_AVAILABLE = True
except (ImportError, TypeError) as e:
    SKLEARN_AVAILABLE = False
    KMeans = None
    print(f"Warning: sklearn not available: {e}")

from collections import Counter
from io import StringIO
from functools import lru_cache
from tools.utils import get_net_data_json


# @lru_cache(maxsize=None)
# def __ranking_plot(ranking_data,net_data):
#     df = pd.read_json(ranking_data, orient='split')
#     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Remove unnamed columns
#     outcomes = ("Outcome 1", "Outcome 2")
#     net_storage = pd.read_json(get_net_data_json(net_data), orient='split')

#     outcome_direction_data1 = net_storage['outcome1_direction'].iloc[1]
#     outcome_direction_1 = False if outcome_direction_data1 == 'beneficial' else True
#     outcome_direction_2 = False  # True=harmful

#     df1 = df.copy(deep=True)

#     if "pscore2" in df1.columns:
#         outcome_direction_data2 = net_storage['outcome2_direction'].iloc[1]
#         outcome_direction_2 = False if outcome_direction_data2 == 'beneficial' else True

#         if outcome_direction_1: df1.pscore1 = 1 - df1.pscore1.values
#         if outcome_direction_2: df1.pscore2 = 1 - df1.pscore2.values
#         df1 = df1.sort_values(by=["pscore1", "pscore2"], ascending=[False, False])
#         treatments = tuple(df1.treatment)
#         if type(treatments[1])==int: treatments = tuple([str(c) + "\0" for c in treatments])
#         z_text = (tuple(df1.pscore1.round(2).astype(str).values),
#                   tuple(df1.pscore2.round(2).astype(str).values)) if len(treatments) < 22 else  (('', ) * len(treatments), ('', ) * len(treatments))
#         pscores = (tuple(df1.pscore1), tuple(df1.pscore2))
#     else:
#         pscore = 1 - df1.pscore if outcome_direction_1 else df1.pscore
#         pscore = pscore.sort_values(ascending=False)
#         elements = pd.DataFrame({"pscore" : pscore, "treat" : df1.treatment})
#         sorted_elements = elements.sort_values(by="pscore", ascending=False)
#         strd_pscore = sorted_elements['pscore']
#         strd_trt = sorted_elements['treat']
#         treatments = tuple(strd_trt)
#         if type(treatments[1])==int: treatments = tuple([str(c) + "\0" for c in treatments])
#         z_text = (tuple(strd_pscore.round(2).astype(str).values), ) if len(sorted_elements) < 22 else  (('', ) * len(sorted_elements),)
#         pscores = (tuple(strd_pscore),)
#         outcomes = ("Outcome", )  if len(sorted_elements) < 22 else ("", )


#     #################### heatmap ####################
#     fig = __ranking_heatmap(treatments, pscores, outcomes, z_text)

#     ######################### scatter plot #########################
#     fig2 = __ranking_scatter(df, net_data, outcome_direction_1, outcome_direction_2)

#     return fig, fig2


def __ranking_plot(ranking_data, out_number, out_idx1, options, out_idx2, net_data):
    """Generate ranking heatmap and scatter plot for outcomes.

    Args:
        ranking_data: List of JSON strings with ranking data for each outcome
        out_number: Number of outcomes
        out_idx1: Index of primary outcome (0-based)
        options: List of dicts with 'label' key for outcome names
        out_idx2: Index of secondary outcome (0-based)
        net_data: Network data storage dict
    """
    # Guard against missing data
    if not ranking_data or not net_data:
        empty_fig = px.scatter()
        empty_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return empty_fig, empty_fig

    try:
        df = pd.read_json(StringIO(ranking_data[0]), orient="split")
        # merged_ranking_data = df
        for i, json_path in enumerate(ranking_data[1:], start=2):
            df2 = pd.read_json(StringIO(json_path), orient="split")
            # Rename the pscore column to pscorei, where i is the loop index
            df2 = df2.rename(columns={"pscore": f"pscore{i}"})
            df = pd.merge(df, df2, on="treatment", how="outer")

        out_number = len(ranking_data)

        df = df.rename(columns={"pscore": "pscore1"})
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Remove unnamed columns

        # Use outcome names from options if available
        if options and len(options) >= out_number:
            outcomes = tuple(f"{options[i]['label']}" for i in range(out_number))
        else:
            outcomes = tuple(f"Outcome {i + 1}" for i in range(out_number))

        net_storage = pd.read_json(
            StringIO(get_net_data_json(net_data)), orient="split"
        )

        df1 = df.copy(deep=True)

        # Only access direction columns that exist in net_storage
        # The net_storage only has outcome1_direction, outcome2_direction etc. based on setup
        outcome_direction = [
            False for _ in range(out_number)
        ]  # Default to beneficial (False)
        for i in range(out_number):
            direction_col = f"outcome{i + 1}_direction"
            if direction_col in net_storage.columns:
                outcome_direction[i] = net_storage[direction_col].iloc[1]
                outcome_direction[i] = (
                    False if outcome_direction[i] == "beneficial" else True
                )
            # else: keep default False (beneficial)
            if outcome_direction[i]:
                df1[f"pscore{i + 1}"] = 1 - df1[f"pscore{i + 1}"].values

        df1 = df1.sort_values(by="pscore1", ascending=False)
        treatments = tuple(df1.treatment)
        # Check if treatments are integers (need to convert to strings for display)
        if len(treatments) > 1 and isinstance(treatments[1], (int, np.integer)):
            treatments = tuple([str(c) + "\0" for c in treatments])
        elif len(treatments) > 0 and isinstance(treatments[0], (int, np.integer)):
            treatments = tuple([str(c) + "\0" for c in treatments])
        z_text = (
            tuple(
                tuple(df1[f"pscore{i + 1}"].round(2).astype(str).values)
                for i in range(out_number)
            )
            if len(treatments) < 22
            else tuple(tuple([""] * len(treatments)) for _ in range(out_number))
        )
        pscores = tuple(tuple(df1[f"pscore{i + 1}"]) for i in range(out_number))

        # pscores = (pscores[out_idx1], pscores[out_idx2])
        # z_text = (z_text[out_idx1], z_text[out_idx2])
        #################### heatmap ####################
        fig = __ranking_heatmap(treatments, pscores, outcomes, z_text)

        ######################### scatter plot #########################
        # Get outcome labels for scatter plot axes
        if options and len(options) > out_idx1:
            label1 = options[out_idx1]["label"]
        else:
            label1 = f"Outcome {out_idx1 + 1}"
        if options and len(options) > out_idx2:
            label2 = options[out_idx2]["label"]
        else:
            label2 = f"Outcome {out_idx2 + 1}"
        outcomes2 = (label1, label2)

        if out_number < 2:
            fig2 = px.scatter()
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
                plot_bgcolor="rgba(0,0,0,0)",
            )
        else:
            # Ensure indices are within bounds
            safe_idx1 = min(out_idx1, out_number - 1) if out_idx1 is not None else 0
            safe_idx2 = (
                min(out_idx2, out_number - 1)
                if out_idx2 is not None
                else min(1, out_number - 1)
            )

            fig2 = __ranking_scatter(
                df,
                net_data,
                outcome_direction[safe_idx1],
                outcome_direction[safe_idx2],
                safe_idx1,
                safe_idx2,
                outcomes2,
            )

        return fig, fig2
    except Exception as e:
        print(f"[ERROR] __ranking_plot failed: {e}")
        import traceback

        traceback.print_exc()
        empty_fig = px.scatter()
        empty_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        return empty_fig, empty_fig


# @lru_cache(maxsize=None)
# def __ranking_heatmap(treatments, pscores, outcomes, z_text):
#     if len(pscores) + len(outcomes) + len(z_text) == 3: pscores, outcomes, z_text = list(pscores), list(outcomes), list(z_text)

#     fig = ff.create_annotated_heatmap(pscores, x=treatments, y=outcomes,
#                                       reversescale=True,
#                                       annotation_text=z_text, colorscale= 'Viridis',
#                                       hoverongaps=False)
#     for annotation in fig.layout.annotations: annotation.font.size = 9
#     fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
#                       plot_bgcolor='rgba(0,0,0,0)',
#                       modebar= dict(orientation = 'h', bgcolor = 'rgba(0,0,0,0.5)'),
#                       xaxis=dict(showgrid=False, autorange=True, title='',
#                                  tickmode='linear', type="category"),
#                       yaxis=dict(showgrid=False, autorange=True, title='', range=[0,len(outcomes)]),
#                       )

#     fig['layout']['xaxis']['side'] = 'bottom'
#     fig['data'][0]['showscale'] = True
#     fig['layout']['yaxis']['autorange'] = "reversed"
#     #fig['layout']['xaxis']['autorange'] = "reversed"
#     fig.layout.margin = dict(l=0, r=0, t=70, b=180)

#     return fig


# def __ranking_scatter(df, net_data, outcome_direction_1, outcome_direction_2):
#     net_data = pd.read_json(get_net_data_json(net_data), orient='split')

#     if 'pscore2' in df.columns:
#         df = df.dropna()
#         if outcome_direction_1: df.pscore1 = 1 - df.pscore1
#         if outcome_direction_2: df.pscore2 = 1 - df.pscore2

#         kmeans = KMeans(n_clusters=int(round(len(df.treatment) / float(5.0), 0)),
#                         init='k-means++', max_iter=300, n_init=10, random_state=0)
#         labels = kmeans.fit(df[['pscore1', 'pscore2']])
#         df['Trt groups'] = labels.labels_.astype(str)
#         df_full = net_data.groupby(['treat1', 'treat2']).TE.count().reset_index()
#         df_full_2 = net_data.groupby(['treat1', 'treat2']).TE2.count().reset_index()
#         node_weight, node_weight_2 = {}, {}
#         for treat in df.treatment:
#             n1 = df_full[df_full.treat1 == treat].TE.sum()
#             n2 = df_full[df_full.treat2 == treat].TE.sum()
#             node_weight[treat] = (n1 + n2) / float(np.shape(df)[0])

#             n1 = df_full_2[df_full_2.treat1 == treat].TE2.sum()
#             n2 = df_full_2[df_full_2.treat2 == treat].TE2.sum()
#             node_weight_2[treat] = (n1 + n2) / float(np.shape(df)[0])

#         sum_weight = dict((Counter(node_weight) + Counter(node_weight_2)))
#         mean_weight = {k: v / 2.0 for k, v in
#                        sum_weight.items()}  # Node size prop to mean count of node size in outcome 1 and outcome 2
#         df["node weight"] = df["treatment"].map(mean_weight)

#         fig2 = px.scatter(df, x="pscore1", y="pscore2",
#                           color="Trt groups", size='node weight',
#                           hover_data=["treatment"],
#                           text='treatment')

#         fig2.update_layout(coloraxis_showscale=True,
#                            showlegend=False,
#                            paper_bgcolor='rgba(0,0,0,0)',  # transparent bg
#                            plot_bgcolor='rgba(0,0,0,0)',
#                            modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0.5)'),
#                            xaxis=dict(showgrid=False, autorange=True, dtick=0.1,
#                                       tickcolor='black', ticks="outside", tickwidth=1,
#                                       showline=True, linewidth=1, linecolor='black',
#                                       zeroline=False, zerolinecolor='black', zerolinewidth=1,
#                                       range=[0, 1]),
#                            yaxis=dict(showgrid=False, autorange=True, dtick=0.1,
#                                       showline=True, linewidth=1, linecolor='black',
#                                       tickcolor='black', ticks="outside", tickwidth=1,
#                                       zeroline=False, zerolinecolor='black', zerolinewidth=1,
#                                       range=[0, 1]
#                                       ))
#         fig2.update_traces(textposition='top center', textfont_size=10,
#                            marker=dict(line=dict(width=1, color='black'))
#                            )
#         fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
#         fig2.layout.margin = dict(l=30, r=30, t=10, b=80)

#     else:  # Empty scatter
#         df = pd.DataFrame([[0] * 2], columns=['pscore1', 'pscore2'])
#         fig2 = px.scatter(df, x="pscore1", y="pscore2")
#         fig2.update_shapes(dict(xref='x', yref='y'))
#         fig2.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
#         fig2.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
#         fig2.update_layout(margin=dict(l=100, r=100, t=12, b=80),
#                           xaxis=dict(showgrid=False, title=''),
#                           modebar=dict(orientation='h', bgcolor='rgba(0,0,0,0.5)'),
#                           yaxis=dict(showgrid=False, title=''),
#                           showlegend=False,
#                           coloraxis_showscale=False,
#                           paper_bgcolor='rgba(0,0,0,0)',
#                           plot_bgcolor='rgba(0,0,0,0)',
#                           autosize=True,
#                           annotations=[{"text": "Please provide a second outcome in data upload to display p-scores scatter plot",
#                                          "font": {"size": 15, "color": "black", 'family': 'sans-serif'},
#                                          "xref":"paper", "yref":"paper",
#                                          "showarrow":False},
#                                        ]
#                            ),
#         fig2.update_annotations(align="center")
#     return fig2


def __ranking_plot_skt():
    # Load ranking CSVs
    ranking_files = ["db/ranking/rank.csv", "db/ranking/rank2.csv"]
    ranking_data = [pd.read_csv(path) for path in ranking_files]

    # Start with the first ranking file
    df = ranking_data[0].copy()

    # Merge remaining ranking files
    for i, rank_df in enumerate(ranking_data[1:], start=2):
        rank_df = rank_df.rename(columns={"pscore": f"pscore{i}"})
        df = pd.merge(df, rank_df, on="treatment", how="outer")

    out_number = len(ranking_data)

    # Clean up and rename columns
    df = df.rename(columns={"pscore": "pscore1"})
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Outcomes and additional data
    outcomes = ["PASI90", "SAE"]
    net_storage = pd.read_csv("db/psoriasis_wide_complete.csv", encoding="iso-8859-1")

    # Adjust scores based on outcome direction
    df1 = df.copy(deep=True)
    outcome_direction = []
    for i in range(out_number):
        direction = net_storage[f"outcome{i+1}_direction"].iloc[1]
        reverse = direction != "beneficial"
        outcome_direction.append(reverse)
        if reverse:
            df1[f"pscore{i+1}"] = 1 - df1[f"pscore{i+1}"]

    # Sort and prepare data for plotting
    df1 = df1.sort_values(by="pscore1", ascending=False)
    treatments = tuple(str(t) for t in df1.treatment)

    # Add text annotations if manageable size
    if len(treatments) < 22:
        z_text = tuple(
            tuple(df1[f"pscore{i+1}"].round(2).astype(str).values)
            for i in range(out_number)
        )
    else:
        z_text = tuple(tuple([""] * len(treatments)) for _ in range(out_number))

    pscores = tuple(tuple(df1[f"pscore{i+1}"]) for i in range(out_number))

    # Generate and return heatmap
    fig = __ranking_heatmap(treatments, pscores, outcomes, z_text)
    return fig




def __ranking_heatmap(treatments, pscores, outcomes, z_text):
    if len(pscores) + len(outcomes) + len(z_text) == 3:
        pscores, outcomes, z_text = list(pscores), list(outcomes), list(z_text)

    fig = ff.create_annotated_heatmap(
        pscores,
        x=treatments,
        y=outcomes,
        reversescale=True,
        annotation_text=z_text,
        colorscale="Viridis",
        hoverongaps=False,
    )
    for annotation in fig.layout.annotations:
        annotation.font.size = 12
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
        plot_bgcolor="rgba(0,0,0,0)",
        modebar=dict(orientation="h", bgcolor="rgba(0,0,0,0.5)"),
        xaxis=dict(
            showgrid=False, autorange=True, title="", tickmode="linear", type="category"
        ),
        yaxis=dict(showgrid=False, autorange=True, title="", range=[0, len(outcomes)]),
    )

    fig["layout"]["xaxis"]["side"] = "bottom"
    fig["data"][0]["showscale"] = True
    fig["layout"]["yaxis"]["autorange"] = "reversed"
    # fig['layout']['xaxis']['autorange'] = "reversed"
    fig.layout.margin = dict(l=0, r=0, t=70, b=180)

    return fig


def __ranking_scatter(
    df,
    net_data_storage,
    outcome_direction_1,
    outcome_direction_2,
    out_idx1,
    out_idx2,
    outcomes,
):
    """Generate ranking scatter plot comparing two outcomes.

    Args:
        df: DataFrame with pscore columns
        net_data_storage: Network data storage dict with "data" key
        outcome_direction_1: Direction for outcome 1 (True=harmful, False=beneficial)
        outcome_direction_2: Direction for outcome 2 (True=harmful, False=beneficial)
        out_idx1: Index of outcome 1 (0-based)
        out_idx2: Index of outcome 2 (0-based)
        outcomes: Tuple of (label1, label2) for axis labels
    """
    net_data = pd.read_json(
        StringIO(get_net_data_json(net_data_storage)), orient="split"
    )

    if out_idx1 != out_idx2:
        df = df.dropna()
        if outcome_direction_1:
            df[f"pscore{out_idx1 + 1}"] = 1 - df[f"pscore{out_idx1 + 1}"]
        if outcome_direction_2:
            df[f"pscore{out_idx2 + 1}"] = 1 - df[f"pscore{out_idx2 + 1}"]

        if SKLEARN_AVAILABLE and KMeans is not None:
            kmeans = KMeans(
                n_clusters=int(round(len(df.treatment) / float(5.0), 0)),
                init="k-means++",
                max_iter=300,
                n_init=10,
                random_state=0,
            )
            labels = kmeans.fit(df[[f"pscore{out_idx1 + 1}", f"pscore{out_idx2 + 1}"]])
            df["Trt groups"] = labels.labels_.astype(str)
        else:
            # Fallback: assign all to same group if sklearn unavailable
            df["Trt groups"] = "0"
        df_full = (
            net_data.groupby(["treat1", "treat2"])[f"TE{out_idx1 + 1}"]
            .count()
            .reset_index()
        )
        df_full_2 = (
            net_data.groupby(["treat1", "treat2"])[f"TE{out_idx2 + 1}"]
            .count()
            .reset_index()
        )
        node_weight, node_weight_2 = {}, {}
        for treat in df.treatment:
            n1 = df_full[df_full.treat1 == treat][f"TE{out_idx1 + 1}"].sum()
            n2 = df_full[df_full.treat2 == treat][f"TE{out_idx1 + 1}"].sum()
            node_weight[treat] = (n1 + n2) / float(np.shape(df)[0])

            n1 = df_full_2[df_full_2.treat1 == treat][f"TE{out_idx2 + 1}"].sum()
            n2 = df_full_2[df_full_2.treat2 == treat][f"TE{out_idx2 + 1}"].sum()
            node_weight_2[treat] = (n1 + n2) / float(np.shape(df)[0])

        sum_weight = dict((Counter(node_weight) + Counter(node_weight_2)))
        mean_weight = {
            k: v / 2.0 for k, v in sum_weight.items()
        }  # Node size prop to mean count of node size in outcome 1 and outcome 2
        df["node weight"] = df["treatment"].map(mean_weight)

        fig2 = px.scatter(
            df,
            x=f"pscore{out_idx1 + 1}",
            y=f"pscore{out_idx2 + 1}",
            color="Trt groups",
            size="node weight",
            hover_data=["treatment"],
            text="treatment",
        )

        # Set axis labels from outcome names
        fig2.update_layout(
            xaxis_title=f"{outcomes[0]}",
            yaxis_title=f"{outcomes[1]}",
        )

        fig2.update_layout(
            coloraxis_showscale=True,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
            plot_bgcolor="rgba(0,0,0,0)",
            modebar=dict(orientation="h", bgcolor="rgba(0,0,0,0.5)"),
            xaxis=dict(
                showgrid=False,
                autorange=True,
                dtick=0.1,
                tickcolor="black",
                ticks="outside",
                tickwidth=1,
                showline=True,
                linewidth=1,
                linecolor="black",
                zeroline=False,
                zerolinecolor="black",
                zerolinewidth=1,
                range=[0, 1],
            ),
            yaxis=dict(
                showgrid=False,
                autorange=True,
                dtick=0.1,
                showline=True,
                linewidth=1,
                linecolor="black",
                tickcolor="black",
                ticks="outside",
                tickwidth=1,
                zeroline=False,
                zerolinecolor="black",
                zerolinewidth=1,
                range=[0, 1],
            ),
        )
        fig2.update_traces(
            textposition="top center",
            textfont_size=12,
            marker=dict(line=dict(width=1, color="black")),
        )
        fig2.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
        fig2.layout.margin = dict(l=30, r=30, t=10, b=80)

    else:  # Empty scatter
        df = pd.DataFrame([[0] * 2], columns=["pscore1", "pscore2"])
        fig2 = px.scatter(df, x="pscore1", y="pscore2")
        fig2.update_shapes(dict(xref="x", yref="y"))
        fig2.update_xaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        fig2.update_yaxes(tickvals=[], ticktext=[], visible=False, zeroline=False)
        (
            fig2.update_layout(
                margin=dict(l=100, r=100, t=12, b=80),
                xaxis=dict(showgrid=False, title=""),
                modebar=dict(orientation="h", bgcolor="rgba(0,0,0,0.5)"),
                yaxis=dict(showgrid=False, title=""),
                showlegend=False,
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                autosize=True,
                annotations=[
                    {
                        "text": "Please provide a second outcome in data upload to display p-scores scatter plot",
                        "font": {"size": 15, "color": "black", "family": "sans-serif"},
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                    },
                ],
            ),
        )
        fig2.update_annotations(align="center")
    return fig2

