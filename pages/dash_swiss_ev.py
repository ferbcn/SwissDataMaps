import json
import time

import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input
import geopandas as gpd
import plotly.graph_objects as go

from data_loader import get_live_ev_station_data

dash.register_page(
    __name__,
    name='EV Charger Network',
    title='EV Charging Stations Network',
    description='EV Chargers Coverage in Switzerland.',
    path='/ev',
    image_url='assets/ev.png'
)
# Load Station data from JSON file
print("Loading EV Stations data...")
ev_gdf = gpd.read_file("static/ev_gdf.json")

layout = html.Div([
    html.H3(children='EV Charger Network'),
    html.Div([
        dcc.Checklist(
            id='layer-toggle',
            options=[{'label': 'Only Show Available', 'value': 'available'}],
            value=[''],
            className='layer-toggle',
        ),
    ], className="ddmenu"),

    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-ev', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: IchTankeStrom"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://github.com/SFOE/ichtankestrom_Documentation',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
])

@callback(
    Output('graph-content-ev', 'figure'),
    Input('layer-toggle', 'value'),
)
def update_graph(selected_layers=None):

    colors = {"Available": "green", "Occupied": "orange", "OutOfService": "red", "Unknown": "gray"}
    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(ev_gdf)
    live_df = get_live_ev_station_data()
    # Inner Join the live data with the existing data (key = EvseID)
    print("Merging live data with existing data...")
    df = pd.merge(df, live_df, on='EvseID', how='inner')
    df['EVSEStatusColor'] = df['EVSEStatus'].map(colors)

    # remove rows where EVSEStatus is not "Available"
    if 'available' in selected_layers:
        df = df[df['EVSEStatus'] == "Available"]

    count = len(df)

    fig = go.Figure(go.Scattermapbox(lat=df['lat'], lon=df['lon'], mode='markers',
                                     marker=dict(size=10, color=df['EVSEStatusColor'], opacity=0.7),
                                     customdata=list(
                                         zip(df["name"].tolist(), df["plugs"].tolist(), df['EVSEStatus'].tolist())),
                                     ))

    fig.update_traces(hovertemplate="GPS: %{lat}, %{lon} <br>Name: %{customdata[0]} <br>Plugs: %{customdata[1]}"
                                    "<br>Status: %{customdata[2]}<extra></extra>")

    fig.update_layout(mapbox_style="open-street-map",
                      title_text=f"{count} EV Stations",
                      title_font={'size': 12, 'color': 'lightgray'},
                      autosize=True,
                      margin=dict(
                          l=20,  # left margin
                          r=20,  # right margin
                          b=10,  # bottom margin
                          t=40,  # top margin
                          pad=10  # padding
                          ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      mapbox=dict(center=dict(lat=46.8, lon=8.2), zoom=7),
                      )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
