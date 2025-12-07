import pandas as pd
import plotly.express as px, plotly.graph_objects as go
import numpy as np


def update_indirect_direct(row):
    if pd.isna(row["direct"]):
        row["indirect"] = pd.NA
    elif pd.isna(row["indirect"]):
        row["direct"] = pd.NA
    return row


def __skt_options_forstplot(
    value_effect, df, lower, scale_lower, scale_upper, refer_name
):
    # df = df.sort_values(by='Reference')
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx / 19, "Reference"] = df.loc[idx, "Reference"]

    # new_rows['Treatment'] = 'Scale'
    new_rows["risk"] = "Enter a number"
    new_rows["Scale_lower"] = "Enter a value for lower"
    new_rows["Scale_upper"] = "Enter a value for upper"
    new_rows["RR"] = "RR"
    new_rows["direct"] = "RR"
    new_rows["indirect"] = "RR"
    new_rows["p-value"] = "0.75\n(Global)"
    interval = 19
    insert_index = 0
    lower = float(lower)
    for _, row in new_rows.iterrows():
        df = pd.concat(
            [df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]
        ).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):
        data_ex = df[j + 1 : j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        # up_rng_max = 10**np.floor(np.log10(up_rng_max))
        # low_rng_min = 10 ** np.floor(np.log10(low_rng_min))
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()
        # up_mix_max = 10**np.floor(np.log10(up_mix_max))
        # low_mix_min = 10 ** np.floor(np.log10(low_mix_min))

        if (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is not None
        ):
            range_scale = [np.log10(scale_lower), np.log10(scale_upper)]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is None
        ):
            range_scale = [np.log10(scale_lower), np.log10(max(up_rng_max, up_mix_max))]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is None
            and scale_upper is not None
        ):
            range_scale = [
                np.log10(min(low_rng_min, 0.1, low_mix_min)),
                np.log10(scale_upper),
            ]
        else:
            range_scale = [
                np.log10(min(low_rng_min, 0.1, low_mix_min)),
                np.log10(max(up_rng_max, 10, up_mix_max)),
            ]

        # print(range_scale) if j == 0  else 0
        fig = go.Figure(go.Scatter(y=[], x=[]))

        tick0 = 10 ** range_scale[0] + 0.1
        tick_end = 10 ** range_scale[1] - 1

        tick_values1 = np.linspace(tick0, 1, num=5).round(2)
        tick_values2 = np.linspace(1, tick_end, num=5).astype(int)
        tick_values = np.concatenate((tick_values1, tick_values2[1:]))
        # Insert 1 at the beginning of the array
        # tick_values = np.insert(tick_values, 0, 1)
        # dtick=(tick_end - tick0) / 9
        fig.update_layout(
            xaxis=dict(
                range=range_scale,
                tickmode="auto",
                tickformat=".1f",
                # tickvals=tick_values
            ),
            dragmode=False,
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
            plot_bgcolor="rgba(0,0,0,0)",
            height=100,
            margin=dict(l=0, r=0),
        )
        fig.update_xaxes(
            ticks="outside",
            type="log",
            showgrid=False,
            # autorange=True,
            showline=True,
            # tickcolor='rgba(0,0,0,0)',
            linecolor="black",
        )

        df.at[j, "Graph"] = fig

        num_line = len(value_effect) + 1

        for i in range(j + 1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            filter_df = pd.concat([filter_df] * num_line, ignore_index=True)
            filter_df["name"] = ""
            for index, value in enumerate(reversed(value_effect)):
                if value == "PI":
                    dif = np.log(filter_df.CI_upper[index]) - np.log(
                        filter_df["RR"][index]
                    )
                    CI_upper = np.exp(np.log(filter_df["RR"][index]) + (dif + 0.2))
                    CI_lower = np.exp(np.log(filter_df["RR"][index]) - (dif + 0.2))
                    filter_df["CI_width_hf"][index] = CI_upper - filter_df["RR"][index]
                    filter_df["lower_error"][index] = filter_df["RR"][index] - CI_lower
                    filter_df["name"][index] = "PI"

                else:
                    filter_df["Treatment"][index] = value
                    filter_df["RR"][index] = filter_df[value][index]
                    filter_df["CI_width_hf"][index] = (
                        filter_df[f"{value}_up"][index] - filter_df[value][index]
                    )
                    filter_df["lower_error"][index] = (
                        filter_df[value][index] - filter_df[f"{value}_low"][index]
                    )
                    filter_df["name"][index] = value

            up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
            up_rng = 10 ** np.floor(np.log10(up_rng))

            colors = {
                "indirect": "#ABB2B9",
                "direct": "#707B7C",
                "PI": "red",
                "other": "black",
            }

            hovert_template = {
                "indirect": "indirect estimate with CI" + "<extra></extra>",
                "direct": "direct estimate with CI" + "<extra></extra>",
                "PI": "mixed estimate with CI & PI" + "<extra></extra>",
                "other": "mixed estimate with CI & PI" + "<extra></extra>",
            }

            fig = go.Figure()
            for idx in range(filter_df.shape[0]):
                data_point = filter_df.iloc[idx]
                if np.isnan(data_point["RR"]):
                    continue
                name = data_point["name"]
                (
                    fig.add_trace(
                        go.Scatter(
                            x=[data_point["RR"]],
                            y=[data_point["Treatment"]],
                            # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                            error_x=dict(
                                type="data",
                                color=colors[name]
                                if name in colors
                                else colors["other"],
                                array=[data_point["CI_width_hf"]],
                                arrayminus=[data_point["lower_error"]],
                                visible=True,
                            ),
                            marker=dict(
                                color=colors[name]
                                if name in colors
                                else colors["other"],
                                size=8,
                            ),
                            showlegend=False,
                            hovertemplate=hovert_template[name]
                            if name in hovert_template
                            else hovert_template["other"],
                        )
                    ),
                )
                fig.update_xaxes(
                    ticks="outside",
                    type="log",
                    range=range_scale,
                )

            fig.update_layout(
                barmode="group",
                bargap=0.25,
                xaxis=dict(range=range_scale, type="log"),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
                showlegend=False,
                yaxis_visible=False,
                yaxis_showticklabels=False,
                xaxis_visible=False,
                xaxis_showticklabels=False,
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=True,
                height=80,  # Set the height to 82 pixels
                # width=200,  # Set the width to 200 pixels
                shapes=[
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=f"{1 + lower}",
                        y0="0",
                        x1=f"{1 - lower}",
                        y1="1",
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below",
                    ),
                ],
                # template="plotly_dark",
            )

            fig.add_trace(
                go.Scatter(
                    x=[1 - lower, 1 + lower],  # x-coordinate in the middle of the shape
                    y=[
                        0,
                        0,
                    ],  # y-coordinate (doesn't matter, since it's vertical shape)
                    mode="markers",
                    marker=dict(color="rgba(0, 0, 0, 0)", size=5),
                    hovertemplate="<b>Range of equivalence</b>: %{x} <extra></extra>",
                    hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)"),
                )
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
                plot_bgcolor="rgba(0,0,0,0)",
            )

            fig.add_shape(
                type="line",
                yref="paper",
                y0=0,
                y1=1,
                xref="x",
                x0=1,
                x1=1,
                line=dict(color="green", width=2, dash="dot"),
                layer="below",
            )

            # fig.update_xaxes(type="log")

            df.at[i, "Graph"] = fig

    return df


