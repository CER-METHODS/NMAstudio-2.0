"""
SKT (Knowledge Translation) Data Helpers

Functions to derive SKT page data from STORAGE components.
This replaces the hardcoded CSV file loading with dynamic data from the user's project.
"""

import pandas as pd
import numpy as np
from io import StringIO
from tools.utils import get_net_data_json, get_league_table_data_list


def get_skt_final_data(forest_data_storage, net_split_data_storage, outcome_idx=0):
    """
    Derive final_all.csv equivalent data from STORAGE.

    Combines forest_data (NMA mixed effects) with net_split_data (direct/indirect).

    Args:
        forest_data_storage: List of JSON strings, one per outcome
        net_split_data_storage: List of JSON strings with direct/indirect estimates
        outcome_idx: Which outcome to use (0-indexed)

    Returns:
        DataFrame with columns: Treatment, Reference, RR, CI_lower, CI_upper, se,
                               direct, direct_low, direct_up, indirect, indirect_low, indirect_up
    """
    if not forest_data_storage or len(forest_data_storage) <= outcome_idx:
        return pd.DataFrame()

    # Load forest data for the outcome
    forest_json = forest_data_storage[outcome_idx]
    if not forest_json:
        return pd.DataFrame()

    forest_df = pd.read_json(StringIO(forest_json), orient="split")

    # Load netsplit data if available
    if net_split_data_storage and len(net_split_data_storage) > outcome_idx:
        netsplit_json = net_split_data_storage[outcome_idx]
        if netsplit_json:
            netsplit_df = pd.read_json(StringIO(netsplit_json), orient="split")

            # Parse comparison column to get Treatment and Reference
            if "comparison" in netsplit_df.columns:
                netsplit_df[["Treatment", "Reference"]] = netsplit_df[
                    "comparison"
                ].str.split(":", expand=True)

            # Helper function to parse CI strings like "0.6 (0.51, 0.71)"
            def parse_ci_string(s):
                if pd.isna(s) or s == "" or not isinstance(s, str):
                    return np.nan, np.nan, np.nan
                try:
                    s = s.strip()
                    if "(" not in s:
                        return float(s), np.nan, np.nan
                    parts = s.split("(")
                    point = float(parts[0].strip())
                    ci_part = parts[1].replace(")", "").strip()
                    ci_vals = ci_part.split(",")
                    low = float(ci_vals[0].strip())
                    high = float(ci_vals[1].strip())
                    return point, low, high
                except:
                    return np.nan, np.nan, np.nan

            # Parse direct/indirect columns if they are formatted strings like "0.6 (0.51, 0.71)"
            if "direct" in netsplit_df.columns:
                # Check if direct is a formatted string
                sample_val = (
                    netsplit_df["direct"].iloc[0] if len(netsplit_df) > 0 else None
                )
                if sample_val and isinstance(sample_val, str) and "(" in sample_val:
                    direct_parsed = netsplit_df["direct"].apply(parse_ci_string)
                    netsplit_df["direct_val"] = direct_parsed.apply(lambda x: x[0])
                    netsplit_df["direct_low"] = direct_parsed.apply(lambda x: x[1])
                    netsplit_df["direct_up"] = direct_parsed.apply(lambda x: x[2])
                    netsplit_df["direct"] = netsplit_df["direct_val"]

            if "indirect" in netsplit_df.columns:
                sample_val = (
                    netsplit_df["indirect"].iloc[0] if len(netsplit_df) > 0 else None
                )
                if sample_val and isinstance(sample_val, str) and "(" in sample_val:
                    indirect_parsed = netsplit_df["indirect"].apply(parse_ci_string)
                    netsplit_df["indirect_val"] = indirect_parsed.apply(lambda x: x[0])
                    netsplit_df["indirect_low"] = indirect_parsed.apply(lambda x: x[1])
                    netsplit_df["indirect_up"] = indirect_parsed.apply(lambda x: x[2])
                    netsplit_df["indirect"] = netsplit_df["indirect_val"]

            # Merge with forest data
            merge_cols = (
                ["Treatment", "Reference"] if "Treatment" in netsplit_df.columns else []
            )

            # Determine which columns to merge
            netsplit_cols_to_merge = merge_cols.copy()
            for col in [
                "direct",
                "direct_low",
                "direct_up",
                "indirect",
                "indirect_low",
                "indirect_up",
            ]:
                if col in netsplit_df.columns:
                    netsplit_cols_to_merge.append(col)

            if merge_cols and len(netsplit_cols_to_merge) > len(merge_cols):
                forest_df = pd.merge(
                    forest_df,
                    netsplit_df[netsplit_cols_to_merge],
                    on=merge_cols,
                    how="left",
                )

    return forest_df


