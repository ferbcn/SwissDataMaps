import os.path
import time

import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input
import geopandas as gpd
import plotly.graph_objects as go

from data_loader import get_live_ev_station_data, load_transform_ev_station_data

dash.register_page(
    __name__,
    name='EV Chargers Swiss',
    title='EV Charging Stations Network Status',
    description='EV charging stations in Switzerland with real time availability and status data.',
    path='/ev',
    image_url='assets/ev.png'
)
# Load Station data from JSON file
print("Loading EV Stations data...")
ev_gdf = gpd.read_file("static/ev_gdf.json")

DDOWN_OPTIONS = ["All", "Available", "Occupied", "OutOfService", "Unknown"]

layout = html.Div([
    html.H3(children='Swiss EV Charger Network - Real Time Data'),
    html.Div([
        dcc.Dropdown(DDOWN_OPTIONS, 'All', className='ddown', id='ddown-type'),
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
    Input('ddown-type', 'value'),
)
def update_graph(selected_layer=None):

    colors = {"Available": "green", "Occupied": "orange", "OutOfService": "red", "Unknown": "gray"}
    # if cached file is older than 24h or does not exist, load fresh data
    if os.path.exists("static/ev_gdf.json") and time.time() > os.path.getctime("static/ev_gdf.json") + 60*60*24:
        print("Loading fresh EV static data...")
        df = load_transform_ev_station_data()
    else:
        print("Using cached EV static data from file...")
        # load pandas df from dictionary
        df = pd.DataFrame(ev_gdf)

    print("Loading live EV station data...")
    live_df = get_live_ev_station_data()
    # Inner Join the live data with the existing data (key = EvseID)
    print("Merging live data with existing data...")
    df = pd.merge(df, live_df, on='EvseID', how='inner')
    df['EVSEStatusColor'] = df['EVSEStatus'].map(colors)

    # remove rows where EVSEStatus is not "Available"
    if selected_layer in DDOWN_OPTIONS and selected_layer != "All":
        df = df[df['EVSEStatus'] == selected_layer]

    count = len(df)
    graph_title = f"{count} EV chargers ({selected_layer.lower()})"

    fig = go.Figure(go.Scattermapbox(lat=df['lat'], lon=df['lon'], mode='markers',
                                        marker=dict(
                                            size=10,
                                            color=df['EVSEStatusColor'],
                                            opacity=0.7,
                                    ),
                                    customdata=list(
                                         zip(df["name"].tolist(), df["plugs"].tolist(), df['EVSEStatus'].tolist())),
                                    ))

    fig.update_traces(hovertemplate="GPS: %{lat}, %{lon} <br>Name: %{customdata[0]} <br>Plugs: %{customdata[1]}"
                                    "<br>Status: %{customdata[2]}<extra></extra>")

    fig.update_layout(mapbox_style="open-street-map",
                      title_text=graph_title,
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
                      mapbox=dict(center=dict(lat=46.8, lon=8.2), zoom=7)
                      )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
