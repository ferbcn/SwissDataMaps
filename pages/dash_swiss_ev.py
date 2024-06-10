import json
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc, callback, Output, Input
import geopandas as gpd
import plotly.graph_objects as go


dash.register_page(
    __name__,
    name='EV Charger Network',
    title='EV Charging Stations Network',
    description='EV Chargers Coverage in Switzerland.',
    path='/ev',
    image_url='assets/ev.png'
)
# Load Antenna data from JSON file
print("Loading EV Stations data...")
ev_gdf = gpd.read_file("static/ev_gdf.json")
count = len(ev_gdf)

ddown_options = ["-", "Kantone", "Bezirke", "Gemeinden"]

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"Kantone": "static/gdf_kan.json",
                    "Bezirke": "static/gdf_bez.json",
                    "Gemeinden": "static/gdf_gem.json"}

# TODO: maybe load all GDFs into memory in one go on startup

layout = html.Div([
    html.H3(children='EV Charger Network'),
    html.Div([
        dcc.Checklist(
            id='layer-toggle',
            options=[{'label': 'EV Chargers', 'value': '5G'}],
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
        children=dcc.Graph(id='graph-content-ev', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: IchTankeStrom"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://github.com/SFOE/ichtankestrom_Documentation',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
])

@callback(
    Output('graph-content-ev', 'figure'),
    Input('layer-toggle', 'value'),
    Input('dropdown-shape', 'value'),
)
def update_graph(selected_layers=None, shape_type=None):

    # Create a pandas DataFrame from the dictionary
    if '5G' in selected_layers:
        df = pd.DataFrame(ev_gdf)
    else:
        df = pd.DataFrame(ev_gdf)[0:0]

    fig = px.density_mapbox(df, lat=df.lat, lon=df.lon, radius=5,
                            mapbox_style="open-street-map", center=dict(lat=46.8, lon=8.2), zoom=7,
                            custom_data=[df["name"], df["plugs"]],
                            )
    fig.update_traces(hovertemplate="GPS: %{lat}, %{lon} <br>Name: %{customdata[0]} <br>Plugs: %{customdata[1]}<extra></extra>")
    fig.update_layout(title_text=f"{count} EV Stations", title_font={'size': 12, 'color': 'lightgray'})
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
                      font=dict(color='lightgray'),
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
                colorscale="blues",
                zmin=0,
                zmax=z_max,
                marker_opacity=0.5,
                marker_line_width=0,
                customdata=gdf['NAME'].values.reshape(-1, 1),
                hovertemplate='<b>%{customdata[0]}</b><br>%{z}<extra></extra>',
                visible= True if shape_type in ddown_options[1:] else False,
                showlegend = False  # Add this line,
            )
        )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
