import json
import plotly.graph_objects as go
import dash
from dash import callback, dcc, Input, Output, html
import geopandas as gpd
from dash_modal_long_wait import modal, toggle_modal

dash.register_page(
    __name__,
    name='Population Map',
    title='Swiss Regional Population Maps',
    description='Map of Switzerland with Population, Area and Density by Kanton, Bezirk and Gemeinde.',
    path="/swiss",
    image_url='assets/swiss.png',
    order=1
)

TEMP_DIR = 'temp'

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"Kantone": ["static/gdf_kan.json", "KANTONSFLA", [1000000, 5000, 10000]],
                    "Bezirke": ["static/gdf_bez.json", "BEZIRKSFLA", [100000, 500, 10000]],
                    "Gemeinden": ["static/gdf_gem.json","GEMEINDEFLA", [100000, 200, 10000]]}

ddown_options = list(shape_files_dict.keys())
DATA_OPTIONS = ["Population", "Area", "Density"]

filepath = "static/gdf_kan.json"
print("Loading Shape data for all shapes...")
gdf_kan = gpd.read_file("static/gdf_kan.json")
gdf_bez = gpd.read_file("static/gdf_bez.json")
gdf_gem = gpd.read_file("static/gdf_gem.json")

gdf_preload = {"Kantone":gdf_kan, "Bezirke":gdf_bez, "Gemeinden":gdf_gem}

layout = [
    modal,
    html.H3(children='Swiss Population'),
    html.Div([
        dcc.Dropdown(ddown_options, 'Kantone', className='ddown', id='dropdown-shape'),
        dcc.Dropdown(DATA_OPTIONS, "Population", className='ddown', id='dropdown-pop'),
    ], className="ddmenu"),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-2', className="graph-content", style={'height': '80vh', 'width': '100%'})
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

@callback(
    Output('graph-content-2', 'figure'),
    Input('dropdown-shape', 'value'),
    Input('dropdown-pop', 'value'),
)
def update_graph(shape_type="Kantone", api_id="Population"):
    print("Loading Shape data...")
    gdf = gdf_preload.get(shape_type)
    print("Converting to GeoJSON...")
    geojson_data = json.loads(gdf.to_json())    # Needed for Choroplethmapbox

    area_name = shape_files_dict.get(shape_type)[1]
    z_max_options = shape_files_dict.get(shape_type)[2]

    # api_id == 'Population'
    fact = gdf['EINWOHNERZ']
    z_max = z_max_options[0]
    if api_id == 'Area':
        fact = gdf[area_name] / 100  # to km^2
        z_max = z_max_options[1]
    if api_id == 'Density':
        fact = gdf['DICHTE']
        z_max = z_max_options[2]

    print("Drawing Map...")
    # Create a figure
    fig = go.Figure(go.Choroplethmapbox(geojson=geojson_data, locations=gdf.index, z=fact,
                                        colorscale="Viridis", zmin=0, zmax=z_max,
                                        marker_opacity=0.5, marker_line_width=0,
                                        customdata=gdf['NAME'].values.reshape(-1, 1),
                                        hovertemplate='<b>%{customdata[0]}</b><br>%{z}<extra></extra>',
                                        ))

    # Set the mapbox style and center
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=7,
                      mapbox_center={"lat": 47, "lon": 8.2},
                      autosize=True,
                      margin=dict(l=20, r=20, t=10, b=10),
                      paper_bgcolor='rgba(0,0,0,0.0)',  # Set the background color of the map
                      coloraxis_showscale=False,  # Hide the color scale
                      font=dict(color='lightgray'),
                      )

    return fig

