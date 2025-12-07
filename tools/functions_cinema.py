"""
CINeMA (Confidence in Network Meta-Analysis) related functions.

This module handles:
- Parsing CINeMA CSV uploads
- Processing CINeMA confidence ratings
- Building CINeMA-colored league tables
"""

import pandas as pd
import numpy as np
from tools.utils import parse_contents


# Required columns for CINeMA CSV files
CINEMA_REQUIRED_COLUMNS = ["Comparison", "Confidence rating"]
CINEMA_OPTIONAL_COLUMNS = ["Reason(s) for downgrading"]
CINEMA_VALID_RATINGS = ["very low", "low", "moderate", "high"]


def validate_cinema_csv(cinema_df, treatments=None):
    """
    Validate that a CINeMA CSV file has the required format.

    Required columns:
    - "Comparison": Format should be "TREAT1:TREAT2"
    - "Confidence rating": Should be one of "Very Low", "Low", "Moderate", "High"

    Optional columns:
    - "Reason(s) for downgrading": Reasons for downgrading the confidence

    Args:
        cinema_df: DataFrame of CINeMA data
        treatments: Optional list of treatments to check comparisons against

    Returns:
        tuple: (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Empty string if valid, error description otherwise
    """
    errors = []

    # Check required columns exist
    for col in CINEMA_REQUIRED_COLUMNS:
        if col not in cinema_df.columns:
            errors.append(f"Missing required column: '{col}'")

    if errors:
        return False, "; ".join(errors)

    # Check Comparison column format (should contain ":")
    comparisons = cinema_df["Comparison"]
    invalid_format = ~comparisons.str.contains(":", na=False)
    if invalid_format.any():
        bad_rows = comparisons[invalid_format].head(3).tolist()
        errors.append(
            f"Invalid Comparison format (expected 'TREAT1:TREAT2'): {bad_rows}"
        )

    # Check Confidence rating values
    valid_ratings_lower = [r.lower() for r in CINEMA_VALID_RATINGS]
    ratings = cinema_df["Confidence rating"].str.lower()
    invalid_ratings = ~ratings.isin(valid_ratings_lower)
    if invalid_ratings.any():
        bad_ratings = cinema_df["Confidence rating"][invalid_ratings].unique().tolist()
        errors.append(
            f"Invalid Confidence rating values (expected {CINEMA_VALID_RATINGS}): {bad_ratings}"
        )

    # If treatments provided, check that comparisons use valid treatments
    if treatments is not None and len(treatments) > 0:
        # Split comparisons and extract all treatments
        all_cinema_treatments = set()
        for comp in comparisons:
            if ":" in str(comp):
                parts = str(comp).split(":")
                all_cinema_treatments.update(parts)

        # Check if CINeMA treatments match league table treatments
        treatments_set = set(treatments)
        unknown_treatments = all_cinema_treatments - treatments_set
        if unknown_treatments:
            # This is a warning, not an error - treatments might use different names
            pass  # We'll handle mismatches gracefully in the league table display

    if errors:
        return False, "; ".join(errors)

    return True, ""


def process_cinema_upload(
    contents, filename, cinema_net_data, outcome_idx=0, treatments=None
):
    """
    Process a CINeMA file upload and store it at the correct outcome index.

    Args:
        contents: Upload contents from dcc.Upload
        filename: Filename of the uploaded file
        cinema_net_data: Existing cinema_net_data_STORAGE data (list)
        outcome_idx: Index of the outcome (0-based)
        treatments: Optional list of treatments for validation

    Returns:
        tuple: (updated_cinema_net_data, message_string)
    """
    if contents is None:
        return cinema_net_data if cinema_net_data else [], ""

    try:
        # Parse uploaded file
        cinema_df = parse_contents(contents, filename)

        # Validate the CINeMA CSV format
        is_valid, error_msg = validate_cinema_csv(cinema_df, treatments)
        if not is_valid:
            print(f"CINeMA validation failed: {error_msg}")
            return (
                cinema_net_data if cinema_net_data else [],
                f"Invalid CINeMA file: {error_msg}",
            )

        # Initialize storage list if empty
        if cinema_net_data is None or not isinstance(cinema_net_data, list):
            cinema_net_data = []
        else:
            # Make a copy to avoid mutating the original
            cinema_net_data = list(cinema_net_data)

        # Ensure list is long enough for outcome_idx
        while len(cinema_net_data) <= outcome_idx:
            cinema_net_data.append(None)

        # Store at the correct outcome index
        cinema_net_data[outcome_idx] = cinema_df.to_json(orient="split")

        return cinema_net_data, f"Loaded: {filename}"

    except Exception as e:
        print(f"Error uploading CINeMA file: {e}")
        return cinema_net_data if cinema_net_data else [], f"Error: {str(e)}"


