import os
import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from link_maker import build_page_registry, build_nav_links

external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
    'assets/style.css'
]

external_scripts = [
    'https://code.jquery.com/jquery-3.3.1.slim.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js'
]

TEMP_DIR = 'temp'

# On startup
# Check if the temp directory exists
if os.path.exists(TEMP_DIR):
    print('Temp directory present')
else:
    print('Creating temp directory')
    os.makedirs(TEMP_DIR)

app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets, external_scripts=external_scripts)

# This callback is a workaround in order to correctly collect and display all nav links inside the home page
# which cant be done from inside a page as the page_registry may not be complete at page creation time
# https://community.plotly.com/t/create-a-list-in-the-offcanvas-which-can-connect-to-the-other-page/69632
@app.callback(
    Output('my-div', 'style'),
    Input('url', 'pathname')
)
def show_hide_div(pathname):
    if pathname == "/":
        return {'display': 'block'}
    else:
        return {'display': 'none'}


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # used to track the current location and show home page links

    build_nav_links(),

    html.Div([
        html.Div(dash.page_container, className='container-main'),
        html.Div(id='my-div', children=build_page_registry()),  # This div is used to show all links in the home page
    ], className='container-outer'),


    html.Div(
        children='Copyright © 2024 Swiss Geo Data Maps. All rights reserved.',
        className='copyrightfooter'
    ),
    html.A(
        children='Developed by: ferbcn',
        href='https://github.com/ferbcn',
        target='_blank',  # This makes the link open in a new tab
        className='pagefooter'
    ),
])

# if __name__ == '__main__':
#     app.run(debug=True)