def __skt_mix_forstplot(df, lower, scale_lower, scale_upper, refer_name):
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx / 19, "Reference"] = df.loc[idx, "Reference"]
    new_rows["Treatment"] = "Scale"
    new_rows["risk"] = "Enter a number"
    new_rows["Scale_lower"] = "Enter a value for lower"
    new_rows["Scale_upper"] = "Enter a value for upper"
    new_rows["RR"] = "RR"
    lower = float(lower)
    interval = 19
    insert_index = 0
    for _, row in new_rows.iterrows():
        df = pd.concat(
            [df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]
        ).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):
        data_ex = df[j + 1 : j + 20]
        up_rng_max, low_rng_min = data_ex.CI_upper.mean(), data_ex.CI_lower.mean()
        up_mix_max, low_mix_min = data_ex.RR.max(), data_ex.RR.min()

        if (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is not None
        ):
            range_scale = [np.log10(scale_lower), np.log10(scale_upper)]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is None
        ):
            range_scale = [
                np.log10(scale_lower),
                np.log10(max(up_rng_max, 10, up_mix_max)),
            ]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is None
            and scale_upper is not None
        ):
            range_scale = [
                np.log10(min(low_rng_min, 0.1, low_mix_min)),
                np.log10(scale_upper),
            ]
        else:
            range_scale = [
                np.log10(min(low_rng_min, 0.1, low_mix_min)),
                np.log10(max(up_rng_max, 10, up_mix_max)),
            ]

        tick0 = 10 ** range_scale[0] + 0.1
        tick_end = 10 ** range_scale[1] - 1

        tick_values1 = np.linspace(tick0, 1, num=5).round(2)
        tick_values2 = np.linspace(1, tick_end, num=5).astype(int)
        tick_values = np.concatenate((tick_values1, tick_values2[1:]))

        fig = go.Figure(go.Scatter(y=[], x=[]))
        fig.update_layout(
            xaxis=dict(range=range_scale, type="log", tickvals=tick_values),
            dragmode=False,
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
            plot_bgcolor="rgba(0,0,0,0)",
            height=100,
            margin=dict(l=0, r=0),
        )
        fig.update_xaxes(
            ticks="outside",
            showgrid=False,
            autorange=True,
            showline=True,
            # tickcolor='rgba(0,0,0,0)',
            linecolor="black",
        )

        df.at[j, "Graph"] = fig

        for i in range(j + 1, j + 20):
            filterDf = df.iloc[i]
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)

            hovert_template = [
                "mixed estimate with CI" + "<extra></extra>",
            ]

            fig = go.Figure()
            for idx in range(filter_df.shape[0]):
                data_point = filter_df.iloc[idx]
                if np.isnan(data_point["RR"]):
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=[data_point["RR"]],
                        y=[data_point["Treatment"]],
                        # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                        error_x=dict(
                            type="data",
                            color="black",
                            array=[data_point["CI_width_hf"]],
                            arrayminus=[data_point["lower_error"]],
                            visible=True,
                        ),
                        marker=dict(color="black", size=8),
                        showlegend=False,
                        hovertemplate=hovert_template[idx],
                    )
                )

            fig.update_layout(
                barmode="group",
                bargap=0.25,
                xaxis=dict(range=range_scale, type="log"),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
                showlegend=False,
                yaxis_visible=False,
                yaxis_showticklabels=False,
                xaxis_visible=False,
                xaxis_showticklabels=False,
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=True,
                height=95,  # Set the height to 82 pixels
                # width=200,  # Set the width to 200 pixels
                shapes=[
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=f"{1 + lower}",
                        y0="0",
                        x1=f"{1 - lower}",
                        y1="1",
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below",
                    ),
                ],
                # template="plotly_dark",
            )

            fig.add_trace(
                go.Scatter(
                    x=[1 - lower, 1 + lower],  # x-coordinate in the middle of the shape
                    y=[
                        0,
                        0,
                    ],  # y-coordinate (doesn't matter, since it's vertical shape)
                    mode="markers",
                    marker=dict(color="rgba(0, 0, 0, 0)", size=5),
                    hovertemplate="<b>Range of equivalence</b>: %{x} <extra></extra>",
                    hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)"),
                )
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
                plot_bgcolor="rgba(0,0,0,0)",
            )

            fig.add_shape(
                type="line",
                yref="paper",
                y0=0,
                y1=1,
                xref="x",
                x0=1,
                x1=1,
                line=dict(color="green", width=2, dash="dot"),
                layer="below",
            )

            fig.update_xaxes(type="log")

            df.at[i, "Graph"] = fig

    # new_row.loc[0, 'Graph'] = df.iloc[1]['Graph']
    return df


