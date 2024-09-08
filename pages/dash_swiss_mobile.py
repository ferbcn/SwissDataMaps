import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import callback, Output, Input, dcc, html

import geopandas as gpd

dash.register_page(
    __name__,
    name='Mobile Network',
    title='3G, 4G, 5G Network Antennas in Switzerland',
    description='Layered maps displaying the distribution of 3G, 4G and 5G antennas in Switzerland.',
    path="/mobile",
    image_url='https://f-web-cdn.fra1.cdn.digitaloceanspaces.com/mobile.png',
    order=150
)

layout = [
    html.H3(children='Mobile Network Antennas'),
    dcc.Dropdown([], "", className='ddown', id='dropdown-data', style={'display': 'none'}),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-data', className="graph-content", style={'height': '80vh', 'width': '100%'})
    ),
]

@callback(
    Output('graph-content-data', 'figure'),
    Input('dropdown-data', 'value'),
)
def update_graph(pop):

    # print("Loading Shape data...")
    gdf = gpd.read_file("static/mobilfunk.json")

    # count
    count = len(gdf)

    # filter by column techno_de containing "5G"
    print("Filtering by antenna technology...")
    gdf_5g = gdf[gdf["techno_de"].str.contains("5G")]
    gdf_4g = gdf[gdf["techno_de"].str.contains("4G")]
    gdf_3g = gdf[gdf["techno_de"].str.contains("3G")]

    # print("Generating Map...")
    # # Create a separate density_mapbox for each GeoDataFrame
    # density_3g = px.density_mapbox(gdf_3g, lat=gdf_3g.geometry.y, lon=gdf_3g.geometry.x, radius=gdf_3g.power_code,
    #                                custom_data=['typ_de', 'techno_de', 'power_de'],
    #                                color_continuous_scale="spectral",
    #                                )
    # density_4g = px.density_mapbox(gdf_4g, lat=gdf_4g.geometry.y, lon=gdf_4g.geometry.x, radius=gdf_4g.power_code,
    #                                custom_data=['typ_de', 'techno_de', 'power_de'],
    #                                )
    # density_5g = px.density_mapbox(gdf_5g, lat=gdf_5g.geometry.y, lon=gdf_5g.geometry.x, radius=gdf_5g.power_code,
    #                                custom_data=['typ_de', 'techno_de', 'power_de'],
    #                                )
    #
    # # Combine the figures into a single figure
    # fig = go.Figure(data=density_3g.data + density_4g.data + density_5g.data)

    print("Generating Map...")
    # Create a separate scatter_mapbox for each GeoDataFrame
    scatter_3g = go.Scattermapbox(
        lat=gdf_3g.geometry.y, lon=gdf_3g.geometry.x, mode='markers',
        marker={'size': gdf_3g.power_code, 'opacity': 0.7},
        customdata=gdf_3g[['typ_de', 'techno_de', 'power_de']].values,
        name='3G'
    )

    scatter_4g = go.Scattermapbox(
        lat=gdf_4g.geometry.y, lon=gdf_4g.geometry.x, mode='markers',
        marker={'size': gdf_4g.power_code, 'opacity': 0.7},
        customdata=gdf_4g[['typ_de', 'techno_de', 'power_de']].values,
        name='4G'
    )

    scatter_5g = go.Scattermapbox(
        lat=gdf_5g.geometry.y, lon=gdf_5g.geometry.x, mode='markers',
        marker={'size': gdf_5g.power_code, 'opacity': 0.7},
        customdata=gdf_5g[['typ_de', 'techno_de', 'power_de']].values,
        name='5G'
    )

    # Combine the figures into a single figure
    fig = go.Figure(data=[scatter_3g, scatter_4g, scatter_5g])
    fig.update_traces(hovertemplate=""
                                    "Techno: %{customdata[1]}"
                                    "<br>Power: %{customdata[2]}"
                                    "<br>Typ: %{customdata[0]}"
                                    "<br>GPS: %{lat}, %{lon}"
                      )

    # token = os.getenv("MAPBOX_TOKEN")
    # Add buttons to the layout to control the visibility of each trace
    fig.update_layout(
        mapbox_style="open-street-map",
        title_text=f"Total: {count} antennas",
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        mapbox_zoom=7,
        mapbox_center={"lat": 47, "lon": 8.2},
        font=dict(color='darkgray'),
        legend=dict(
            orientation="h",  # Horizontal orientation
            yanchor="bottom",
            y=1.02,  # Position legend slightly above the bottom
            xanchor="right",
            x=1  # Position legend to the right
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=list([
                    dict(
                        args=[{"visible": [True, False, False]}],
                        label="Show 3G",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [False, True, False]}],
                        label="Show 4G",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [False, False, True]}],
                        label="Show 5G",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [True, True, True]}],
                        label="Show All",
                        method="update",
                    )
                ]),
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.8,
                xanchor="right",
                y=1.1,
                yanchor="top",
            ),
        ]
    )
    print("Returning figure...")
    return fig
