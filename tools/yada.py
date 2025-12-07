from dash_yada import YadaAIO

hover_message_dict = {
    "name": "Hedwig",
    "greeting": "I'm Your Automated Dashboard Assistant. But you can call me XXX!\nClick me to get started.",
}

steps_offcanvas_style = {
    "boxShadow": "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
    "margin": "8px auto",
    "padding": "0px 24px 5px",
    "backgroundColor": "var(--bs-gray-500)",
    "color": "white",
    "borderRadius": 12,
    "maxWidth": 800,
}

housekeeping_script = [
    {
        "target": ".title",
        "convo": """
                First, a few housekeeping notes:            
                - You can close this dialogue box to see the whole screen, then click on me to continue
                - Press the escape key any time to exit the tour                   
                """,
    },
]
dev_intro_script = (
    [
        {
            "target": "#title",
            "convo": """
            ##### I'll show you how to create a fun interactive demo so people can get the most out of your site.  
            For more information about adding this component to your app, see [Dash Yada Github](https://github.com/BSd3v/dash-yada)
            
            """,
        }
    ]
    + housekeeping_script
    + [
        {
            "target": "#title",
            "convo": """
                I navigate using [selectors](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector) so I can go to any element on the page.        
                We are now at the title.  Here you can describe the overview and purpose of your site.  
                Next, I'll show how to filter the AG Grid component.
                """,
        },
    ]
)


yada_stand = YadaAIO(
    yada_id="demo",
    hover_message_dict=hover_message_dict,
    next_button_props={
        "size": "sm",
    },
    prev_button_props={
        "size": "sm",
        "children": "prev",
    },
    # steps_offcanvas_style=steps_offcanvas_style,
    scripts={
        "Intro": [
            {
                "target": "#yoda_stand_start",
                "convo": "Welcome to My Dashboard tour!",
            },
        ]
    },
)