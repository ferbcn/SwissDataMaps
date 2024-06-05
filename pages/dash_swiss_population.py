import json
import plotly.graph_objects as go
import dash
from dash import callback, Output, Input, dcc, html

import geopandas as gpd

from string_decode import decode_string

dash.register_page(
    __name__,
    title='Swiss Population',
    name='Swiss Population',
    description='Map of Switzerland with Population, Area and Density by Kanton.',
    path="/swiss",
)

TEMP_DIR = 'temp'
DATA_OPTIONS = ["Population", "Area", "Density"]

layout = [
    html.H3(children='Swiss Data'),
    html.Div([
        dcc.Dropdown(["Kantone", "Bezirke", "Gemeinden"], 'Kantone', className='ddown', id='dropdown-shape'),
        dcc.Dropdown(DATA_OPTIONS, "Population", className='ddown', id='dropdown-5g'),
    ], className="ddmenu"),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-2', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Open Data"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://opendata.swiss/',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
]

# Set the file path to the shapefile
shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp"

# load Shape file into GeoDataFrame
gdf = gpd.GeoDataFrame.from_file(shapefile)

# Convert Polygon Z to Polygon
# gdf['geometry'] = gdf['geometry'].apply(lambda p: Polygon([(x, y) for x, y, z in p.exterior.coords]))

# Convert to WGS84
gdf.crs = "EPSG:2056"  # Use CH1903+ / LV95 (epsg:2056)
# Use WGS84 (epsg:4326) as the geographic coordinate system
gdf = gdf.to_crs(epsg=4326)

# Convert the GeoDataFrame to GeoJSON
geojson_data = json.loads(gdf.to_json())
print("GeoJSON data loaded")

# Correct string encoding for the NAME column
gdf['NAME'] = gdf['NAME'].apply(decode_string)

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"Kantone": ["static/gdf_kan.json", "KANTONSFLA"],
                    "Bezirke": ["static/gdf_bez.json", "BEZIRSKFLA"],
                    "Gemeinden": ["static/gdf_gem.json","GEMEINDEFLA"]}

@callback(
    Output('graph-content-2', 'figure'),
    Input('dropdown-5g', 'value'),
    Input('dropdown-shape', 'value'),
)
def update_graph(api_id="Population", shape_type="Kantone"):

    filepath = shape_files_dict.get(shape_type)[0]
    print("Loading Shape data...")
    gdf = gpd.read_file(filepath)
    print("Converting to GeoJSON...")
    geojson_data = json.loads(gdf.to_json())

    area_name = shape_files_dict.get(shape_type)[1]

    fact = gdf['EINWOHNERZ']
    z_max = 1500000
    if api_id == 'Area':
        fact = gdf[area_name]
        z_max = 750000
    if api_id == 'Density':
        fact = gdf['DICHTE']
        z_max = 10000

    # Create a figure
    fig = go.Figure(go.Choroplethmapbox(geojson=geojson_data, locations=gdf.index, z=fact,
                                        colorscale="Viridis", zmin=0, zmax=z_max,
                                        marker_opacity=0.5, marker_line_width=0,
                                        customdata=gdf['NAME'].values.reshape(-1, 1),
                                        hovertemplate='<b>%{customdata[0]}</b><br>%{z}<extra></extra>'
                                        ))

    # Set the mapbox style and center
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=7,
                      mapbox_center={"lat": 47, "lon": 8.2},
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

