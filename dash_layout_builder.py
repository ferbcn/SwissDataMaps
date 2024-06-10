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
                dcc.Link(f"{page['name']}", href=page["relative_path"], className="nav-item nav-link nav-button"),
            ) for page in dash.page_registry.values()
        ])
    ], className="navbar navbar-expand-lg navbar-dark bg-dark")
    return nav_links


def build_page_registry():
    links = html.Div([
        dcc.Link(
            html.Div([
                html.H4(f"{page['title']}"),
                html.Div([
                    html.Img(src=page['image_url'], className='link-item-img'),
                    html.P(page['description']),
                ], className='link-item-img-text'),
            ], className="link-item"),
            href=page['relative_path']
        ) for page in dash.page_registry.values() if page['name'] != 'Home'
    ], className="homepage-links"),
    return links

