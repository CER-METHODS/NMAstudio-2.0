import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, html, dcc
# from assets.Tabs.saveload_modal_button import saveload_modal

NMASTUDIO_LOGO = "/assets/logos/NMAstudio_bold.png"
CRESS_LOGO = "/assets/logos/CRESS_logo.png"
UP_LOGO = "/assets/logos/logo_universite_paris.jpg"


def Navbar():
    realhome_button = dbc.NavItem(
        dbc.NavLink(
            "HOME",
            href="/home",
            external_link=True,
            style={"color": "#white", "fontFamily": "sans-serif ", "fontSize": "15px"},
        )
    )
    results_button = dbc.NavItem(
        dbc.NavLink(
            "RESULTS",
            href="/results",
            external_link=True,
            style={
                "color": "#white",
                "fontFamily": "sans-serif ",
                "fontSize": "15px",
            },
        )
    )
    skt_button = dbc.NavItem(
        dbc.NavLink(
            "Knowledge Translation",
            href="/knowledge-translation",
            external_link=True,
            style={
                "color": "#white",
                "fontFamily": "sans-serif ",
                "fontSize": "15px",
            },
            id="skt_button",
        )
    )
    setup_button = dbc.NavItem(
        dbc.NavLink(
            "SETUP",
            href="/setup",
            external_link=True,
            style={
                "color": "#white",
                "fontFamily": "sans-serif ",
                "fontSize": "15px",
            },
            id="",
        )
    )
    # skt_button = dbc.NavItem(dbc.NavLink('SKT TOOL', n_click=0,
    #                                      style = {'color':'#white','font-family': "sans-serif ",
    #                                               'font-size': '13px', 'pointer-events': 'stroke',
    #                                               'padding': 'unset',
    #                                               'margin-top':'-7px', 'border': 'none'}, id= 'skt_button'))

    # doc_button = dbc.NavItem(dbc.NavLink('DOCUMENTATION', href="/doc", external_link=True,
    #                                      style = {'color':'#white','font-family': "sans-serif ",
    #                                               'font-size': '13px' }))
    # news_button = dbc.NavItem(dbc.NavLink('NEWS', href="/news", external_link=True,
    #                                      style = {'color':'#white','font-family': "sans-serif ",
    #                                               'font-size': '13px' }))

    # saveload_button = saveload_modal

    navbar = dbc.Navbar(
        [
            html.Div(
                dbc.Col(
                    html.Img(
                        src=NMASTUDIO_LOGO,
                        height="53px",
                        style={
                            "filter": "invert()",
                            # 'filter': 'invert(42 %) sepia(26 %) saturate(2474 %) hue-rotate(218deg) brightness(97 %) contrast(89 %)',
                            #'filter': 'invert(44%) sepia(57%) saturate(3117%) hue-rotate(147deg) brightness(99%) contrast(94%)',
                            "paddingLeft": "2%",
                            "paddingRight": "2%",
                            "paddingBottom": "0.4%",
                            "paddingTop": "0.4%",
                            "marginLeft": "50px",
                        },
                    ),
                    className="child",
                    sm=3,
                    md=2,
                ),
                style={
                    # "border": "0.01px white solid",
                    "paddingBottom": "0.6%",
                    "paddingLeft": "0.6%",
                    "paddingRight": "0.6%",
                    "paddingTop": "0.6%",
                    # 'backgroundColor':'#304569'
                },
            ),
        # Browser compatibility warning - shown to non-Chrome users
        # The browser-warning.js script in assets/ will show this for non-Chrome browsers
        html.Div(
            [
                html.Span(
                    "Warning: ",
                    style={"fontWeight": "bold"},
                ),
                html.Span(
                    "For the best experience, please use Google Chrome. "
                    "Some features may not work properly in other browsers (Firefox, Safari, Edge)."
                ),
            ],
            id="browser-warning",
            className="browser-warning",
            style={
                "fontSize": "18px",
                "textAlign": "center",
                "color": "white",
                "backgroundColor": "rgb(222, 132, 83)",
                "padding": "12px 20px",
                "borderRadius": "8px",
                "margin": "0 auto",
                "maxWidth": "800px",
                "display": "none",  # Hidden by default, shown by browser-warning.js
            },
        ),
            html.Div(
                [
                    dbc.Col(
                        children=[
                            dbc.Nav(
                                [
                                    realhome_button,
                                    setup_button,
                                    results_button,
                                    skt_button,
                                ],
                                navbar=True,
                                style={
                                    "textAlign": "center",
                                    "paddingRight": "5%",
                                    "paddingTop": "0.5%",
                                    "marginLeft": "50px",
                                    "justifyContent": "end",
                                },
                            ),
                        ]
                    ),
                    # Toggle theme
                    # dbc.Col([html.P(
                    #     "Light",
                    #     id='light_theme',
                    #     style={'display': 'inline-block',
                    #            'margin': 'auto', 'color':'white',
                    #            'font-size': '10px',
                    #            'padding-left': '0px'}),
                    #     daq.ToggleSwitch(
                    #         id='toggleTheme', value=True, color="#00418e",
                    #         size=40, vertical=False,
                    #         label={'label': "",
                    #                'style': dict(color='white', font='0.5em')},
                    #         labelPosition="top",
                    #         style={'display': 'inline-block',
                    #                'margin': 'auto', 'font-size': '10px',
                    #                'padding-left': '2px',
                    #                'padding-right': '2px'}),
                    #     html.P('Dark',
                    #            id='dark_theme',
                    #            style={'display': 'inline-block',
                    #                   'margin': 'auto', 'color':'white',
                    #                   'font-size': '10px',
                    #                   'padding-right': '10px'})
                    #
                    # ], style={'display': 'inline-block',
                    #           'margin-top': '10px',  'margin-right': '25px'}
                    # ),
                    # dbc.Col(html.Img(src=UP_LOGO, height="57px"), style={'padding-right':'1%','padding-top':'0.3%','padding-bottom':'0.3%'},
                    #     width="auto")
                ],
                className="child child-right",
            ),
        ],
        color="#5c7780",
        dark=True,
    )

    return navbar
