from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc

modal = html.Div(
    [
        dbc.Button("Open modal", id="open", n_clicks=0, style={'display': 'none'}),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Long processing time"), style={'color': 'black'}),
                dbc.ModalBody("Hang on, larger datasets take more time to process and render...", style={'color': 'black'}),
                dbc.ModalFooter(
                    dbc.Button(
                        "Ok", id="close", className="btn-secondary", n_clicks=0
                    )
                ),
            ],
            id="modal",
            centered=True,
            is_open=False,
        ),
    ]
)

@callback(
    Output("modal", "is_open"),
    [Input("dropdown-shape", "value"),
     Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(dropdown_shape, n2, is_open):
    if dropdown_shape or n2:
        if dropdown_shape in ['Kantone', "-"]:
            return
        return not is_open
    return is_open
