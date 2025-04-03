# Title     :  Dash NMA app
# Objective :  visualisation of network meta-analysis based on network interactivity
# Created by:  Silvia Metelli
# Created on: 10/11/2020
# --------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------#
# --------------------------------------------------------------------------------------------------------------------#

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use default values

# Set DEBUG_MODE from environment variable, default to False
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

from dash import dash, html, dcc, Output, Input, State, ctx
from tools.navbar import Navbar
from assets.storage import TODAY, SESSION_TYPE, get_new_session_id

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

NMASTUDIO_art = "/assets/logos/nmastudio_art2.gif"
LOAD = "/assets/logos/small.gif"

server = app.server


def get_new_layout():
    SESSION_ID = get_new_session_id()
    return html.Div(
        [
            dcc.Location(id="url", refresh="callback-nav"),
            Navbar(),
            dcc.Store(
                id="consts_STORAGE",
                data={"today": TODAY, "session_ID": SESSION_ID},
                storage_type=SESSION_TYPE,
            ),
            dash.page_container,
        ]
    )


app.layout = get_new_layout()

if __name__ == "__main__":
    # app._favicon = ("assets/favicon.ico")
    # app.title = 'NMAstudio' #TODO: title works fine locally, does not on Heroku
    # context = generate_ssl_perm_and_key(cert_name='cert.pem', key_name='key.pem')
    # app.run(debug=False, ssl_context=context)
    app.run(host="macas.lan", debug=DEBUG_MODE)  # change port or remove if needed
