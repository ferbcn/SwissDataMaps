import json
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input
import geopandas as gpd
import plotly.graph_objects as go


dash.register_page(
    __name__,
    name='Swiss 5G Coverage',
    title='5G-Network Coverage',
    description='Points of 5G Antenna Coverage in Switzerland.',
    path='/antenna',
    image_url='assets/antenna.png'
)

# Load Antenna data from JSON file
print("Loading Antenna data...")
ant_gdf = gpd.read_file("static/ant_gdf.json")
count = len(ant_gdf)

ddown_options = ["-", "Kantone", "Bezirke", "Gemeinden"]

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"Kantone": "static/gdf_kan.json",
                    "Bezirke": "static/gdf_bez.json",
                    "Gemeinden": "static/gdf_gem.json"}

# TODO: maybe load all GDFs into memory in one go on startup


layout = html.Div([
    html.H3(children='5G Network Coverage'),
    html.Div([
        dcc.Checklist(
            id='layer-toggle',
            options=[{'label': '5G Antennas', 'value': '5G'}],
            value=['5G'],
            className='layer-toggle',
        ),
        html.Div([
            "Pop. density:",
            dcc.Dropdown(ddown_options, '-', className='ddown', id='dropdown-shape')
        ], className='ddmenu'),
    ], className="ddmenu"),

    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-ant', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Bakom"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='http://data.geo.admin.ch/ch.bakom.mobil-antennenstandorte-5g/data/ch.bakom.mobil-antennenstandorte-5g_de.json',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
])

@callback(
    Output('graph-content-ant', 'figure'),
    Input('layer-toggle', 'value'),
    Input('dropdown-shape', 'value'),
)
def update_graph(selected_layers=None, shape_type=None):

    # Create a pandas DataFrame from the dictionary
    if '5G' in selected_layers:
        df = pd.DataFrame(ant_gdf)
    else:
        df = pd.DataFrame(ant_gdf)[0:0]

    fig = px.density_mapbox(df, lat=df.lat, lon=df.lon, radius=df.power_int,
                            mapbox_style="open-street-map", center=dict(lat=46.8, lon=8.2), zoom=7,
                            )
    #fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{count} antennas", title_font={'size': 12, 'color': 'lightgray'})
    fig.update_layout(coloraxis_showscale=False,
                      autosize=True,
                      margin=dict(
                          l=20,  # left margin
                          r=20,  # right margin
                          b=10,  # bottom margin
                          t=40,  # top margin
                          pad=10  # padding
                          ),
                      paper_bgcolor='rgba(0,0,0,0)',
                      )

    # Draw map with shape data
    if shape_type in ddown_options[1:]:
        filepath = shape_files_dict.get(shape_type)
        print("Loading Shape data...")
        gdf = gpd.read_file(filepath)
        print("Converting to GeoJSON...")
        geojson_data = json.loads(gdf.to_json())
        z_max = 10000

        fig.add_trace(
            go.Choroplethmapbox(
                geojson=geojson_data,
                locations=gdf.index,  # or replace with the column containing the feature identifiers
                z=gdf['DICHTE'],  # or replace with the column containing the values to color-code
                colorscale="reds",
                zmin=0,
                zmax=z_max,
                marker_opacity=0.5,
                marker_line_width=0,
                customdata=gdf['NAME'].values.reshape(-1, 1),
                hovertemplate='<b>%{customdata[0]}</b><br>%{z}<extra></extra>',
                visible= True if shape_type in ddown_options[1:] else False
            )
        )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
