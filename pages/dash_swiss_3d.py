import plotly.graph_objects as go
import dash
from dash import callback, Output, Input, dcc, html
import geopandas as gpd
import numpy as np
from scipy.interpolate import griddata

from dash_modal_long_wait import modal, toggle_modal

dash.register_page(
    __name__,
    name='Topographic Map',
    title='Swiss 3D Topographic Map',
    description='3D Topographic surface representation of Switzerland.',
    path="/map3d",
    image_url='https://f-web-cdn.fra1.cdn.digitaloceanspaces.com/map3d.png'
)

ddown_methods = ["linear", "cubic", "nearest"]

# Preload shape data
filepath = "static/gdf_kan.json"
print("Loading Shape data...")
gdf = gpd.read_file(filepath)

layout = [
    modal,
    html.H3(children='Swiss Topographic Map'),
    html.Div([
        dcc.Dropdown(ddown_methods, "linear", className='ddown', id='dropdown-method')
    ], className="ddmenu"),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-5', style={'height': '80vh', 'width': '100%'})
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
    Output('graph-content-5', 'figure'),
    Input('dropdown-method', 'value'),
)
def update_graph(method="cubic"):

    print("Drawing Map...")
    # iterate over geopandas dataframe gdf and extract all x,y, z values
    x, y, z = [], [], []
    for geom in gdf.geometry:
        if geom.geom_type == 'Polygon':
            polygon = geom.exterior.coords
            for coord in polygon:
                x.append(coord[0])
                y.append(coord[1])
                z.append(coord[2])
        if geom.geom_type == 'MultiPolygon':
            for poly_coll in geom.geoms:
                polygon = poly_coll.exterior.coords
                for coord in polygon:
                    x.append(coord[0])
                    y.append(coord[1])
                    z.append(coord[2])

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.linspace(y.min(), y.max(), 100)
    X, Y = np.meshgrid(xi, yi)

    Z = griddata((x, y), z, (X, Y), method=method)

    fig = go.Figure(go.Surface(x=xi, y=yi, z=Z))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                      highlightcolor="limegreen", project_z=True))
    fig.update_layout(scene=dict(aspectratio=dict(x=1.2, y=1.2, z=1),
                                 aspectmode='manual',
                                xaxis_title='Longitude',
                                yaxis_title='Latitude',
                                zaxis_title='Altitude'),
                      margin=dict(l=0, r=0, b=0, t=0),
                      autosize=True,
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='lightgray'),
                      )

    return fig

