import dash
from dash import html, dcc

dash.register_page(__name__,
                   path='/',
                   name='Home',
                   title="Geo Data Maps",
                   description="Landing Page for all available maps",
                   order=0,
                   top_menu=True
                   )


layout = html.Div([

    html.H3('Swiss Geo Data Maps'),

    html.Div([
        html.Div([
            html.P([html.Img(src="assets/logo.png", alt="Swiss Geo Data Maps Logo", className="logo"),
               'Welcome to the Swiss Geo Data Maps Project. '
               'We aim to provide open source geospatial data visualizations making it easy for everyone '
               'to access and understand geospatial data and information.',
            html.P('We are constantly working on new maps and features, so stay tuned!')], className="long-text")]),
    ], className="logo-text-box"),

])