def get_skt_pairwise_data(forest_data_prws_storage, outcome_idx=0):
    """
    Get pairwise forest plot data from STORAGE.

    Args:
        forest_data_prws_storage: List of JSON strings for pairwise data
        outcome_idx: Which outcome to use

    Returns:
        DataFrame with pairwise comparison data
    """
    if not forest_data_prws_storage or len(forest_data_prws_storage) <= outcome_idx:
        return pd.DataFrame()

    prws_json = forest_data_prws_storage[outcome_idx]
    if not prws_json:
        return pd.DataFrame()

    return pd.read_json(StringIO(prws_json), orient="split")


def get_skt_ranking_data(ranking_data_storage, outcome_idx=0):
    """
    Get ranking (P-score) data from STORAGE.

    Args:
        ranking_data_storage: List of JSON strings with ranking data
        outcome_idx: Which outcome to use

    Returns:
        DataFrame with columns: treatment, pscore
    """
    if not ranking_data_storage or len(ranking_data_storage) <= outcome_idx:
        return pd.DataFrame()

    ranking_json = ranking_data_storage[outcome_idx]
    if not ranking_json:
        return pd.DataFrame()

    return pd.read_json(StringIO(ranking_json), orient="split")


def get_skt_cinema_data(cinema_net_data_storage, outcome_idx=0):
    """
    Get CINeMA confidence data from STORAGE.

    Args:
        cinema_net_data_storage: List of JSON strings with CINeMA data
        outcome_idx: Which outcome to use

    Returns:
        DataFrame with columns: Comparison, Confidence rating, Within-study bias, etc.
    """
    if not cinema_net_data_storage or len(cinema_net_data_storage) <= outcome_idx:
        return pd.DataFrame()

    cinema_json = cinema_net_data_storage[outcome_idx]
    if not cinema_json:
        return pd.DataFrame()

    return pd.read_json(StringIO(cinema_json), orient="split")


def get_skt_network_data(net_data_storage):
    """
    Get wide-format network data from STORAGE.

    Args:
        net_data_storage: Dict with "data" key containing JSON string

    Returns:
        DataFrame with study-level data (treat1, treat2, TE1, seTE1, etc.)
    """
    if not net_data_storage:
        return pd.DataFrame()

    json_str = get_net_data_json(net_data_storage)
    if not json_str:
        return pd.DataFrame()

    return pd.read_json(StringIO(json_str), orient="split")


def get_skt_league_table(league_table_data_storage, outcome_idx=0):
    """
    Get league table data from STORAGE.

    Args:
        league_table_data_storage: Dict or list with league table data
            New format: {"data": [...], "primary_outcomes": {...}}
            Legacy format: [json_str1, json_str2, ...]
        outcome_idx: Which outcome to use

    Returns:
        DataFrame with league table format (Treatment as rows, treatments as columns)
    """
    # Handle new dict format and legacy list format
    league_data_list = get_league_table_data_list(league_table_data_storage)

    if not league_data_list or len(league_data_list) <= outcome_idx:
        return pd.DataFrame()

    league_json = league_data_list[outcome_idx]
    if not league_json:
        return pd.DataFrame()

    return pd.read_json(StringIO(league_json), orient="split")


