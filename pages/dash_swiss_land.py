import json
import plotly.graph_objects as go
import dash
from dash import callback, dcc, Input, Output, html
import geopandas as gpd

dash.register_page(
    __name__,
    name='Swiss Landscape',
    title='Landschafts Typen Maps',
    description='Landschafts-Typen der Schweiz.',
    path="/land",
    image_url='assets/land.png',
    order=1
)


layout = [
    html.H3(children='Swiss Landscape Types'),
    dcc.Dropdown([], "", className='ddown', id='dropdown-land', style={'display': 'none'}),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-land', className="graph-content", style={'height': '80vh', 'width': '100%'})
    ),
]

@callback(
    Output('graph-content-land', 'figure'),
    Input('dropdown-land', 'value'),
)
def update_graph(pop):
    print("Loading Shape data...")
    filepath = "static/landschaft.gpkg"
    gdf = gpd.read_file(filepath)
    gdf.set_crs(epsg=2056, inplace=True)
    gdf = gdf.to_crs(epsg=4326)

    print("Columns: ", gdf.columns)
    print("Shape: ", gdf.shape)
    print(gdf.head())
    print(gdf.index)

    print("Converting to GeoJSON...")
    geojson_data = json.loads(gdf.to_json())    # Needed for Choroplethmapbox

    print("Drawing Map...")
    # Create a figure
    fig = go.Figure(go.Choroplethmapbox(geojson=geojson_data,
                                        locations=gdf.index,  # Use the DataFrame index as the location identifiers
                                        z=gdf["TYP_NR"],  # Use a column of ones for the z parameter
                                        showscale=False,  # Hide the color scale
                                        colorscale="earth",
                                        customdata=gdf[["OBJECT", "TYPNAME_DE", "REGNAME_DE"]],
                                        hovertemplate='<b>%{customdata[0]}</b> - %{customdata[1]}'
                                                      '<br>Region: %{customdata[2]}'
                                                      '<extra></extra>',
                                        visible=True
                                        ))

    token = "pk.eyJ1IjoiZmVyMmJjbiIsImEiOiJjbHhlYm45eDQwZmRuMmtxdHE2endtbDkyIn0.Rvlmi6NpKQ11HFsnh3BTlg"

    # # Set the mapbox style and center
    # fig.update_layout(
    #                   mapbox_accesstoken=token,
    #                   mapbox_style="satellite",
    #                   # mapbox_style="carto-positron",
    #                   mapbox_zoom=7,
    #                   mapbox_center={"lat": 47, "lon": 8.2},
    #                   autosize=True,
    #                   paper_bgcolor='rgba(0,0,0,0.0)',  # Set the background color of the map
    #                   # coloraxis_showscale=False,  # Hide the color scale
    #                   font=dict(color='lightgray'),
    #                   margin={"r": 0, "t": 0, "l": 0, "b": 0}
    #                   )

    # Add a button to the layout that toggles the visibility of the Choroplethmapbox
    fig.update_layout(
        mapbox_accesstoken=token,
        mapbox_style="satellite",
        # mapbox_style="carto-positron",
        mapbox_zoom=7,
        mapbox_center={"lat": 47, "lon": 8.2},
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0.0)',  # Set the background color of the map
        # coloraxis_showscale=False,  # Hide the color scale
        font=dict(color='lightgray'),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=list([
                    dict(
                        args=[{"visible": [True]}],
                        label="Show",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [False]}],
                        label="Hide",
                        method="update",
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )

    return fig

