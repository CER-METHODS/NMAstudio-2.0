# Demo data for 3-outcome project (PASI90, SAE, AE)
# Based on test_create_3outcomes_project.py configuration
import pandas as pd
from pandas import DataFrame
from tools.utils import get_network, get_network_new
from collections import OrderedDict
import json

# Load raw data - same as 2-outcome version
RAW_DATA = pd.read_csv("db/psoriasis_long_complete.csv", encoding="iso-8859-1")
NET_DATA = pd.read_csv("db/psoriasis_wide_complete.csv", encoding="iso-8859-1")

# For 3 outcomes, we prepare network datasets
# Note: The wide CSV only has 2 outcomes (TE1, TE2), so we reuse outcome 2 for outcome 3
# In a real 3-outcome scenario, the wide CSV would have TE1, TE2, TE3

# Outcome 1: PASI90 (uses TE1, seTE1)
NET_DATA1 = NET_DATA.copy()
DEFAULT_ELEMENTS1 = USER_ELEMENTS1 = get_network_new(df=NET_DATA, i=0)

# Outcome 2: SAE (uses TE2, seTE2)
NET_DATA2 = NET_DATA.drop(["TE1", "seTE1", "n11", "n21"], axis=1)
DEFAULT_ELEMENTS2 = USER_ELEMENTS2 = get_network_new(df=NET_DATA2, i=1)

# Outcome 3: AE (Adverse Events)
# Since the wide CSV only has 2 outcomes, we reuse outcome 2's network elements for outcome 3
# This is just for demo purposes - in production, this would be computed from actual AE data
DEFAULT_ELEMENTS3 = USER_ELEMENTS3 = DEFAULT_ELEMENTS2

# Load forest plot data
FOREST_DATA_OUT1 = pd.read_csv("db/forest_data/forest_data_out1.csv")
FOREST_DATA_OUT2 = pd.read_csv("db/forest_data/forest_data_out2.csv")
# For outcome 3, use outcome 2 data as placeholder (in real scenario would be computed)
FOREST_DATA_OUT3 = FOREST_DATA_OUT2.copy()

FOREST_DATA_PRWS_OUT1 = pd.read_csv("db/forest_data/forest_data_pairwise.csv")
FOREST_DATA_PRWS_OUT2 = pd.read_csv("db/forest_data/forest_data_pairwise_out2.csv")
FOREST_DATA_PRWS_OUT3 = FOREST_DATA_PRWS_OUT2.copy()

# Load league table data
LEAGUE_TABLE_DATA1: DataFrame = pd.read_csv(
    "db/league_table_data/league_1.csv", index_col=0
)
LEAGUE_TABLE_DATA2: DataFrame = pd.read_csv(
    "db/league_table_data/league_2.csv", index_col=0
)
# For outcome 3, use outcome 2 as placeholder
LEAGUE_TABLE_DATA3 = LEAGUE_TABLE_DATA2.copy()

LEAGUE_TABLE_DATA_BOTH: DataFrame = pd.read_csv(
    "db/league_table_data/league_table.csv", index_col=0
)

# Format league tables
replace_and_strip = lambda x: x.replace(" (", "\n(").strip()

LEAGUE_TABLE_DATA1 = LEAGUE_TABLE_DATA1.fillna("")
LEAGUE_TABLE_DATA1 = pd.DataFrame(
    [
        [replace_and_strip(col) for col in list(row)]
        for idx, row in LEAGUE_TABLE_DATA1.iterrows()
    ],
    columns=LEAGUE_TABLE_DATA1.columns,
    index=LEAGUE_TABLE_DATA1.index,
)

LEAGUE_TABLE_DATA2 = LEAGUE_TABLE_DATA2.fillna("")
LEAGUE_TABLE_DATA2 = pd.DataFrame(
    [
        [replace_and_strip(col) for col in list(row)]
        for idx, row in LEAGUE_TABLE_DATA2.iterrows()
    ],
    columns=LEAGUE_TABLE_DATA2.columns,
    index=LEAGUE_TABLE_DATA2.index,
)

LEAGUE_TABLE_DATA3 = LEAGUE_TABLE_DATA3.fillna("")
LEAGUE_TABLE_DATA3 = pd.DataFrame(
    [
        [replace_and_strip(col) for col in list(row)]
        for idx, row in LEAGUE_TABLE_DATA3.iterrows()
    ],
    columns=LEAGUE_TABLE_DATA3.columns,
    index=LEAGUE_TABLE_DATA3.index,
)

LEAGUE_TABLE_DATA_BOTH = LEAGUE_TABLE_DATA_BOTH.fillna("")
LEAGUE_TABLE_DATA_BOTH = pd.DataFrame(
    [
        [replace_and_strip(col) for col in list(row)]
        for idx, row in LEAGUE_TABLE_DATA_BOTH.iterrows()
    ],
    columns=LEAGUE_TABLE_DATA_BOTH.columns,
    index=LEAGUE_TABLE_DATA_BOTH.index,
)

# Load consistency data
CONSISTENCY_DATA = pd.read_csv("db/consistency/consistency.csv")
NETSPLIT_DATA_OUT1 = pd.read_csv("db/consistency/node_split_out1.csv")
NETSPLIT_DATA_OUT2 = pd.read_csv("db/consistency/node_split_out2.csv")
NETSPLIT_DATA_OUT3 = NETSPLIT_DATA_OUT2.copy()

