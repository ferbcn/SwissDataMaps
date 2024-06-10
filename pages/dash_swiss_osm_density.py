import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html, dcc, callback, Output, Input
from geopandas import sjoin

from osm_overpy import get_data_overpy, get_tag_keys_values_options
import geopandas as gpd

dash.register_page(
    __name__,
    name='Open Street Density Maps',
    title='Open Street Maps Swiss Population Densities',
    description='Open Street Maps Points of Interest collected via the Overpass API using python overpy augmented with population data and density maps.',
    path='/density',
    image_url='assets/density.png'
)

tag_keys, tag_values, tag_key_value_list = get_tag_keys_values_options()

# Define the shape files (Kantone, Bezirke, Gemeinden), and their file paths (files have been pre-processed)
shape_files_dict = {"-": "",
                    "Kantone": "static/gdf_kan.json",
                    "Bezirke": "static/gdf_bez.json",
                    "Gemeinden": "static/gdf_gem.json",
                    }

ddown_options = list(shape_files_dict.keys())

layout = html.Div([
    html.H3(children='Open Street Maps and Swiss Population Densities'),
    html.Div([
        html.Div([
            "Fact:",
            dcc.Dropdown(tag_values, 'books', className='ddown', id='dropdown-value'),
        ], className='ddmenu'),
        html.Div([
            "Pop. by:",
            dcc.Dropdown(ddown_options, '-', className='ddown', id='dropdown-shape')
        ], className='ddmenu')
    ], className='ddmenu'),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-3', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Open Street Maps Overpass API"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://python-overpy.readthedocs.io/en/latest/',
            target='_blank'),
    ], className='source-data')
])


def count_points_in_polygon(poi_df, gdf):
    print("Counting POIs in each shape...")
    # Convert the DataFrame to a GeoDataFrame
    poi_gdf = gpd.GeoDataFrame(poi_df, geometry=gpd.points_from_xy(poi_df.longs, poi_df.lats))
    poi_gdf.crs = gdf.crs

    # Perform a spatial join operation
    joined_gdf = sjoin(poi_gdf, gdf, how='inner', predicate='within')

    # Count the number of points in each polygon
    counts = joined_gdf['index_right'].value_counts()

    # Update the 'COUNT' column in the original GeoDataFrame
    gdf['COUNT'] = counts
    gdf['COUNT'] = gdf['COUNT'].fillna(0)

    print("Calculating density...")
    gdf['OSM_DICHTE'] = gdf['COUNT'] / gdf['DICHTE'] * 1000
    z_max = gdf['OSM_DICHTE'].max()
    return gdf, z_max


@callback(
    Output('graph-content-3', 'figure'),
    Input('dropdown-value', 'value'),
    Input('dropdown-shape', 'value'),
)
def update_graph(tag_value="shop", shape_type=None, country_code="CH"):
    if tag_value not in tag_values:
        tag_value = 'books'
    tag_key = tag_key_value_list[tag_value]

    data_dict = get_data_overpy(country_code, tag_key, tag_value)

    total_points = len(data_dict["names"])
    print(f"Plotting nodes for {tag_value}: {total_points}")

    # Create a pandas DataFrame from the dictionary
    poi_df = pd.DataFrame(data_dict)

    fig = px.density_mapbox(poi_df, lat=data_dict["lats"], lon=data_dict["longs"], radius=5, zoom=7,
                            mapbox_style="open-street-map", color_continuous_scale="oxy",
                            custom_data=['names', 'websites'])
    # fig = px.scatter_mapbox(poi_df, lat=data_dict["lats"], lon=data_dict["longs"],
    #                         mapbox_style="open-street-map", color_continuous_scale="oxy",
    #                         custom_data=['names', 'websites'])

    fig.update_traces(
                    # marker=dict(
                    #     size=10,  # Sets the marker size
                    #     color='purple',  # Sets the marker color
                    #     opacity=0.8,  # Sets the marker opacity
                    # ),
                    hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}",
                    )
    fig.update_layout(title_text=f"{tag_value.capitalize()}: {total_points} points", title_font={'size': 12})
    fig.update_layout(coloraxis_showscale=False,
                      autosize=True,
                      margin=dict(
                          l=20,
                          r=20,
                          b=10,
                          t=40,
                          pad=10  # padding
                      ),
                      paper_bgcolor='rgba(0,0,0,0.0)',
                      font=dict(color='lightgray'),
                      )
    # Draw map with shape data
    if shape_type in ddown_options[1:]:
        # load the shape data
        filepath = shape_files_dict.get(shape_type)
        print("Loading Shape data...")
        gdf = gpd.read_file(filepath)
        print("Converting to GeoJSON...")
        geojson_data = json.loads(gdf.to_json())

        # Count the number of points in each polygon
        gdf, z_max = count_points_in_polygon(poi_df, gdf)

        print("Drawing Choroplethmapbox...")
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=geojson_data,
                locations=gdf.index,  # or replace with the column containing the feature identifiers
                z=gdf['OSM_DICHTE'],  # or replace with the column containing the values to color-code
                colorscale="reds",
                zmin=0,
                zmax=z_max,
                marker_opacity=0.5,
                marker_line_width=0,
                customdata=gdf['NAME'].values.reshape(-1, 1),
                hovertemplate='<b>%{customdata[0]}</b><br>%{z}<extra></extra>',
                visible=True if shape_type in ddown_options[1:] else False,
            )
        )

    return fig
