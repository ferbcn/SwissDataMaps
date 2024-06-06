import dash
from dash import html, dcc


def build_nav_links():
    nav_links = html.Nav([
        html.Button(className="navbar-toggler", type="button", **{
            'data-toggle': "collapse",
            'data-target': "#navbarToggler",
            'aria-controls': "navbarToggler",
            'aria-expanded': "false",
            'aria-label': "Toggle navigation"
        }, children=[
            html.Span(className="navbar-toggler-icon")
        ]),

        html.Div(className="collapse navbar-collapse", id="navbarToggler", children=[
            html.Div(
                dcc.Link(f"{page['title']}", href=page["relative_path"], className="nav-item nav-link nav-button"),
            ) for page in dash.page_registry.values()
        ])
    ], className="navbar navbar-expand-lg navbar-light bg-light")
    return nav_links


def build_page_registry():
    links = html.Div([
        html.Div([
            html.H4(
                dcc.Link(f"{page['name']}", href=page['relative_path']),
            ),
            html.P(page['description']),
        ], className="link-item") for page in dash.page_registry.values() if page['name'] != 'Home'
    ], className="homepage-links")
    return links

