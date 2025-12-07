"""
SKT (Knowledge Translation) ranking plot functions.
Separated from functions_ranking_plots.py to keep SKT-specific code isolated.
"""

import pandas as pd
import plotly.figure_factory as ff


def __ranking_plot_skt():
    """Generate ranking heatmap for SKT (Knowledge Translation) page."""
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
        direction = net_storage[f"outcome{i + 1}_direction"].iloc[1]
        reverse = direction != "beneficial"
        outcome_direction.append(reverse)
        if reverse:
            df1[f"pscore{i + 1}"] = 1 - df1[f"pscore{i + 1}"]

    # Sort and prepare data for plotting
    df1 = df1.sort_values(by="pscore1", ascending=False)
    treatments = tuple(str(t) for t in df1.treatment)

    # Add text annotations if manageable size
    if len(treatments) < 22:
        z_text = tuple(
            tuple(df1[f"pscore{i + 1}"].round(2).astype(str).values)
            for i in range(out_number)
        )
    else:
        z_text = tuple(tuple([""] * len(treatments)) for _ in range(out_number))

    pscores = tuple(tuple(df1[f"pscore{i + 1}"]) for i in range(out_number))

    # Generate and return heatmap
    fig = __ranking_heatmap_skt(treatments, pscores, outcomes, z_text)
    return fig


def __ranking_heatmap_skt(treatments, pscores, outcomes, z_text):
    """Generate heatmap figure for SKT ranking."""
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
        paper_bgcolor="rgba(0,0,0,0)",
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
    fig.layout.margin = dict(l=0, r=0, t=70, b=180)

    return fig
