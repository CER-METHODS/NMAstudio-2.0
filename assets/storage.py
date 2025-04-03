######SESSION AND LOCALSTORAGE INITIALIZATION#######

# from assets.modal_values import *
from dash import dcc
from assets.psoriasisDemo import PSORIASIS_DATA
import pandas as pd
import json

# from collections import OrderedDict
import datetime, uuid
from dash.dependencies import Output, State

SESSION_PICKLE = {"wait": False}
get_new_session_id = lambda: uuid.uuid4().__str__()
SESSION_TYPE = "local"  # localstorage

TODAY = str(datetime.datetime.today().date())

# All state should be described here and the respect this dict
#
# ============================================================================
# STORAGE SCHEMA DOCUMENTATION - Version 2.0 (List Format)
# ============================================================================
#
# Single-data storage (raw_data_STORAGE, net_data_STORAGE):
#   raw_data_STORAGE = {
#       "data": <json_string>  # DataFrame.to_json(orient="split")
#   }
#
#   net_data_STORAGE = {
#       "data": <json_string>,      # REQUIRED: DataFrame.to_json(orient="split")
#       "elements_out1": <list>,    # Optional: Network elements for outcome 1
#       "elements_out2": <list>,    # Optional: Network elements for outcome 2
#       "n_classes": <int>          # Optional: Number of RoB classes
#   }
#
# Multi-outcome storage (forest_data_STORAGE, ranking_data_STORAGE, etc.):
#   forest_data_STORAGE = [
#       <json_string_outcome1>,  # DataFrame.to_json(orient="split")
#       <json_string_outcome2>,  # DataFrame.to_json(orient="split")
#       <json_string_outcome3>,  # DataFrame.to_json(orient="split")
#   ]
#
# Effect modifiers:
#   effect_modifiers_STORAGE = ["age", "weight", "male"]  # List of modifier names
#
# Access pattern:
#   from tools.utils import get_net_data_json
#
#   # Single data:
#   json_str = get_net_data_json(net_data_STORAGE)
#   df = pd.read_json(json_str, orient="split")
#
#   # Multi-outcome (list format):
#   json_str = forest_data_STORAGE[outcome_index]  # outcome_index = 0, 1, 2, ...
#   df = pd.read_json(json_str, orient="split")
#
# ============================================================================
#
STORAGE_SCHEMA = {
    "nmastudio-version": "version",
    "raw_data_STORAGE": "dict",
    "net_data_STORAGE": "dict",
    "league_table_data_STORAGE": "list",  # List of JSON strings for multiple outcomes
    "consistency_data_STORAGE": "list",
    "forest_data_STORAGE": "list",
    "forest_data_prws_STORAGE": "list",
    "ranking_data_STORAGE": "list",
    "funnel_data_STORAGE": "list",
    "net_split_data_STORAGE": "list",
    "net_split_ALL_data_STORAGE": "list",
    "net_download_activation": "bl",
    "results_ready_STORAGE": "bl",
    "effect_modifiers_STORAGE": "list",  # List of effect modifier names
    "uploaded_datafile_to_disable_cinema": "dict",
    "R_errors_STORAGE": "dict",
    "number_outcomes_STORAGE": "dict",
    "outcome_names_STORAGE": "dict",
}

EMPTY_STORAGE = {
    "nmastudio-version": "2.0",
    "raw_data_STORAGE": {},
    "net_data_STORAGE": {},
    "league_table_data_STORAGE": [],
    "consistency_data_STORAGE": [],
    "forest_data_STORAGE": [],
    "forest_data_prws_STORAGE": [],
    "ranking_data_STORAGE": [],
    "funnel_data_STORAGE": [],
    "net_split_data_STORAGE": [],
    "net_split_ALL_data_STORAGE": [],
    "net_download_activation": False,
    "results_ready_STORAGE": False,
    "effect_modifiers_STORAGE": [],
    "uploaded_datafile_to_disable_cinema": {},
    "R_errors_STORAGE": {},
    "number_outcomes_STORAGE": {},
    "outcome_names_STORAGE": {},
}


STORAGE_KEYS = list(STORAGE_SCHEMA.keys())

STORAGESTATE = [State(id, "data") for id in list(STORAGE_SCHEMA.keys())]

# They are located in the dcc.store object in the browser
STORAGEOUTPUT = [
    Output(id, "data", allow_duplicate=True) for id in list(STORAGE_SCHEMA.keys())
]


def __get_state_of(stid):
    STKEYS = [id for id in list(STORAGE_SCHEMA.keys())]
    return STKEYS.index(stid)


def storage_keys():
    return list(STORAGE_SCHEMA.keys())


# get initial type of storage value
def init_type(stkey):
    match STORAGE_SCHEMA[stkey]:
        case "dict":
            stype = dict()
        case "list":
            stype = list()
        case "bl":
            stype = False
        case "strng":
            stype = "Nothing"
        case "version":
            stype = "2.0"
        case _:
            stype = dict()
    return stype


# Update dcc.Store (it is a list)
def __empty_project():
    return [
        dcc.Store(id="nmastudio-version", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="raw_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="net_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="league_table_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="consistency_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="forest_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="forest_data_prws_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="ranking_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="funnel_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="net_split_data_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(
            id="net_split_ALL_data_STORAGE", data=None, storage_type=SESSION_TYPE
        ),
        dcc.Store(id="net_download_activation", data=False, storage_type=SESSION_TYPE),
        dcc.Store(id="results_ready_STORAGE", data=False, storage_type=SESSION_TYPE),
        dcc.Store(id="effect_modifiers_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(
            id="uploaded_datafile_to_disable_cinema",
            data=None,
            storage_type=SESSION_TYPE,
        ),
        dcc.Store(id="R_errors_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="number_outcomes_STORAGE", data=None, storage_type=SESSION_TYPE),
        dcc.Store(id="outcome_names_STORAGE", data=None, storage_type=SESSION_TYPE),
    ]


# Project must be already jsonified
def __load_project(storagium, prjct):
    strg = [prjct.get(label) for label in list(STORAGE_SCHEMA.keys())]
    return strg


# Storage as list passed from State
def __storage_to_dict(storagium):
    return dict(zip(STORAGE_KEYS, storagium))


# Start with empty storage
STORAGE = __empty_project()

# STORAGE = __load_project(__empty_project(), PSORIASIS_DATA)
