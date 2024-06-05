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
    title='Swiss 5G-Network Coverage',
    description='Points of 5G Antenna Coverage in Switzerland',
    path='/antenna',
)

layout = html.Div([
    html.H3(children='5G Antenna Coverage'),
    # dcc.Dropdown(["5G-Coverage"], '5G-Coverage', className='ddown', id='dropdown-ant'),
    dcc.Checklist(
        id='layer-toggle',
        options=[{'label': 'Population Density', 'value': 'Pop'}, {'label': '5G Antennas', 'value': '5G'}],
        value=['5G'],
        className='layer-toggle'
    ),
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


# Set the file path to the shapefile
# shapefile = "static/Gemeinden.shp"
shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp"

# load Shape file into GeoDataFrame
gdf = gpd.GeoDataFrame.from_file(shapefile)

# Convert to WGS84
gdf.crs = "EPSG:2056"  # Use CH1903+ / LV95 (epsg:2056)
# Use WGS84 (epsg:4326) as the geographic coordinate system
gdf = gdf.to_crs(epsg=4326)

# Convert the GeoDataFrame to GeoJSON
geojson_data = json.loads(gdf.to_json())
print("GeoJSON data loaded")

# Prepare antenna data
filepath = 'static/antennenstandorte-5g_de.json'
ant_gdf = gpd.read_file(filepath)

# Use WGS 84 (epsg:4326) as the geographic coordinate system
ant_gdf = ant_gdf.to_crs(epsg=4326)

# Convert powercode_de to integer value
# dictionary to convert antenna power data
powercodes = {"Sehr Klein": 2, "Klein": 3, "Mittel": 5, "Gross": 10}
# convert powercode_de to integer value
ant_gdf["power_int"] = ant_gdf["powercode_de"].apply(lambda x: powercodes.get(x))

# create lat and lon columns in ant_gdf
ant_gdf['lat'] = ant_gdf.geometry.y
ant_gdf['lon'] = ant_gdf.geometry.x

gdf['DICHTE'] = gdf['EINWOHNERZ'] / gdf['KANTONSFLA']

count = len(ant_gdf)
z_max = 10


@callback(
    Output('graph-content-ant', 'figure'),
    Input('layer-toggle', 'value'),
)
def update_graph(selected_layers=None):

    # Create a pandas DataFrame from the dictionary
    if '5G' in selected_layers:
        df = pd.DataFrame(ant_gdf)
    else:
        df = pd.DataFrame(ant_gdf)[0:0]

    fig = px.density_mapbox(df, lat=df.lat, lon=df.lon, radius=df.power_int,
                            mapbox_style="open-street-map", center=dict(lat=46.8, lon=8.2), zoom=7,
                            )

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
            visible= True if 'Pop' in selected_layers else False
        )
    )

    #fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{count} antennas", title_font={'size': 12})
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
