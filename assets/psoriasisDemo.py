# from assets.modal_values import *
import pandas as pd
from pandas import DataFrame
from tools.utils import get_network, get_network_new
from collections import OrderedDict
import json

RAW_DATA = pd.read_csv("db/psoriasis_long_complete.csv", encoding="iso-8859-1")
NET_DATA = pd.read_csv("db/psoriasis_wide_complete.csv", encoding="iso-8859-1")
NET_DATA2 = NET_DATA.drop(["TE1", "seTE1", "n11", "n21"], axis=1)
# NET_DATA2 = NET_DATA2.rename(columns={"TE2": "TE2", "seTE2": "seTE2", "n12": "n1", "n22": "n2"})
DEFAULT_ELEMENTS = USER_ELEMENTS = get_network_new(df=NET_DATA, i=0)
DEFAULT_ELEMENTS2 = USER_ELEMENTS2 = get_network_new(df=NET_DATA2, i=1)
# FOREST_DATA = pd.read_csv('db/forest_data/forest_data.csv')
# FOREST_DATA_OUT2 = pd.read_csv('db/forest_data/forest_data_outcome2.csv')
FOREST_DATA = pd.read_csv("db/forest_data/forest_data_out1.csv")
FOREST_DATA_OUT2 = pd.read_csv("db/forest_data/forest_data_out2.csv")
FOREST_DATA_PRWS = pd.read_csv("db/forest_data/forest_data_pairwise.csv")
FOREST_DATA_PRWS_OUT2 = pd.read_csv("db/forest_data/forest_data_pairwise_out2.csv")
LEAGUE_TABLE_DATA1: DataFrame = pd.read_csv(
    "db/league_table_data/league_1.csv", index_col=0
)
LEAGUE_TABLE_DATA2: DataFrame = pd.read_csv(
    "db/league_table_data/league_2.csv", index_col=0
)
LEAGUE_TABLE_DATA_BOTH: DataFrame = pd.read_csv(
    "db/league_table_data/league_table.csv", index_col=0
)

##THESE SHOULD BE PUT INTO A FUNCTION
N_CLASSES = (
    USER_ELEMENTS[-1]["data"]["n_class"]
    if "n_class" in USER_ELEMENTS[-1]["data"]
    else 1
)
OPTIONS_VAR = [
    {"label": "{}".format(col), "value": col}
    for col in NET_DATA.select_dtypes(["number"]).columns
]

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
LEAGUE_TABLE_DATA_BOTH = LEAGUE_TABLE_DATA_BOTH.fillna("")
LEAGUE_TABLE_DATA_BOTH = pd.DataFrame(
    [
        [replace_and_strip(col) for col in list(row)]
        for idx, row in LEAGUE_TABLE_DATA_BOTH.iterrows()
    ],
    columns=LEAGUE_TABLE_DATA_BOTH.columns,
    index=LEAGUE_TABLE_DATA_BOTH.index,
)

CINEMA_NET_DATA1 = pd.read_csv("db/Cinema/cinema_report_PASI90.csv")
CINEMA_NET_DATA2 = pd.read_csv("db/Cinema/cinema_report_SAE.csv")
CONSISTENCY_DATA = pd.read_csv("db/consistency/consistency.csv")
NETSPLIT_DATA = pd.read_csv("db/consistency/node_split_out1.csv")
NETSPLIT_DATA_OUT2 = pd.read_csv("db/consistency/node_split_out2.csv")
NETSPLIT_DATA_ALL = pd.read_csv("db/consistency/netsplit_all.csv")
NETSPLIT_DATA_ALL_OUT2 = pd.read_csv("db/consistency/netsplit_all_out2.csv")
RANKING_DATA = pd.read_csv("db/ranking/rank.csv")
RANKING_DATA2 = pd.read_csv("db/ranking/rank2.csv")
FUNNEL_DATA = pd.read_csv("db/funnel/funnel_data.csv")
FUNNEL_DATA_OUT2 = pd.read_csv("db/funnel/funnel_data_out2.csv")

PSORIASIS_DATA = {
    "nmastudio-version": "2.0",
    "raw_data_STORAGE": {"data": RAW_DATA.to_json(orient="split")},
    "net_data_STORAGE": {
        "data": NET_DATA.to_json(orient="split"),
        "elements_out1": DEFAULT_ELEMENTS,
        "elements_out2": DEFAULT_ELEMENTS2,
        "n_classes": USER_ELEMENTS[-1]["data"]["n_class"]
        if "n_class" in USER_ELEMENTS[-1]["data"]
        else 1,
    },
    "league_table_data_STORAGE": [
        LEAGUE_TABLE_DATA1.to_json(orient="split"),  # Outcome 1
        LEAGUE_TABLE_DATA2.to_json(orient="split"),  # Outcome 2
        LEAGUE_TABLE_DATA_BOTH.to_json(orient="split"),  # Both outcomes combined
    ],
    "consistency_data_STORAGE": [
        CONSISTENCY_DATA.to_json(orient="split"),
        CONSISTENCY_DATA.to_json(orient="split"),  # Placeholder for outcome 2
    ],
    "forest_data_STORAGE": [
        FOREST_DATA.to_json(orient="split"),
        FOREST_DATA_OUT2.to_json(orient="split"),
    ],
    "forest_data_prws_STORAGE": [
        FOREST_DATA_PRWS.to_json(orient="split"),
        FOREST_DATA_PRWS_OUT2.to_json(orient="split"),
    ],
    "ranking_data_STORAGE": [
        RANKING_DATA.to_json(orient="split"),
        RANKING_DATA2.to_json(orient="split"),
    ],
    "funnel_data_STORAGE": [
        FUNNEL_DATA.to_json(orient="split"),
        FUNNEL_DATA_OUT2.to_json(orient="split"),
    ],
    "net_split_data_STORAGE": [
        NETSPLIT_DATA.to_json(orient="split"),
        NETSPLIT_DATA_OUT2.to_json(orient="split"),
    ],
    "net_split_ALL_data_STORAGE": [
        NETSPLIT_DATA_ALL.to_json(orient="split"),
        NETSPLIT_DATA_ALL_OUT2.to_json(orient="split"),
    ],
    "results_ready_STORAGE": True,
    "effect_modifiers_STORAGE": ["age", "bmi", "weight", "male_percentage"],
    "uploaded_datafile_to_disable_cinema": {"filename": "psoriasis_long_complete.csv"},
    "R_errors_STORAGE": {},
    "number_outcomes_STORAGE": 2,
    "outcome_names_STORAGE": ["PASI90", "SAE"],
    "cinema_net_data_STORAGE": [
        CINEMA_NET_DATA1.to_json(orient="split"),
        CINEMA_NET_DATA2.to_json(orient="split"),
    ],
    "cinema_net_data_STORAGE2": [
        CINEMA_NET_DATA1.to_json(orient="split"),
        CINEMA_NET_DATA2.to_json(orient="split"),
    ],
    "protocol_link_STORAGE": "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011535.pub4/full",
    "project_title_STORAGE": "Systemic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis",
}
