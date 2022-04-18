import plotly.express as px
from dash.dependencies import Input, Output

from data import *
from app import app

# Mapbox
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

suppress_callback_exceptions=True

@app.callback(Output('world-map', 'figure'),
              Input('dropdown-component', 'value'),
             )
def show_map(value):
    print('value:')
    print(value)
    fig = px.scatter_mapbox(country_df(value), lat="Latitude", lon="Longitude", hover_name="countryName", hover_data=["EPRTRSectorCode", "emissions"],
                            color_discrete_sequence=["fuchsia"], zoom=5, height=600)
    fig.update_layout(
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style=MAPBOX_STYLE,
        autosize=True,
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e"
    )
    return fig