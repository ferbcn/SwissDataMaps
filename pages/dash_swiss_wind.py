import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input, dash_table
import geopandas as gpd
from shapely.geometry import Point

color_scales = ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
             'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
             'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
             'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
             'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
             'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
             'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
             'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
             'ylorrd']

dash.register_page(
    __name__,
    name='Wind Turbines',
    title='Swiss Wind Energy Turbines',
    description='Locations of Wind Turbines in Switzerland.',
    path='/wind',
    image_url='assets/wind.png'
)

print("Loading Turbine data...")
wind_gdf = gpd.read_file("static/wind-turb.csv")
# correct bad charecters in manufacturer column
wind_gdf['manufacturer'] = wind_gdf['manufacturer'].str.replace('Ã¼', 'ü')

layout = html.Div([
    html.H3(children='Swiss Wind Energy Turbines'),
    html.Div([
        html.Div([
            "Color-Scale: ",
            dcc.Dropdown(color_scales, value='cividis', id="color-input", className='ddown'),
        ], className='ddmenu'),
    ], className="ddmenu", style={'display': 'flex', 'justify-content': 'space-around'}),

    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-wind', style={'height': '70vh', 'width': '100%'})
    ),

    # Add a DataTable below the Graph
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in wind_gdf[["manufacturer", "model", "ratedPower", "diameter", "yearOfConstruction"]].columns],
            # select manufacturer and model columns
            data=wind_gdf[["manufacturer", "model", "ratedPower", "diameter", "yearOfConstruction"]].to_dict('records'),
            style_as_list_view=True,
            style_header={
                    'backgroundColor': 'lightgray',
                },
            style_table={
                'height': '10vh',
                'overflowY': 'auto',
                'overflowX': 'auto',
                'font-size': '1.2vh',
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
    ], className='ddmenu'),

    html.Span(children=[
        html.Pre(children="Source: SFOE"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://data.geo.admin.ch/browser/index.html#/collections/ch.bfe.windenergieanlagen?.language=en',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
])


@callback(
    Output('graph-content-wind', 'figure'),
    Input('color-input', 'value')
)
def update_graph(color_input):
    # Convert Swiss geodata to WGS84
    print("Loading Turbine data...")
    wind_gdf = gpd.read_file("static/wind-turb.csv")

    count = len(wind_gdf)
    # convert column y to epsg4326
    # Create a new geometry column from the 'x' and 'y' columns
    wind_gdf['geometry'] = [Point(xy) for xy in zip(wind_gdf.x, wind_gdf.y)]

    # Set the current CRS of the GeoDataFrame to EPSG:2056
    wind_gdf.set_crs("EPSG:2056", inplace=True)

    # Convert the GeoDataFrame to EPSG:4326
    wind_gdf = wind_gdf.to_crs("EPSG:4326")
    print(wind_gdf.shape)
    print(wind_gdf.columns)

    # convert column diameter to int
    wind_gdf['diameter'] = wind_gdf['diameter'].astype(int)
    # convert column ratedPower to int
    wind_gdf['ratedPower'] = wind_gdf['ratedPower'].astype(int)

    # correct bad charecters in manufacturer column
    wind_gdf['manufacturer'] = wind_gdf['manufacturer'].str.replace('Ã¼', 'ü')

    total_mW = f"{(wind_gdf['ratedPower'].sum() / 1000):.3f} mW"

    # yearOfConstruction  yearOfDismantling  manufacturer model diameter
    fig = px.scatter_mapbox(wind_gdf,
                            lat=wind_gdf.geometry.y, lon=wind_gdf.geometry.x,
                            size=wind_gdf.diameter*10, opacity=0.8,
                            color=wind_gdf.ratedPower, color_continuous_scale=color_input,
                            mapbox_style="open-street-map", center=dict(lat=46.8, lon=8.2), zoom=7,
                            custom_data=[
                                         wind_gdf["ratedPower"],
                                         wind_gdf["diameter"],
                                         wind_gdf["yearOfConstruction"],
                                         wind_gdf["model"],
                                         wind_gdf["manufacturer"],
                            ])
    # Create a pandas DataFrame from the dictionary
    fig.update_traces(hovertemplate="GPS: %{lat}, %{lon} "
                                    "<br>Manufacturer: %{customdata[4]}"
                                    "<br>Model: %{customdata[3]}"
                                    "<br>Power: %{customdata[0]}kW"
                                    "<br>Diameter: %{customdata[1]}"
                                    "<br>(*): %{customdata[2]}"
                                    "<extra></extra>"
                      )

    fig.update_layout(title_text=f"{count} wind turbines totaling {total_mW}",
                      legend_title_text='Power (kW)',
                      title_font={'size': 12, 'color': 'lightgray'},
                      autosize=True,
                      margin=dict(l=0, r=0, b=5, t=0),
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      )
    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
