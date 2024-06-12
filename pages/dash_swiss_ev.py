import os.path
import time

import pandas as pd
import dash
from dash import html, dcc, callback, Output, Input, dash_table
import geopandas as gpd
import plotly.graph_objects as go

from data_loader import get_live_ev_station_data, load_transform_ev_station_data

dash.register_page(
    __name__,
    name='EV Chargers Swiss',
    title='EV Charging Stations Network Status',
    description='EV charging stations in Switzerland with real time availability and status data.',
    path='/ev',
    image_url='assets/ev.png',
    order=1
)
# Load Station data from JSON file
print("Loading EV Stations data...")
if os.path.exists("static/ev_gdf.json"):
    ev_gdf = gpd.read_file("static/ev_gdf.json")
else:
    print("EV Stations file not found.")


DDOWN_OPTIONS = ["All", "Available", "Occupied", "OutOfService", "Unknown"]

layout = html.Div([
    html.H3(children='Swiss EV Charger Network'),
    html.Div([
        html.Div([
            "Select: ", dcc.Dropdown(DDOWN_OPTIONS, 'All', className='ddown', id='ddown-type'),
        ], className='ddmenu'),
    ], className="ddmenu"),

    dcc.Loading(
        id="loading",
        type="circle",
        children=[
            dcc.Graph(id='graph-content-ev', style={'height': '65vh', 'width': '100%'}),

            # Custom Legend
            html.Div([

                html.Div([
                    html.Span(style={'background-color': 'green'}, className='legend-color'),
                    html.Span('Available', style={'margin-right': '15px'}),
                ], className='legend-item'),
                html.Div([
                    html.Span(style={'background-color': 'orange'}, className='legend-color'),
                    html.Span("Occupied"),
                ], className='legend-item'),
                html.Div([
                    html.Span(style={'background-color': 'red'}, className='legend-color'),
                    html.Span("OutOfService"),
                ], className='legend-item'),
                html.Div([
                    html.Span(style={'background-color': 'gray'}, className='legend-color'),
                    html.Span("Unknown"),
                ], className='legend-item'),
            ], className='legend-container'),

            # Data Table
            dash_table.DataTable(id='table',
                                style_as_list_view=True,
                                style_header={
                                        'backgroundColor': 'lightgray',
                                    },
                                style_table={
                                    'font-size': '1.2vh',
                                    'max-width': '50%',
                                    'margin-left': 'auto',
                                    'margin-right': 'auto',
                                },
                                style_cell={
                                    'textAlign': 'right',
                                    'color': 'gray',
                                },
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Status'},
                                        'textAlign': 'left',
                                    }],
                                 ),
        ]
    ),

    html.Span(children=[
        html.Pre(children="Source: IchTankeStrom"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://github.com/SFOE/ichtankestrom_Documentation',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data-ev'),

])

@callback(
    Output('graph-content-ev', 'figure'),
    Output('table', 'data'),
    Input('ddown-type', 'value'),
)
def update_graph(selected_layer=None):

    colors = {"Available": "green", "Occupied": "orange", "OutOfService": "red", "Unknown": "gray"}
    # if cached file is older than 24h or does not exist, load fresh data
    if os.path.exists("static/ev_gdf.json") and time.time() < os.path.getctime("static/ev_gdf.json") + 60*60*24:
        print("Using cached EV static data from file (not older than 24h) ...")
        df = pd.DataFrame(ev_gdf)
    else:
        print("Loading FRESH EV static data...")
        df = load_transform_ev_station_data()

    print("Loading live EV station data...")
    if os.path.exists("static/live_ev_df.json") and time.time() < os.path.getctime("static/live_ev_df.json") + 60*1*1:
        print("Using cached live EV data from file (not older than 1 min) ...")
        live_df = pd.read_json("static/live_ev_df.json", lines=True)
    else:
        print("Loading FRESH live EV data...")
        live_df = get_live_ev_station_data()

    # Inner Join the live data with the existing data (key = EvseID)
    print("Merging live data with existing data...")
    df = pd.merge(df, live_df, on='EvseID', how='inner')
    df['EVSEStatusColor'] = df['EVSEStatus'].map(colors)

    # Count dataset by all Statuses
    counts = [len(df[df['EVSEStatus'] == status]) for status in DDOWN_OPTIONS]

    # Filter by selected Status
    if selected_layer in DDOWN_OPTIONS and selected_layer != "All":
        df = df[df['EVSEStatus'] == selected_layer]

    # Generate Graph title
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
                          b=0,  # bottom margin
                          t=20,  # top margin
                          pad=10  # padding
                          ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      mapbox=dict(center=dict(lat=46.8, lon=8.2), zoom=7)
                      )
    # Add total to "All"
    counts[0] = sum(counts)
    # calculate percentages from counts
    percentages = [f"{round(c/counts[0]*100, 1)}" for c in counts]

    # Define the data table
    table_data = [{"Status": i, "Total": p, "%": w} for i, p, w in zip(DDOWN_OPTIONS, counts, percentages)]

    # Return the figure and the table data
    return fig, table_data


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
