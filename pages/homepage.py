import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash import Input, Output, State, ALL, callback
from dash_extensions import Download
from dash_extensions.snippets import send_file

dash.register_page(__name__, path="/", redirect_from=["/home"])

MAIN_PIC = "/assets/logos/mainpage.png"
BOXPLOT = "/assets/logos/boxplot.gif"
NETPLOT = "/assets/logos/network.gif"
FOREST = "/assets/logos/forest.gif"
TABLE = "/assets/logos/table.gif"
CONS = "/assets/logos/consist.gif"
RANK = "/assets/logos/rank.gif"
FUNEL = "/assets/logos/funel.gif"
OSLO_LOGO = "/assets/logos/oslo_logo.png"
UP_LOGO = "/assets/logos/universite.jpeg"
CRESS_LOGO = "/assets/logos/cress_logo2.jpeg"
inserm_logo = "/assets/logos/inserm_logo.png"
###################homepage###############################

layout = html.Div(
    [
        html.Div(
            [
                html.H2(
                    [
                        html.Span("Welcome ", className="title-word title-word-1"),
                        html.Span("to ", className="title-word title-word-2"),
                        html.Span("NMA", className="title-word title-word-3"),
                        html.Span("studio 2.0", className="title-word title-word-4"),
                    ],
                    className="title",
                )
            ],
            # style={"fontSize": '40px',
            #        'textAlign': 'center',
            #        'color':'#5c7780',
            #        'fontFamily':'sans-serif'},
            className="container",
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        #  dcc.Markdown('NMAstudio serves as an interactive web application designed to simplifies the whole Network Meta-Analysis (NMA) procedures and enhances the visualization of results.',
        #                 className="markdown_style", style={"color": "black", "marginRight":"10%"}),
        #                 html.Div([dcc.Markdown("We strongly advise you to download and review the Tutorial prior to using it:", className="markdown_style",
        #                 style={'marginRight':'5px', 'display':'inline-block', "color": "black"}),
        #                 html.Button('Tutorial', id='full-tuto-pdf',
        #                          style={'color': 'black',
        #                                 'display': 'inline-block',
        #                                 'marginLeft':'-23px',
        #                                 'padding': '4px'}),
        #                 Download(id="download-tuto")]),
        # html.Br(),
        html.Div(html.Img(src=MAIN_PIC, width="1200px", className="main_pic")),
        html.Br(),
        # html.Div([html.Span('What', style={'--i':'1'}),
        #     html.Span('results',style={'--i':'2'}),
        #     html.Span('you', style={'--i':'3'}),
        #     html.Span('can', style={'--i':'4'}),
        #     html.Span('get', style={'--i':'5'}),
        #     html.Span('from', style={'--i':'6'}),
        #     html.Span('NMAstudio?', style={'--i':'7'}),],
        # # style={"fontSize": '40px',
        # #        'textAlign': 'center',
        # #        'color':'#5c7780',
        # #        'fontFamily':'sans-serif'},
        #        className='waviy'),
        dcc.Markdown(
            "What results you can get from NMAstudio?",
            className="markdown_style_main",
            style={
                "fontSize": "30px",
                "textAlign": "center",
                "color": "#5c7780",
            },
        ),
        html.Br(),
        html.Br(),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Img(
                                    src=NETPLOT,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Network plot for interventions",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=BOXPLOT,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Boxplots for transitivity assessment",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=FOREST,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Forest plots for direct and network estimates",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=TABLE,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "League Table for relative effects",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=RANK,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Ranking plots for interventions",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=CONS,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Global & Local consistency assessment",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                        dbc.Col(
                            [
                                html.Img(
                                    src=FUNEL,
                                    width="70px",
                                    style={"justifySelf": "center"},
                                ),
                                html.Span(
                                    "Funnel plots for small-study effect",
                                    className="main_results",
                                ),
                            ],
                            className="col_results",
                        ),
                    ],
                    style={
                        "width": "-webkit-fill-available",
                        "justifyContent": "center",
                    },
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown(
            "Before uploading your data, you can:",
            className="markdown_style_main",
            style={
                "fontSize": "25px",
                "textAlign": "center",
                "color": "#5c7780",
            },
        ),
        html.Br(),
        dbc.Row(
            [
                html.Div(
                    [
                        html.Button(
                            "Download demonstration data",
                            id="demodata",
                            style={"display": "inline-block", "padding": "1px"},
                        ),
                        Download(id="download-demodata"),
                    ]
                ),
                html.Span(
                    "and",
                    style={"justifySelf": "center", "alignSelf": "center"},
                ),
                html.Div(
                    [
                        html.Button(
                            "See the explanation of the variables",
                            id="data_explain",
                            style={"display": "inline-block", "padding": "1px"},
                        ),
                        Download(id="download-data-explain"),
                    ]
                ),
            ],
            style={
                "display": "grid",
                "width": "40%",
                "justifySelf": "center",
                "gridTemplateColumns": "1fr 1fr 1fr",
            },
        ),
        html.Br(),
        html.Br(),
        dbc.NavLink(
            "Click to watch the tutorial video",
            href="https://youtu.be/CGj729iqBOQ",
            target="_blank",
            external_link=True,
            className="tutorial-link",
            style={
                "color": "orange",
                "textDecoration": "unset",
                "fontSize": "x-large",
                "display": "block",
                "marginRight": "20px",
            },
        ),
        html.Span(
            "More tutorials coming soon...",
            style={"justifySelf": "center", "alignSelf": "center"},
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown(
            "Now you are ready to:",
            className="markdown_style_main",
            style={
                "fontSize": "25px",
                "textAlign": "center",
                "color": "#5c7780",
            },
        ),
        html.Br(),
        dbc.Row(
            html.Button(
                dbc.NavLink(
                    "Start",
                    href="/setup",
                    external_link=True,
                    className="upload_data",
                    n_clicks=0,
                    id="upload_homepage",
                ),
                style={
                    "color": "white",
                    "backgroundColor": "orange",
                    "height": "fit-content",
                    "display": "inline-block",
                    "justifySelf": "center",
                    "border": "unset",
                    "padding": "4px",
                },
            ),
            style={"display": "grid"},
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        dcc.Markdown(
            "Any questions?",
            className="markdown_style_main",
            style={
                "fontSize": "25px",
                "textAlign": "center",
                "color": "#5c7780",
            },
        ),
        html.Br(),
        html.Span(
            "Please get in touch at tianqi.yu@etu.u-paris.fr",
            style={
                "justifySelf": "center",
                "fontWeight": "bold",
                "fontSize": "large",
            },
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Markdown(
                            "Contributors",
                            className="markdown_style_main",
                            style={
                                "fontSize": "20px",
                                "textAlign": "center",
                                "color": "orange",
                                "borderBottom": "2px solid",
                                "fontWeight": "bold",
                                "height": "fit-content",
                                "marginRight": "20px",
                            },
                        ),
                        dbc.NavLink(
                            "Tianqi Yu",
                            href="https://www.cer-methods.com/tianqi-yu/",
                            external_link=True,
                            style={
                                "color": "#5b7780",
                                "textDecoration": "unset",
                                "fontSize": "large",
                                "display": "block",
                                "marginRight": "20px",
                            },
                        ),
                        dbc.NavLink(
                            "Anna Chaimani",
                            href="https://www.cer-methods.com/anna/",
                            external_link=True,
                            style={
                                "color": "#5b7780",
                                "textDecoration": "unset",
                                "fontSize": "large",
                                "display": "block",
                                "marginRight": "20px",
                            },
                        ),
                        dbc.NavLink(
                            "Silvia Metelli",
                            href="https://www.cer-methods.com/team/",
                            external_link=True,
                            style={
                                "color": "#5b7780",
                                "textDecoration": "unset",
                                "fontSize": "large",
                                "display": "block",
                                "marginRight": "20px",
                            },
                        ),
                        dbc.NavLink(
                            "Thodoris Papakonstantinou",
                            href="https://www.cer-methods.com/team/",
                            external_link=True,
                            style={
                                "color": "#5b7780",
                                "textDecoration": "unset",
                                "fontSize": "large",
                                "display": "block",
                                "marginRight": "20px",
                            },
                        ),
                    ],
                    style={
                        "textAlign": "center",
                        "display": "grid",
                        "justifyContent": "space-around",
                        "borderRight": "2px solid orange",
                        "marginBottom": "2%",
                    },
                ),
                dbc.Col(
                    [
                        dcc.Markdown(
                            "Other Information",
                            className="markdown_style_main",
                            style={
                                "fontSize": "20px",
                                "textAlign": "center",
                                "color": "orange",
                                "borderBottom": "2px solid",
                                "fontWeight": "bold",
                                "height": "fit-content",
                                # 'marginLeft': '20px',
                                "width": "100%",
                                "marginTop": "0",
                            },
                        ),
                        dcc.Markdown(
                            "Please cite us as: Tianqi Y, Silvia M, Chaimani A. NMAstudio: a fully interactive web-application for producing and visualising network meta-analyses. *Cochrane Colloquium 2023, London, UK.*",
                            className="markdown_style",
                            style={"color": "black", "marginRight": "10%"},
                        ),
                        html.Br(),
                        dcc.Markdown(
                            "NMAstudio is a web application to produce and visualise interactive outputs from network meta-analyses. NMAstudio is written in Python, and linked to the R-package netmeta for performing network meta analysis.",
                            className="markdown_style",
                            style={"color": "black", "marginRight": "10%"},
                        ),
                        dbc.NavLink(
                            "Balduzzi, S., Rücker, G., Nikolakopoulou, A., Papakonstantinou, T., Salanti, G., Efthimiou, O., & Schwarzer, G. (2023). netmeta: An R Package for Network Meta-Analysis Using Frequentist Methods. Journal of Statistical Software, 106(2), 1-40. https://doi.org/10.18637/jss.v106.i02",
                            href="https://www.jstatsoft.org/article/view/v106i02",
                            external_link=True,
                            className="markdown_style",
                            style={"fontSize": "14px", "color": "#3498db"},
                        ),
                        html.Br(),
                        html.Br(),
                        dcc.Markdown(
                            "Embedded and demonstration datasets taken from:",
                            className="markdown_style",
                            style={
                                "marginRight": "0px",
                                "display": "inline-block",
                                "color": "black",
                            },
                        ),
                        dbc.NavLink(
                            "Sbidian E, Chaimani A, Garcia-Doval I, Doney L, Dressler C, Hua C, et al. Systemic pharmacological treatments for chronic plaque psoriasis: a network meta-analysis. \n Cochrane Database Syst Rev. 2021 Apr 19;4:CD011535.",
                            href="https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD011535.pub4/full",
                            className="markdown_style",
                            external_link=True,
                            style={
                                "fontSize": "14px",
                                "color": "#3498db",
                                "marginRight": "10%",
                            },
                        ),
                        html.Br(),
                        html.Br(),
                    ],
                    style={"width": "80%", "paddingLeft": "3%"},
                ),
            ],
            style={
                "height": "fit-content",
                "backgroundColor": "antiquewhite",
                "justifyContent": "center",
            },
        ),
        #     html.Br(), html.Br(),html.Br(),
        html.Footer(
            [
                html.P(
                    "Copyright © 2025. All rights reserved.",
                    style={"color": "white", "marginLeft": "45px", "marginTop": "2%"},
                ),
                dcc.Markdown(
                    "This project has received funding from the EU H2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 101031840 & the French National Research Agency under the project ANR-22-CE36-0013-01",
                    className="markdown_style",
                    style={
                        "color": "white",
                        "fontWeight": "330",
                        "fontSize": "14px",
                        "paddingLeft": "3%",
                    },
                ),
                #  dcc.Markdown('Project team members: \nAnna Chaimani  Silvia Metelli  Tianqi Yu',
                #  className="markdown_style",style={"color": "white", "fontWeight": "330", "fontSize":"14px", 'whiteSpace': 'pre'}),
                dbc.Col(
                    [
                        html.Img(src=OSLO_LOGO, height="57px"),
                        html.Img(src=UP_LOGO, height="57px"),
                        html.Img(src=CRESS_LOGO, height="57px"),
                        html.Img(src=inserm_logo, height="57px"),
                    ],
                    style={
                        "paddingRight": "1%",
                        "paddingTop": "0.3%",
                        "paddingBottom": "0.3%",
                        "borderTop": "solid",
                        "display": "flex",
                        "marginLeft": "10px",
                        "justifyContent": "space-between",
                        "width": "700px",
                        "marginLeft": "43px",
                    },
                    width="auto",
                ),
            ],
            className="__footer",
        ),
    ],
    style={"display": "grid"},
)


### download demo data ####
@callback(
    Output("download-demodata", "data"),
    Input("demodata", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return send_file("db/psoriasis_long_complete.csv")


@callback(
    Output("download-data-explain", "data"),
    Input("data_explain", "n_clicks"),
    prevent_initial_call=True,
)
def func_explain(n_clicks):
    return send_file("Documentation/variables_explain.pdf")
