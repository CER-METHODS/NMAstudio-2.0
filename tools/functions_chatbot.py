# from dash import html
# import dash_bootstrap_components as dbc
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq
# from dash import dcc
# from dash import html

# ##################### input box#################################################################
# def render_chat_input():
#     chat_input = dbc.InputGroup(
#         children=[
#             dbc.Input(id="user-input", 
#                       placeholder="e.g. What is the side effects of eicosatetraenoic acid (ETA)?", 
#                       type="text", style={'width': '95%'}),
#             dbc.Button(id="submit", children=">", color="success"),
#         ],
#         style={'width': '95%','display': 'flex', 'justify-content': 'center'}
#     )
#     return chat_input

# ##################### chat box#################################################################

# def render_textbox(text:str, box:str = "AI"):
#     text = text.replace(f"ChatBot:", "").replace("Human:", "")
#     style1 = {
#         "max-width": "350px",
#         "width": "fit-content",
#         "padding": "5px 10px",
#         "border-radius": 25,
#         "margin-bottom": 10,
#         "margin-top": 10,
#         'border': '0px solid',
#         'display': 'inline-flex',
#         'background-color': '#149a80',
#         'color': 'white'
#     }
#     style2 = {
#         "max-width": "350px",
#         "width": "max-content",
#         "padding": "5px 10px",
#         "border-radius": 25,
#         "margin-bottom": 10,
#         "margin-top": 10,
#         'border': '0px solid',
#         'display': 'inline-flex',
#         'background-color': 'beige',
#     }

#     if box == "human":
#         style1["margin-left"] = "auto"
#         style1["margin-right"] = 0

#         thumbnail_human = html.Img(
#             src='/assets/icons/human.png',
#             style={
#                 "border-radius": 50,
#                 "height": 28,
#                 "margin-left": 5,
#                 "margin-top": 10,
#                 "float": "right",
#                 'display': 'inline-flex'
#             },
#         )
#         textbox_human = dbc.Card(text, style=style1, body=True, color='dark', inverse=True)
#         return html.Div([textbox_human,thumbnail_human,],
#                          style={'display': 'inline-flex','justify-content': 'end'}
#                          )

#     elif box == "AI":
#         style2["margin-left"] = 0
#         style2["margin-right"] = "auto"

#         thumbnail = html.Img(
#             src='/assets/icons/chatbot.png',
#             style={
#                 "border-radius": 50,
#                 "height": 28,
#                 "margin-right": 5,
#                 "margin-top": 10,
#                 "float": "left",
#                 'display': 'inline-flex'
#             },
#         )
#         textbox = dbc.Card(text, style=style2, body=True, color="light", inverse=False)

#         return html.Div([thumbnail, textbox])

#     else:
#         raise ValueError("Incorrect option for `box`.")
    
# ##################### chat model#################################################################
# import os
# llm = ChatGroq(temperature=0.8, 
#                model_name="llama-3.1-8b-instant",
#                api_key = os.getenv("API_KEY"),
#                max_tokens=300
#                )
# # Define the system message introducing the AI assistant's capabilities.
# system = "You are a experienced clinicians."

# # Define a placeholder for the user's input.
# human = "{text}"

# # Create a chat prompt consisting of the system and human messages.
# prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

# chain = prompt | llm

# ##################### chat model#################################################################
# # define layout
# chatbot_layout = html.Div(
#     html.Div(id="display-conversation", style={'display': 'grid'}),
#     style={
#         "overflow-y": "auto",
#         "display": "flex",
#         "height": "90%",
#         "width": "100%",
#         # "height": "calc(90vh - 132px)",
#         "flex-direction": "column-reverse",
#     },
# )

# def render_chatbot():
#     return html.Div(
#         [
#             dcc.Store(id="store-conversation", data=""),
#             dbc.Container(
#                 fluid=True,
#                 children=[
#                     dbc.Row(
#                         [
#                             dbc.Col(width=1),
#                             dbc.Col(
#                                 width=10,
#                                 children=dbc.Card(
#                                     [
#                                         dbc.CardBody([
#                                             chatbot_layout,
#                                             html.Div(render_chat_input(), 
#                                                      style={'margin-bottom': '20px',
#                                                             'width': '95%', 'justify-items': 'center'}
#                                                      ),
#                                             dbc.Spinner(html.Div(id="loading-component")),
#                                         ],style={"height": "100%","width": "100%",})
#                                     ],
#                                     style={'border-radius': 25, 
#                                            'background': '#FFFFFF', 
#                                            'border': '0px solid',
#                                            "height": "100%","width": "100%"}
#                                 )
#                             ,style={"height": "100%","width": "100%",}),
#                             dbc.Col(width=1),
#                         ],style={"height": "100%","width": "100%",})
#                 ]
#             ,style={"height": "100%","width": "100%"}),
#         ],style={"height": "95%","width": "95%",})