def __skt_ab_forstplot(
    risk, value_effect, df, lower, scale_lower, scale_upper, refer_name
):
    # df = df.sort_values(by='Reference')
    new_rows = pd.DataFrame(columns=df.columns)
    for idx in range(0, 380, 19):
        new_rows.loc[idx / 19, "Reference"] = df.loc[idx, "Reference"]

    # new_rows['Treatment'] = 'Scale'
    new_rows["risk"] = "Enter a number"
    new_rows["Scale_lower"] = "Enter a value for lower"
    new_rows["Scale_upper"] = "Enter a value for upper"
    new_rows["RR"] = "RR"
    new_rows["direct"] = "RR"
    new_rows["indirect"] = "RR"
    new_rows["p-value"] = "0.75\n(Global)"
    interval = 19
    insert_index = 0
    lower = float(lower)
    for _, row in new_rows.iterrows():
        df = pd.concat(
            [df.iloc[:insert_index], row.to_frame().T, df.iloc[insert_index:]]
        ).reset_index(drop=True)
        insert_index += interval + 1  # Move to the next insertion position

    for j in range(0, 400, 20):
        data_ex = df[j + 1 : j + 20]
        risk = (
            risk
            if refer_name is not None and data_ex["Reference"].iloc[0] == refer_name
            else 20
        )
        data_ex["abs"] = data_ex["RR"] * risk - risk
        data_ex["abs_low"] = data_ex["CI_lower"] * risk - risk
        data_ex["abs_up"] = data_ex["CI_upper"] * risk - risk
        up_rng_max, low_rng_min = data_ex.abs_up.max(), data_ex.abs_low.min()
        # up_rng_max = 10**np.floor(np.log10(up_rng_max))
        # low_rng_min = 10 ** np.floor(np.log10(low_rng_min))
        up_mix_max, low_mix_min = data_ex["abs"].max(), data_ex["abs"].min()
        # up_mix_max = 10**np.floor(np.log10(up_mix_max))
        # low_mix_min = 10 ** np.floor(np.log10(low_mix_min))
        if (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is not None
        ):
            range_scale = [scale_lower, scale_upper]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is not None
            and scale_upper is None
        ):
            range_scale = [scale_lower, max(up_rng_max, up_mix_max)]
        elif (
            refer_name is not None
            and refer_name == df["Reference"][j + 1]
            and scale_lower is None
            and scale_upper is not None
        ):
            range_scale = [min(low_rng_min, low_mix_min), scale_upper]
        else:
            range_scale = [min(low_rng_min, low_mix_min), max(up_rng_max, up_mix_max)]

        fig = go.Figure(go.Scatter(y=[], x=[]))

        # tick0 = range_scale[0] + 1
        # tick_end = range_scale[1] - 1

        # tick_values1 = np.linspace(tick0, 1, num=5).round(2)
        # tick_values2 = np.linspace(1, tick_end, num=5).astype(int)
        # tick_values = np.concatenate((tick_values1, tick_values2[1:]))
        # Insert 1 at the beginning of the array
        # tick_values = np.insert(tick_values, 0, 1)
        # dtick=(tick_end - tick0) / 9

        fig.update_layout(
            xaxis=dict(
                range=range_scale,
                # tickvals=tick_values
            ),
            dragmode=False,
            showlegend=False,
            yaxis_visible=False,
            yaxis_showticklabels=False,
            autosize=True,
            paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
            plot_bgcolor="rgba(0,0,0,0)",
            height=100,
            margin=dict(l=0, r=0),
        )
        fig.update_xaxes(
            ticks="outside",
            #  type="log",
            showgrid=False,
            # autorange=True,
            showline=True,
            # tickcolor='rgba(0,0,0,0)',
            linecolor="black",
        )

        df.at[j, "Graph"] = fig

        num_line = len(value_effect) + 1

        for i in range(j + 1, j + 20):
            filterDf = df.iloc[i]
            risk = (
                risk
                if refer_name is not None and filterDf["Reference"] == refer_name
                else 20
            )
            filter_df = pd.DataFrame([filterDf])
            filter_df = filter_df.apply(update_indirect_direct, axis=1)
            filter_df["direct"]
            filter_df = pd.concat([filter_df] * num_line, ignore_index=True)
            filter_df["abs"] = filter_df["RR"] * risk - risk
            filter_df["abs_low"] = filter_df["CI_lower"] * risk - risk
            filter_df["abs_up"] = filter_df["CI_upper"] * risk - risk
            filter_df["CI_width_hf"] = filter_df.abs_up - filter_df["abs"]
            filter_df["lower_error"] = filter_df["abs"] - filter_df.abs_low
            filter_df["name"] = ""
            for index, value in enumerate(reversed(value_effect)):
                if value == "PI":
                    CI_upper = filter_df["abs_up"][index] + 0.2
                    CI_lower = filter_df["abs_low"][index] - 0.2
                    filter_df["CI_width_hf"][index] = CI_upper - filter_df["abs"][index]
                    filter_df["lower_error"][index] = filter_df["abs"][index] - CI_lower
                    filter_df["name"][index] = "PI"

                else:
                    filter_df["Treatment"][index] = value
                    filter_df["abs"][index] = filter_df[value][index]
                    filter_df["CI_width_hf"][index] = (
                        filter_df[f"{value}_up"][index] * risk
                        - filter_df[value][index] * risk
                    )
                    filter_df["lower_error"][index] = (
                        filter_df[value][index] * risk
                        - filter_df[f"{value}_low"][index] * risk
                    )
                    filter_df["name"][index] = value

            # up_rng, low_rng = df.CI_upper.max(), df.CI_lower.min()
            # up_rng = up_rng+1

            colors = {
                "indirect": "#ABB2B9",
                "direct": "#707B7C",
                "PI": "red",
                "other": "black",
            }

            hovert_template = {
                "indirect": "indirect estimate with CI" + "<extra></extra>",
                "direct": "direct estimate with CI" + "<extra></extra>",
                "PI": "mixed estimate with CI & PI" + "<extra></extra>",
                "other": "mixed estimate with CI & PI" + "<extra></extra>",
            }

            fig = go.Figure()
            for idx in range(filter_df.shape[0]):
                data_point = filter_df.iloc[idx]
                if np.isnan(data_point["abs"]):
                    continue
                name = data_point["name"]
                (
                    fig.add_trace(
                        go.Scatter(
                            x=[data_point["abs"]],
                            y=[data_point["Treatment"]],
                            # error_x_minus=dict(type='data',color = colors[i],array='lower_error',visible=True),
                            error_x=dict(
                                type="data",
                                color=colors[name]
                                if name in colors
                                else colors["other"],
                                array=[data_point["CI_width_hf"]],
                                arrayminus=[data_point["lower_error"]],
                                visible=True,
                            ),
                            marker=dict(
                                color=colors[name]
                                if name in colors
                                else colors["other"],
                                size=8,
                            ),
                            showlegend=False,
                            hovertemplate=hovert_template[name]
                            if name in hovert_template
                            else hovert_template["other"],
                        )
                    ),
                )
                fig.update_xaxes(
                    ticks="outside",
                    # type="log",
                    range=range_scale,
                )

            fig.update_layout(
                barmode="group",
                bargap=0.25,
                xaxis=dict(range=range_scale),
                # xaxis=dict(range=[min(low_rng_min, -10), up_rng_max]),
                showlegend=False,
                yaxis_visible=False,
                yaxis_showticklabels=False,
                xaxis_visible=False,
                xaxis_showticklabels=False,
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=True,
                height=80,  # Set the height to 82 pixels
                # width=200,  # Set the width to 200 pixels
                shapes=[
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=f"{0 + lower}",
                        y0="0",
                        x1=f"{0 - lower}",
                        y1="1",
                        fillcolor="orange",
                        opacity=0.4,
                        line_width=0,
                        layer="below",
                    ),
                ],
                # template="plotly_dark",
            )

            fig.add_trace(
                go.Scatter(
                    x=[0 - lower, 0 + lower],  # x-coordinate in the middle of the shape
                    y=[
                        0,
                        0,
                    ],  # y-coordinate (doesn't matter, since it's vertical shape)
                    mode="markers",
                    marker=dict(color="rgba(0, 0, 0, 0)", size=5),
                    hovertemplate="<b>Range of equivalence</b>: %{x} <extra></extra>",
                    hoverlabel=dict(bgcolor="rgba(255, 165, 0, 0.4)"),
                )
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",  # transparent bg
                plot_bgcolor="rgba(0,0,0,0)",
            )

            fig.add_shape(
                type="line",
                yref="paper",
                y0=0,
                y1=1,
                xref="x",
                x0=0,
                x1=0,
                line=dict(color="green", width=2, dash="dot"),
                layer="below",
            )

            # fig.update_xaxes(type="log")

            df.at[i, "Graph"] = fig

    return df
