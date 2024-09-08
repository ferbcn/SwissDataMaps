# Zürich Tourism API: https://www.zuerich.com/en/api/v2/data
import pandas as pd
import plotly.express as px
import dash
from dash import callback, Output, Input, dcc, html

from data_loader import ZueriData

dash.register_page(
    __name__,
    name='Zürich POIs API',
    title='Zürich Tourism Points of Interest',
    description='Points of Interest in Zürich retrieved from the Zürich Tourism API.',
    path="/zueri",
    image_url='https://f-web-cdn.fra1.cdn.digitaloceanspaces.com/zueri.png',
    order=10
)

# Get API endpoints will be used to populate dropdown menu
api_ids_names = ZueriData().get_endpoint_list()

layout = [
    html.H3(children='Zürich Tourism POIs'),
    dcc.Dropdown(api_ids_names, '101', className='ddown', id='dropdown-id'),
    dcc.Loading(
        id="loading",
        type="circle",
        children=dcc.Graph(id='graph-content-1', style={'height': '80vh', 'width': '100%'})
    ),
    html.Span(children=[
        html.Pre(children="Source: Open Data Zürich Tourism API v2"),
        html.Pre(children=" "),
        html.A(
            children='Docs',
            href='https://zt.zuerich.com/en/open-data/v2',
            target='_blank',  # This makes the link open in a new tab
        )
    ], className='source-data')
]


@callback(
    Output('graph-content-1', 'figure'),
    Input('dropdown-id', 'value'),
)
def update_graph(api_id=101):
    zueri_data = ZueriData()
    names = []
    lats = []
    longs = []
    infos = []

    data = zueri_data.get_api_data(api_id)
    print(f'Received {len(data)} items')

    for item in data:
        if item.get('geoCoordinates') is None:
            continue
        try:  # not all entries have a name
            names.append(item.get('name').get('de'))
            longs.append(item.get('geoCoordinates').get('longitude'))
            lats.append(item.get('geoCoordinates').get('latitude'))
            infos.append(item.get('address').get('url'))
        except KeyError:
            names.append("n/a")

    data_dict = dict(
        names=names,
        longs=longs,
        lats=lats,
        infos=infos
    )
    total_points = len(data_dict.get('names'))
    print(f'Displaying {total_points} items')
    # show plotly dash modal

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(data_dict)
    fig = px.density_mapbox(df, lat=lats, lon=longs, radius=10,
                            mapbox_style="open-street-map",
                            color_continuous_scale="spectral",
                            custom_data=['names', 'infos'],
                            center=dict(lat=47.37, lon=8.53), zoom=12,
                            )
    fig.update_traces(hovertemplate="Name: %{customdata[0]} <br><a href='%{customdata[1]}'>%{customdata[1]}</a> <br>Coordinates: %{lat}, %{lon}")
    fig.update_layout(title_text=f"{api_ids_names.get(str(api_id))}: {total_points} points", title_font={'size': 12, 'color': 'lightgray'})
    fig.update_layout(coloraxis_showscale=False,
                      autosize=True,
                      margin=dict(l=0, r=0, b=0, t=0),
                      paper_bgcolor='rgba(0,0,0,0.0)',
                      )

    return fig


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)
