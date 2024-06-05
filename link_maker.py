import dash
from dash import html, dcc


def build_page_registry():
    links = html.Div([
        html.Div([
            html.H4(
                dcc.Link(f"{page['title']}", href=page['relative_path']),
            ),
            html.P(page['description']),
        ], className="link-item") for page in dash.page_registry.values() if page['name'] != 'Home'
    ], className="homepage-links")
    return links