def get_skt_two_outcome_data(
    forest_data_storage, cinema_net_data_storage, outcome_names=None
):
    """
    Derive skt_df_two.csv equivalent - combined data for two outcomes.

    This is the main table data for the Standard KT view showing
    treatment comparisons with RR and certainty for both outcomes.

    Args:
        forest_data_storage: List of JSON strings for forest data
        cinema_net_data_storage: List of JSON strings for CINeMA data
        outcome_names: List of outcome names (e.g., ["PASI90", "SAE"])

    Returns:
        DataFrame with columns: Treatment, Reference, RR, CI_lower, CI_upper,
                               RR_out2, CI_lower_out2, CI_upper_out2,
                               Certainty_out1, Certainty_out2, etc.
    """
    if not forest_data_storage or len(forest_data_storage) < 1:
        return pd.DataFrame()

    # Load first outcome forest data
    forest1_json = forest_data_storage[0]
    if not forest1_json:
        return pd.DataFrame()

    df1 = pd.read_json(StringIO(forest1_json), orient="split")

    # Ensure required columns exist
    required_cols = ["Treatment", "Reference", "RR", "CI_lower", "CI_upper"]
    if not all(col in df1.columns for col in required_cols):
        # Try alternative column names
        if "treat1" in df1.columns:
            df1 = df1.rename(columns={"treat1": "Treatment", "treat2": "Reference"})

    result_df = df1[["Treatment", "Reference", "RR", "CI_lower", "CI_upper"]].copy()

    # Add second outcome if available
    if len(forest_data_storage) >= 2 and forest_data_storage[1]:
        df2 = pd.read_json(StringIO(forest_data_storage[1]), orient="split")
        if "treat1" in df2.columns:
            df2 = df2.rename(columns={"treat1": "Treatment", "treat2": "Reference"})

        # Merge second outcome
        df2_subset = df2[
            ["Treatment", "Reference", "RR", "CI_lower", "CI_upper"]
        ].copy()
        df2_subset = df2_subset.rename(
            columns={
                "RR": "RR_out2",
                "CI_lower": "CI_lower_out2",
                "CI_upper": "CI_upper_out2",
            }
        )

        result_df = pd.merge(
            result_df, df2_subset, on=["Treatment", "Reference"], how="outer"
        )

    # Add CINeMA certainty ratings
    if cinema_net_data_storage:
        for i, cinema_json in enumerate(cinema_net_data_storage[:2]):
            if cinema_json:
                cinema_df = pd.read_json(StringIO(cinema_json), orient="split")
                suffix = "" if i == 0 else "_out2"
                col_name = f"Certainty_out{i + 1}"

                if (
                    "Comparison" in cinema_df.columns
                    and "Confidence rating" in cinema_df.columns
                ):
                    # Parse comparison to match with Treatment/Reference
                    certainty_map = dict(
                        zip(cinema_df["Comparison"], cinema_df["Confidence rating"])
                    )

                    result_df[col_name] = result_df.apply(
                        lambda row: certainty_map.get(
                            f"{row['Treatment']}:{row['Reference']}",
                            certainty_map.get(
                                f"{row['Reference']}:{row['Treatment']}", None
                            ),
                        ),
                        axis=1,
                    )

    return result_df


def get_skt_network_elements(net_data_storage, outcome_idx=0):
    """
    Generate cytoscape network elements from STORAGE data.

    Args:
        net_data_storage: Dict with network data
        outcome_idx: Which outcome to use

    Returns:
        List of cytoscape elements (nodes and edges)
    """
    df = get_skt_network_data(net_data_storage)
    if df.empty:
        return []

    # Get unique treatments
    if "treat1" not in df.columns or "treat2" not in df.columns:
        return []

    te_col = f"TE{outcome_idx + 1}"
    se_col = f"seTE{outcome_idx + 1}"

    # Filter out rows without effect estimates
    if te_col in df.columns and se_col in df.columns:
        df = df.dropna(subset=[te_col, se_col])

    # Get unique treatments
    treatments = pd.concat([df["treat1"], df["treat2"]]).unique()

    # Create nodes
    nodes = [{"data": {"id": treat, "label": treat}} for treat in treatments]

    # Create edges - aggregate by treatment pair
    edge_data = df.groupby(["treat1", "treat2"]).size().reset_index(name="n_studies")

    edges = [
        {
            "data": {
                "source": row["treat1"],
                "target": row["treat2"],
                "weight": row["n_studies"],
                "label": str(row["n_studies"]),
            }
        }
        for _, row in edge_data.iterrows()
    ]

    return nodes + edges


def get_treatment_fullnames(net_data_storage, treatment_fullnames_skt=None):
    """
    Get mapping of treatment abbreviations to full names.

    If treatment_fullnames_skt is provided, use that.
    Otherwise, return abbreviations as-is.

    Args:
        net_data_storage: Dict with network data
        treatment_fullnames_skt: Optional dict with abbreviation -> full name mapping

    Returns:
        Dict mapping abbreviation -> full name
    """
    if treatment_fullnames_skt:
        return treatment_fullnames_skt

    # If no fullnames provided, use abbreviations as fullnames
    df = get_skt_network_data(net_data_storage)
    if df.empty:
        return {}

    treatments = pd.concat([df["treat1"], df["treat2"]]).unique()
    return {treat: treat for treat in treatments}


