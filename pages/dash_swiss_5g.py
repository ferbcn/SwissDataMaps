import json
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input
import geopandas as gpd

dash.register_page(
    __name__,
    title='5G-Coverage',
    name='5G Antenna Coverage',
    description='Points of 5G Antenna Coverage in Switzerland',
    path='/antenna',
)

layout = html.Div([
    html.H3(children='5G Antenna Coverage'),
    dcc.Dropdown(["5G-Coverage"], '5G-Coverage', className='ddown', id='dropdown-ant'),
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


# Correct wrong string encoding, TODO: Check data source / import
def decode_string(s):
    if isinstance(s, str):
        return s.encode('latin1').decode('utf8')
    return s

# Set the file path to the shapefile
# shapefile = "static/Gemeinden.shp"
shapefile = "static/Grenzen.shp/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp"

# load Shape file into GeoDataFrame
gdf = gpd.GeoDataFrame.from_file(shapefile)

# Convert Polygon Z to Polygon
# gdf['geometry'] = gdf['geometry'].apply(lambda p: Polygon([(x, y) for x, y, z in p.exterior.coords]))

# Convert to WGS84
gdf.crs = "EPSG:2056"  # Use CH1903+ / LV95 (epsg:2056)
# Use WGS84 (epsg:4326) as the geographic coordinate system
gdf = gdf.to_crs(epsg=4326)
# print(gdf.head(5))
# print(gdf.columns)
# print(gdf['EINWOHNERZ'].nlargest(n=5))

# Convert the GeoDataFrame to GeoJSON
geojson_data = json.loads(gdf.to_json())
print("GeoJSON data loaded")

# Correct string encoding for the NAME column
gdf['NAME'] = gdf['NAME'].apply(decode_string)


@callback(
    Output('graph-content-ant', 'figure'),
    Input('dropdown-ant', 'value')
)
def update_graph(param="5G-Coverage"):

    filepath = 'static/antennenstandorte-5g_de.json'
    ant_gdf = gpd.read_file(filepath)
    # print(ant_gdf.columns)

    # Use WGS 84 (epsg:4326) as the geographic coordinate system
    ant_gdf = ant_gdf.to_crs(epsg=4326)

    # Convert powercode_de to integer value
    # dictionary to convert antenna power data
    powercodes = {"Sehr Klein": 2, "Klein": 3, "Mittel": 5, "Gross": 10}
    # convert powercode_de to integer value
    ant_gdf["power_int"] = ant_gdf["powercode_de"].apply(lambda x: powercodes.get(x))

    # creat lat and lon columns in ant_gdf
    ant_gdf['lat'] = ant_gdf.geometry.y
    ant_gdf['lon'] = ant_gdf.geometry.x

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(ant_gdf)
    fig = px.density_mapbox(df, lat=df.lat, lon=df.lon, radius=df.power_int,
                            mapbox_style="open-street-map")

    #fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{len(df)} antennas", title_font={'size': 12})
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
