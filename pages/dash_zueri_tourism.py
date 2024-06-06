# Zürich Tourism API: https://www.zuerich.com/en/api/v2/data
import os
import json
import time

import pandas as pd
import plotly.express as px
import requests
import dash
from dash import callback, Output, Input, dcc, html

dash.register_page(
    __name__,
    name='Zürich POIs',
    title='Zürich Tourism POIs',
    description='Points of Interest in Zürich retrieved from the Zürich Tourism API.',
    path="/zueri",
    image_url='assets/zueri.png',
    order=10
)

TEMP_DIR = 'temp'


class ZueriData:
    def __init__(self):
        self.end_url = "https://www.zuerich.com/en/api/v2/data"
        self.api_url = self.end_url + "?id="
        self.temp_dir = TEMP_DIR

    def get_endpoint_list(self):
        print('Retrieving Zürich Tourism API endpoints...')
        api_endpoints_raw = requests.get(self.end_url)
        api_ids_names = {item.get('id'): item.get('name').get('de') for item in api_endpoints_raw.json() if not item.get('name').get('de') is None}
        return api_ids_names

    def get_api_data(self, api_id=101):
        print(f'Checking for cached version of API endpoint with id {api_id}')
        # Check if the data is already cached and not older than 24h
        if os.path.exists(f'{self.temp_dir}/{api_id}.json') and os.path.getctime(f'{self.temp_dir}/{api_id}.json') > time.time() - (60 * 60 * 24):
            print('Loading cached data...')
            with open(f'{self.temp_dir}/{api_id}.json', 'r') as f:
                data = json.load(f)
            return data
        else:
            print('No cached data found, retrieving fresh API data...')
            response = requests.get(self.api_url + str(api_id))
            data = response.json()
            with open(f'{self.temp_dir}/{api_id}.json', 'w') as f:
                json.dump(data, f)
        return data


# Get API endpoints will be used to populate dropdown menu
api_ids_names = ZueriData().get_endpoint_list()

layout = [
    html.H3(children='Zürich Tourism POIs'),
    dcc.Dropdown(api_ids_names, '101', className='ddown', id='dropdown-id'),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-1', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Open Data Zürich Tourism API v2"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://zt.zuerich.com/en/open-data/v2',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
]


@callback(
    Output('graph-content-1', 'figure'),
    Input('dropdown-id', 'value'),
)
def update_graph(api_id=101):
    zueri_data = ZueriData()
    names = []
    lats = []
    longs = []
    infos = []

    data = zueri_data.get_api_data(api_id)
    print(f'Received {len(data)} items')

    for item in data:
        if item.get('geoCoordinates') is None:
            continue
        try:  # not all entries have a name
            names.append(item.get('name').get('de'))
            longs.append(item.get('geoCoordinates').get('longitude'))
            lats.append(item.get('geoCoordinates').get('latitude'))
            infos.append(item.get('address').get('url'))
        except KeyError:
            names.append("n/a")

    data_dict = dict(
        names=names,
        longs=longs,
        lats=lats,
        infos=infos
    )
    total_points = len(data_dict.get('names'))
    print(f'Displaying {total_points} items')

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(data_dict)
    fig = px.density_mapbox(df, lat=lats, lon=longs, radius=10,
                            mapbox_style="open-street-map", color_continuous_scale="spectral",
                            custom_data=['names', 'infos'],
                            center=dict(lat=47.37, lon=8.53), zoom=12
                            )
    fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{api_ids_names.get(str(api_id))}: {total_points} points", title_font={'size': 12})
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
