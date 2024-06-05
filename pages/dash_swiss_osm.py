import json
import os
import time

import overpy
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    title='Open Street Maps POIs',
    name='Open Street Maps',
    description='Open Street Maps Points of Interest collected via the Overpass API using python overpy',
    path='/osm',
    order=20
)

tag_key_value_list = {"restaurant": "amenity", "bank": "amenity", "bar": "amenity", "fuel": "amenity",
                      "fast_food": "amenity", "atm": "amenity", "hospital": "amenity", "pharmacy": "amenity",
                      "library": "amenity", "books": "shop", "park": "leisure", "station": "public_transport",
                      "alcohol": "shop", "bakery": "shop", "bicycle": "shop", "post_office": "amenity"}
tag_keys = list(set(tag_key_value_list.values()))
tag_values = list(set(tag_key_value_list.keys()))

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


def get_data_overpy(country_iso_a2, tag_key, tag_value):
    names = []
    lats = []
    longs = []
    websites = []
    temp_dir = "temp"
    file_path = f'{temp_dir}/{tag_key}_{tag_value}.json'

    # if cached version exists and is not older than 24h, load from file
    if os.path.exists(file_path) and os.path.getctime(file_path) > time.time() - (60 * 60 * 24):
        print('Loading cached data...')
        with open(file_path, 'r') as f:
            data_dict = json.load(f)

    else:
        print('No cached data found, retrieving fresh API data...')
        api = overpy.Overpass()
        r = api.query("""
                ( area["ISO3166-1"="{0}"][admin_level=2]; )->.searchArea;
                ( node[{1}={2}]( area.searchArea );
                );
                out center;""".format(country_iso_a2, tag_key, tag_value))

        #print(f"Received {len(r.nodes)} nodes for {tag_value}")
        for node in r.nodes:
            try:  # not all entries have a name
                names.append(node.tags.get('name'))
            except KeyError:
                names.append("n/a")

            longs.append(float(node.lon))
            lats.append(float(node.lat))
            websites.append(node.tags.get('website'))

        data_dict = dict(
            names=names,
            longs=longs,
            lats=lats,
            websites=websites
        )

        with open(file_path, 'w') as f:
            json.dump(data_dict, f)

    return data_dict


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
