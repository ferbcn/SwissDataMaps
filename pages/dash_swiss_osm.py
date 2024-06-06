import json
import os
import time

import overpy
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input

from osm_overpy import get_data_overpy, get_tag_keys_values_options

dash.register_page(
    __name__,
    name='Open Street Maps',
    title='Swiss Open Street Maps POIs',
    description='Open Street Maps Points of Interest collected via the Overpass API using python overpy.',
    path='/osm',
    image_url='assets/osm.png'
)

tag_keys, tag_values, tag_key_value_list = get_tag_keys_values_options()

layout = html.Div([
    html.H3(children='Open Street Maps POIs'),
    dcc.Dropdown(tag_values, 'books', className='ddown', id='dropdown-value'),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Open Street Maps Overpass API"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://python-overpy.readthedocs.io/en/latest/',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
])


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-value', 'value')
)
def update_graph(tag_value="shop"):
    if tag_value not in tag_values:
        tag_value = 'books'
    tag_key = tag_key_value_list[tag_value]

    data_dict = get_data_overpy('CH', tag_key, tag_value)

    total_points = len(data_dict["names"])
    print(f"Plotting nodes for {tag_value}: {total_points}")

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(data_dict)
    fig = px.density_mapbox(df, lat=data_dict["lats"], lon=data_dict["longs"], radius=10,
                            mapbox_style="open-street-map", color_continuous_scale="inferno",
                            custom_data=['names', 'websites'])
    fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{tag_value.capitalize()}: {total_points} points", title_font={'size': 12})
    fig.update_layout(coloraxis_showscale=False,
                      autosize=True,
                      margin=dict(
                          l=20,  # left margin
                          r=20,  # right margin
                          b=10,  # bottom margin
                          t=40,  # top margin
                          pad=10  # padding
                          ),
                      )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