def process_cinema_upload_both(
    contents1,
    contents2,
    filename1,
    filename2,
    cinema_net_data,
    triggered_prop_ids,
):
    """
    Process CINeMA file uploads for both outcomes (both outcomes league table).

    Args:
        contents1: Upload contents for outcome 1
        contents2: Upload contents for outcome 2
        filename1: Filename for outcome 1
        filename2: Filename for outcome 2
        cinema_net_data: Existing cinema_net_data_STORAGE2 data (list [outcome1, outcome2])
        triggered_prop_ids: List of triggered property IDs from callback context

    Returns:
        tuple: (updated_cinema_net_data, msg1, msg2)
    """
    # Initialize storage list if empty [outcome1, outcome2]
    if cinema_net_data is None or not isinstance(cinema_net_data, list):
        cinema_net_data = [None, None]
    else:
        # Make a copy to avoid mutating the original
        cinema_net_data = list(cinema_net_data)

    # Ensure list has at least 2 elements
    while len(cinema_net_data) < 2:
        cinema_net_data.append(None)

    file1_msg = ""
    file2_msg = ""

    try:
        # Process file 1 if uploaded (for outcome 1)
        if (
            "datatable-secondfile-upload-1.contents" in triggered_prop_ids
            and contents1 is not None
        ):
            cinema_df1 = parse_contents(contents1, filename1)
            # Validate CINeMA CSV format
            is_valid, error_msg = validate_cinema_csv(cinema_df1)
            if is_valid:
                cinema_net_data[0] = cinema_df1.to_json(orient="split")
                file1_msg = f"Loaded: {filename1}"
            else:
                file1_msg = f"Invalid: {error_msg}"

        # Process file 2 if uploaded (for outcome 2)
        if (
            "datatable-secondfile-upload-2.contents" in triggered_prop_ids
            and contents2 is not None
        ):
            cinema_df2 = parse_contents(contents2, filename2)
            # Validate CINeMA CSV format
            is_valid, error_msg = validate_cinema_csv(cinema_df2)
            if is_valid:
                cinema_net_data[1] = cinema_df2.to_json(orient="split")
                file2_msg = f"Loaded: {filename2}"
            else:
                file2_msg = f"Invalid: {error_msg}"

        return cinema_net_data, file1_msg, file2_msg

    except Exception as e:
        print(f"Error uploading CINeMA files: {e}")
        return cinema_net_data, f"Error: {str(e)}", f"Error: {str(e)}"


def check_cinema_data_available(cinema_net_data, outcome_idx=0):
    """
    Check if CINeMA data is available for a specific outcome.

    Args:
        cinema_net_data: The cinema_net_data_STORAGE data (list)
        outcome_idx: Index of the outcome to check

    Returns:
        bool: True if CINeMA data is available, False otherwise
    """
    if cinema_net_data is None or not isinstance(cinema_net_data, list):
        return False

    if len(cinema_net_data) <= outcome_idx:
        return False

    if cinema_net_data[outcome_idx] is None:
        return False

    return True


def check_cinema_data_available_both(cinema_net_data):
    """
    Check if CINeMA data is available for both outcomes.

    Args:
        cinema_net_data: The cinema_net_data_STORAGE2 data (list [outcome1, outcome2])

    Returns:
        bool: True if CINeMA data is available for both outcomes
    """
    if cinema_net_data is None or not isinstance(cinema_net_data, list):
        return False

    if len(cinema_net_data) < 2:
        return False

    if cinema_net_data[0] is None or cinema_net_data[1] is None:
        return False

    return True