def get_risk_ranges_from_wide(net_data_storage, outcome_idx=0):
    """
    Calculate risk ranges per treatment from wide-format network data.

    This derives the same data that was previously read from psoriasis_long_complete.csv.
    It calculates min/max observed event rates for each treatment across studies.

    Args:
        net_data_storage: Dict with network data (wide format)
        outcome_idx: Which outcome to use (0-indexed)

    Returns:
        DataFrame with columns: treat, min_value, max_value
        Values are event rates per 1000
    """
    df = get_skt_network_data(net_data_storage)
    if df.empty:
        return pd.DataFrame()

    # Wide format has: event11, n11, event21, n21 for outcome 1
    # and event12, n12, event22, n22 for outcome 2
    suffix = str(outcome_idx + 1)
    event1_col = f"event1{suffix}"  # events for treat1
    n1_col = f"n1{suffix}"  # sample size for treat1
    event2_col = f"event2{suffix}"  # events for treat2
    n2_col = f"n2{suffix}"  # sample size for treat2

    # Check if columns exist
    required_cols = [event1_col, n1_col, event2_col, n2_col]
    if not all(col in df.columns for col in required_cols):
        # Try alternative naming: r11, n11, r21, n21
        event1_col = f"r1{suffix}"
        event2_col = f"r2{suffix}"
        if not all(
            col in df.columns for col in [event1_col, n1_col, event2_col, n2_col]
        ):
            return pd.DataFrame()

    # Create long-format data from wide format
    # For treat1 arms
    df1 = df[["treat1", event1_col, n1_col]].copy()
    df1.columns = ["treat", "events", "n"]

    # For treat2 arms
    df2 = df[["treat2", event2_col, n2_col]].copy()
    df2.columns = ["treat", "events", "n"]

    # Combine
    long_df = pd.concat([df1, df2], ignore_index=True)
    long_df = long_df.dropna(subset=["events", "n"])

    # Filter out zero sample sizes
    long_df = long_df[long_df["n"] > 0]

    if long_df.empty:
        return pd.DataFrame()

    # Calculate event rate per 1000 for each arm
    long_df["rate"] = (long_df["events"] / long_df["n"]) * 1000

    # Group by treatment and get min/max rates
    range_ref_ab = (
        long_df.groupby("treat")
        .agg(min_value=("rate", "min"), max_value=("rate", "max"))
        .reset_index()
    )

    return range_ref_ab


def get_effect_modifier_data(net_data_storage, effect_modifiers_storage):
    """
    Get effect modifier data for transitivity plots.

    Args:
        net_data_storage: Dict with network data
        effect_modifiers_storage: List of effect modifier column names

    Returns:
        DataFrame with treat1, treat2, and effect modifier columns
    """
    df = get_skt_network_data(net_data_storage)
    if df.empty or not effect_modifiers_storage:
        return pd.DataFrame()

    # Get available effect modifiers that exist in the data
    available_modifiers = [col for col in effect_modifiers_storage if col in df.columns]

    if not available_modifiers:
        return pd.DataFrame()

    return df[["treat1", "treat2"] + available_modifiers].copy()