NETSPLIT_DATA_ALL_OUT1 = pd.read_csv("db/consistency/netsplit_all.csv")
NETSPLIT_DATA_ALL_OUT2 = pd.read_csv("db/consistency/netsplit_all_out2.csv")
NETSPLIT_DATA_ALL_OUT3 = NETSPLIT_DATA_ALL_OUT2.copy()

# Load ranking data
RANKING_DATA1 = pd.read_csv("db/ranking/rank.csv")
RANKING_DATA2 = pd.read_csv("db/ranking/rank2.csv")
RANKING_DATA3 = RANKING_DATA2.copy()

# Load funnel data
FUNNEL_DATA_OUT1 = pd.read_csv("db/funnel/funnel_data.csv")
FUNNEL_DATA_OUT2 = pd.read_csv("db/funnel/funnel_data_out2.csv")
FUNNEL_DATA_OUT3 = FUNNEL_DATA_OUT2.copy()

# Get number of RoB classes
N_CLASSES = (
    USER_ELEMENTS1[-1]["data"]["n_class"]
    if "n_class" in USER_ELEMENTS1[-1]["data"]
    else 1
)

# Create 3-outcome project data structure
# This matches the test configuration:
# - Outcome 1: PASI90 (beneficial, OR)
# - Outcome 2: SAE (harmful, OR)
# - Outcome 3: AE (harmful, OR)
# - Effect modifiers: age, weight
PSORIASIS_3OUTCOMES_DATA = {
    "nmastudio-version": "2.0",
    "raw_data_STORAGE": {"data": RAW_DATA.to_json(orient="split")},
    "net_data_STORAGE": {
        "data": NET_DATA.to_json(orient="split"),
        "elements_out1": DEFAULT_ELEMENTS1,
        "elements_out2": DEFAULT_ELEMENTS2,
        "elements_out3": DEFAULT_ELEMENTS3,
        "n_classes": N_CLASSES,
    },
    "league_table_data_STORAGE": [
        LEAGUE_TABLE_DATA1.to_json(orient="split"),  # Outcome 1: PASI90
        LEAGUE_TABLE_DATA2.to_json(orient="split"),  # Outcome 2: SAE
        LEAGUE_TABLE_DATA3.to_json(orient="split"),  # Outcome 3: AE
        LEAGUE_TABLE_DATA_BOTH.to_json(orient="split"),  # Combined (outcomes 2 & 3)
    ],
    "consistency_data_STORAGE": [
        CONSISTENCY_DATA.to_json(orient="split"),  # Outcome 1
        CONSISTENCY_DATA.to_json(orient="split"),  # Outcome 2
        CONSISTENCY_DATA.to_json(orient="split"),  # Outcome 3
    ],
    "forest_data_STORAGE": [
        FOREST_DATA_OUT1.to_json(orient="split"),  # Outcome 1: PASI90
        FOREST_DATA_OUT2.to_json(orient="split"),  # Outcome 2: SAE
        FOREST_DATA_OUT3.to_json(orient="split"),  # Outcome 3: AE
    ],
    "forest_data_prws_STORAGE": [
        FOREST_DATA_PRWS_OUT1.to_json(orient="split"),  # Outcome 1
        FOREST_DATA_PRWS_OUT2.to_json(orient="split"),  # Outcome 2
        FOREST_DATA_PRWS_OUT3.to_json(orient="split"),  # Outcome 3
    ],
    "ranking_data_STORAGE": [
        RANKING_DATA1.to_json(orient="split"),  # Outcome 1: PASI90
        RANKING_DATA2.to_json(orient="split"),  # Outcome 2: SAE
        RANKING_DATA3.to_json(orient="split"),  # Outcome 3: AE
    ],
    "funnel_data_STORAGE": [
        FUNNEL_DATA_OUT1.to_json(orient="split"),  # Outcome 1: PASI90
        FUNNEL_DATA_OUT2.to_json(orient="split"),  # Outcome 2: SAE
        FUNNEL_DATA_OUT3.to_json(orient="split"),  # Outcome 3: AE
    ],
    "net_split_data_STORAGE": [
        NETSPLIT_DATA_OUT1.to_json(orient="split"),  # Outcome 1
        NETSPLIT_DATA_OUT2.to_json(orient="split"),  # Outcome 2
        NETSPLIT_DATA_OUT3.to_json(orient="split"),  # Outcome 3
    ],
    "net_split_ALL_data_STORAGE": [
        NETSPLIT_DATA_ALL_OUT1.to_json(orient="split"),  # Outcome 1
        NETSPLIT_DATA_ALL_OUT2.to_json(orient="split"),  # Outcome 2
        NETSPLIT_DATA_ALL_OUT3.to_json(orient="split"),  # Outcome 3
    ],
    "results_ready_STORAGE": True,
    "effect_modifiers_STORAGE": ["age", "weight"],  # As per test configuration
    "outcome_names_STORAGE": ["PASI90", "SAE", "AE"],  # As per test configuration
    "number_outcomes_STORAGE": 3,  # Integer as per new schema
    "uploaded_datafile_to_disable_cinema": {"filename": "psoriasis_long_complete.csv"},
    "R_errors_STORAGE": {},
    "cinema_net_data_STORAGE": [],  # CINeMA data not loaded for 3-outcome demo
    "cinema_net_data_STORAGE2": [],  # CINeMA data not loaded for 3-outcome demo
}
