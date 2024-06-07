import plotly.graph_objects as go
import dash
from dash import callback, Output, Input, dcc, html
import geopandas as gpd
import numpy as np
from scipy.interpolate import griddata

dash.register_page(
    __name__,
    name='Swiss 3D Topographic Map',
    title='3D Switzerland',
    description='3D Topographic surface representation of Switzerland.',
    path="/map3d",
    image_url='assets/map3d.png'
)

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"Kantone": ["static/gdf_kan.json", "KANTONSFLA", [1000000, 5000, 10000]],
                    "Bezirke": ["static/gdf_bez.json", "BEZIRSKFLA", [100000, 500, 10000]],
                    "Gemeinden": ["static/gdf_gem.json","GEMEINDEFLA", [100000, 200, 10000]]}

ddown_options = list(shape_files_dict.keys())
ddown_methods = ["linear", "cubic", "nearest"]

layout = [
    html.H3(children='Swiss 3D-Map'),
    html.Div([
        dcc.Dropdown(ddown_options, 'Kantone', className='ddown', id='dropdown-shape'),
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
    Input('dropdown-shape', 'value'),
    Input('dropdown-method', 'value'),
)
def update_graph(shape_type="Kantone", method="cubic"):
    filepath = shape_files_dict.get(shape_type)[0]
    print("Loading Shape data...")
    gdf = gpd.read_file(filepath)

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