def build_skt_advanced_row_data(
    forest_data_storage,
    net_split_data_storage,
    ranking_data_storage,
    cinema_net_data_storage,
    net_data_storage,
    outcome_idx=0,
):
    """
    Build the row data for the SKT Advanced grid from STORAGE.

    This replicates the data processing done at import time in skt_layout.py,
    but dynamically from STORAGE data.

    Args:
        forest_data_storage: List of JSON strings for forest data
        net_split_data_storage: List of JSON strings for netsplit data
        ranking_data_storage: List of JSON strings for ranking data
        cinema_net_data_storage: List of JSON strings for CINeMA data
        net_data_storage: Dict with network data
        outcome_idx: Which outcome to use

    Returns:
        tuple: (row_data, row_data_default) as list of dicts for AG Grid
    """
    # Get the main forest data with direct/indirect
    df = get_skt_final_data(forest_data_storage, net_split_data_storage, outcome_idx)
    if df.empty:
        return [], []

    # Get CINeMA data
    cinema_df = get_skt_cinema_data(cinema_net_data_storage, outcome_idx)

    # Get ranking data
    p_score = get_skt_ranking_data(ranking_data_storage, outcome_idx)

    # Get risk ranges
    range_ref_ab = get_risk_ranges_from_wide(net_data_storage, outcome_idx)

    # Add CINeMA certainty columns
    df["Certainty"] = ""
    df["within_study"] = ""
    df["reporting"] = ""
    df["indirectness"] = ""
    df["imprecision"] = ""
    df["heterogeneity"] = ""
    df["incoherence"] = ""

    if not cinema_df.empty and "Comparison" in cinema_df.columns:
        for i in range(df.shape[0]):
            if "Reference" not in df.columns or "Treatment" not in df.columns:
                continue
            src = df["Reference"].iloc[i]
            trgt = df["Treatment"].iloc[i]
            slctd_comps = [f"{src}:{trgt}", f"{trgt}:{src}"]

            matching = cinema_df[cinema_df["Comparison"].isin(slctd_comps)]
            if not matching.empty:
                df.loc[df.index[i], "Certainty"] = (
                    matching["Confidence rating"].iloc[0]
                    if "Confidence rating" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "within_study"] = (
                    matching["Within-study bias"].iloc[0]
                    if "Within-study bias" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "reporting"] = (
                    matching["Reporting bias"].iloc[0]
                    if "Reporting bias" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "indirectness"] = (
                    matching["Indirectness"].iloc[0]
                    if "Indirectness" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "imprecision"] = (
                    matching["Imprecision"].iloc[0]
                    if "Imprecision" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "heterogeneity"] = (
                    matching["Heterogeneity"].iloc[0]
                    if "Heterogeneity" in matching.columns
                    else ""
                )
                df.loc[df.index[i], "incoherence"] = (
                    matching["Incoherence"].iloc[0]
                    if "Incoherence" in matching.columns
                    else ""
                )

    # Add calculated columns
    df["Comments"] = ""
    df["CI_width_hf"] = (
        df["CI_upper"] - df["RR"]
        if "CI_upper" in df.columns and "RR" in df.columns
        else 0
    )
    df["lower_error"] = (
        df["RR"] - df["CI_lower"]
        if "RR" in df.columns and "CI_lower" in df.columns
        else 0
    )
    df["weight"] = 1 / df["CI_width_hf"].replace(0, np.nan)
    df["Graph"] = ""
    df["risk"] = "Enter a number"
    df["Scale_lower"] = "Enter a value for lower"
    df["Scale_upper"] = "Enter a value for upper"
    df["ab_difference"] = ""
    df["rationality"] = "Enter a reason"

    df = df.round(2)

    # Group by Reference to create nested structure
    if "Reference" not in df.columns:
        return [], []

    grouped = df.groupby(["Reference", "risk", "Scale_lower", "Scale_upper"])
    row_data_list = []

    for (ref, risk, scale_lower, scale_upper), group in grouped:
        treatments = []
        for _, row in group.iterrows():
            treatment_data = {
                "Treatment": row.get("Treatment", ""),
                "RR": row.get("RR", ""),
                "direct": row.get("direct", ""),
                "Graph": row.get("Graph", ""),
                "indirect": row.get("indirect", ""),
                "p-value": row.get("p-value", ""),
                "Certainty": row.get("Certainty", ""),
                "direct_low": row.get("direct_low", ""),
                "direct_up": row.get("direct_up", ""),
                "indirect_low": row.get("indirect_low", ""),
                "indirect_up": row.get("indirect_up", ""),
                "CI_lower": row.get("CI_lower", ""),
                "CI_upper": row.get("CI_upper", ""),
                "Comments": row.get("Comments", ""),
                "ab_difference": row.get("ab_difference", ""),
                "within_study": row.get("within_study", ""),
                "reporting": row.get("reporting", ""),
                "indirectness": row.get("indirectness", ""),
                "imprecision": row.get("imprecision", ""),
                "heterogeneity": row.get("heterogeneity", ""),
                "incoherence": row.get("incoherence", ""),
            }
            treatments.append(treatment_data)

        row_data_list.append(
            {
                "Reference": ref,
                "risk": risk,
                "Scale_lower": scale_lower,
                "Scale_upper": scale_upper,
                "Treatments": treatments,
            }
        )

    # Create DataFrame and merge with ranking and risk range
    row_data = pd.DataFrame(row_data_list)

    if not p_score.empty and "treatment" in p_score.columns:
        row_data = row_data.merge(
            p_score, left_on="Reference", right_on="treatment", how="left"
        )

    if not range_ref_ab.empty and "treat" in range_ref_ab.columns:
        row_data = row_data.merge(
            range_ref_ab, left_on="Reference", right_on="treat", how="left"
        )
        row_data["risk_range"] = row_data.apply(
            lambda r: f"from {int(r['min_value'])} to {int(r['max_value'])}"
            if pd.notna(r.get("min_value")) and pd.notna(r.get("max_value"))
            else "",
            axis=1,
        )

    return row_data.to_dict("records"), row_data.to_dict("records")