def parse_cinema_data(cinema_json, treatments=None):
    """
    Parse CINeMA data from JSON and build confidence matrices.

    Args:
        cinema_json: JSON string of CINeMA data
        treatments: Optional list of treatments to filter to

    Returns:
        dict: {
            'confidence': DataFrame of confidence ratings,
            'downgrading': DataFrame of downgrading reasons (or empty),
            'comprs_conf_lt': Lower triangle comparisons with confidence,
            'comprs_conf_ut': Upper triangle comparisons with confidence,
        }
    """
    cinema_df = pd.read_json(cinema_json, orient="split")
    confidence_map = {
        k: n for n, k in enumerate(["very low", "low", "moderate", "high"])
    }

    # Parse comparisons from CINeMA data
    comparisons1 = cinema_df.Comparison.str.split(":", expand=True)
    confidence1 = cinema_df["Confidence rating"].str.lower().map(confidence_map)

    # Set up comparison matrices
    comparisons2 = comparisons1.copy()
    comprs_conf_ut = comparisons2.copy()  # Upper triangle
    comparisons1.columns = [1, 0]  # To get lower triangle
    comprs_conf_lt = comparisons1.copy()  # Lower triangle

    # Process downgrading reasons if available
    comprs_downgrade = pd.DataFrame()
    if "Reason(s) for downgrading" in cinema_df.columns:
        downgrading1 = cinema_df["Reason(s) for downgrading"]
        comprs_downgrade_lt = comprs_conf_lt.copy()
        comprs_downgrade_ut = comprs_conf_ut.copy()
        comprs_downgrade_lt["Downgrading"] = downgrading1
        comprs_downgrade_ut["Downgrading"] = pd.Series(
            np.array([np.nan] * len(downgrading1)), copy=False
        )
        comprs_downgrade = pd.concat([comprs_downgrade_ut, comprs_downgrade_lt])
        comprs_downgrade = comprs_downgrade.pivot(
            index=0, columns=1, values="Downgrading"
        )

    # Build confidence pivot table
    comprs_conf_lt["Confidence"] = confidence1
    comprs_conf_ut["Confidence"] = pd.Series(
        np.array([np.nan] * len(confidence1)), copy=False
    )
    comprs_conf = pd.concat([comprs_conf_ut, comprs_conf_lt])
    comprs_conf = comprs_conf.pivot(index=0, columns=1, values="Confidence")

    # Mask upper triangle
    ut = np.triu(np.ones(comprs_conf.shape), 1).astype(bool)
    comprs_conf = comprs_conf.where(ut == False, np.nan)

    return {
        "confidence": comprs_conf,
        "downgrading": comprs_downgrade,
        "comprs_conf_lt": comprs_conf_lt,
        "comprs_conf_ut": comprs_conf_ut,
    }


def get_cinema_color_styles(
    robs, treatments, toggle_cinema, cmap, ranges, CLR_BCKGRND2
):
    """
    Generate conditional styles for league table based on ROB or CINeMA ratings.

    Args:
        robs: DataFrame of ROB or CINeMA confidence values
        treatments: List of treatment names
        toggle_cinema: Boolean indicating if CINeMA mode is active
        cmap: List of colors for bins
        ranges: Array of bin boundaries
        CLR_BCKGRND2: Background color for empty cells

    Returns:
        list: List of conditional style dictionaries
    """
    league_table_styles = []

    for treat_r in treatments:
        for treat_c in treatments:
            if treat_r != treat_c:
                try:
                    rob_val = (
                        robs.loc[treat_r, treat_c]
                        if treat_r in robs.index and treat_c in robs.columns
                        else np.nan
                    )
                    empty = rob_val != rob_val  # Check for NaN

                    if not empty:
                        # Map value to color bin
                        indxs = np.where(rob_val < ranges)[0] if not empty else [0]
                        clr_indx = (
                            indxs[0] - 1 if len(indxs) > 0 and indxs[0] > 0 else 0
                        )
                        league_table_styles.append(
                            {
                                "if": {
                                    "filter_query": f'{{Treatment}} = "{treat_r}"',
                                    "column_id": treat_c,
                                },
                                "backgroundColor": cmap[clr_indx],
                                "color": "white",
                            }
                        )
                    else:
                        league_table_styles.append(
                            {
                                "if": {
                                    "filter_query": f'{{Treatment}} = "{treat_r}"',
                                    "column_id": treat_c,
                                },
                                "backgroundColor": CLR_BCKGRND2,
                                "color": "black",
                            }
                        )
                except (KeyError, IndexError):
                    pass

    return league_table_styles


def build_cinema_legend(toggle_cinema, cmap, N_BINS):
    """
    Build the legend HTML for ROB or CINeMA rating display.

    Args:
        toggle_cinema: Boolean indicating if CINeMA mode is active
        cmap: List of colors for bins
        N_BINS: Number of bins

    Returns:
        list: List of html.Div elements for legend
    """
    from dash import html

    legend_height = "4px"
    legend = [
        html.Div(
            style={"display": "inline-block", "width": "100px"},
            children=[
                html.Div(),
                html.Small(
                    "Risk of bias: " if not toggle_cinema else "CINeMA rating: ",
                    style={"color": "black"},
                ),
            ],
        )
    ]
    legend += [
        html.Div(
            style={"display": "inline-block", "width": "60px"},
            children=[
                html.Div(style={"backgroundColor": cmap[n], "height": legend_height}),
                html.Small(
                    ("Very Low" if toggle_cinema else "Low")
                    if n == 0
                    else "High"
                    if n == N_BINS - 1
                    else None,
                    style={"paddingLeft": "2px", "color": "black"},
                ),
            ],
        )
        for n in range(N_BINS)
    ]

    return legend
