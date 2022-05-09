import dash
import dash_daq as daq
from dash import Dash, dcc, html, callback, Input, Output
from data import *

import plotly.express as px
import warnings

warnings.filterwarnings('ignore')
#-----------------------------------------------------------------------------------------------------------------------
MAPBOX_ACCESS_TOKEN: str = open('mapbox_token').read()
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr"

countries = ['Finland' 'France' 'Ireland' 'Portugal' 'Bulgaria' 'Croatia' 'Estonia' 'Latvia' 'Malta' 'Slovenia' 
             'Norway' 'Denmark' 'Germany' 'Greece' 'Sweden' 'Cyprus' 'Lithuania' 'Poland' 'Romania' 'EU28' 'Iceland'
             'Austria' 'Italy' 'United Kingdom' 'Belgium' 'Netherlands' 'Spain' 'Czech Republic' 'Slovakia' 'Hungary'
             'Turkey' 'EEA33' 'Switzerland' 'Luxembourg' 'Liechtenstein']
#-----------------------------------------------------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# This is for gunicorn
server = app.server
suppress_callback_exceptions = True

# Dash_DAQ elements

utc = html.Div(
    id="control-panel-utc",
    children=[
        daq.LEDDisplay(
            id="control-panel-utc-component",
            value="16:23",
            label="Time",
            size=40,
            color="#fec036",
            backgroundColor="#2b2b2b",
        )
    ],
    n_clicks=0,
)

map_toggle = daq.ToggleSwitch(
    id="control-panel-toggle-map",
    value=True,
    label=["Hide path", "Show path"],
    color="#ffe102",
    style={"color": "#black"},
)

# Side panel
# Mapbox

satellite_dropdown = dcc.Dropdown(
    id="dropdown-component",
    options=countries,
    clearable=False,
    value="France",
)

satellite_dropdown_text = html.P(
    id="satellite-dropdown-text", children=['Air Pollution', html.Br(), ' Dashboard']
)

satellite_title = html.H1(id="satellite-name", children="")

satellite_body = html.P(
    className="satellite-description", id="satellite-description", children=[""]
)

side_panel_layout = html.Div(
    id="panel-side",
    children=[
        satellite_dropdown_text,
        html.Div(id="satellite-dropdown", children=satellite_dropdown),
        html.Div(id="panel-side-text", children=[satellite_title, satellite_body]),
    ],
)


map_graph2 = html.Div(
    id="world-map-wrapper",
    children=[
        dcc.Graph(
            id="world-map",
            config={"displayModeBar": False, "scrollZoom": True},
        ),
    ],
)

# Histogram

histogram = html.Div(
    id='histogram-container',
    children=[
        html.Div(
            id='histogram-header',
            children=[
                html.H1(
                    id='histogram-title',
                    children=['Gothenburg Protocol, LRTAP Convention']
                ),
                html.H1(id='histogram-dropdown-sector',
                        children=[dcc.Dropdown(id='dropdown-component-sector',
                                               options=np.append('All', get_clrtap_df()['Sector_label_EEA'].unique()),
                                               clearable=False,
                                               value='All')]
                        ),
                html.H1(
                    id='histogram-dropdown',
                    children=[dcc.Dropdown(id='dropdown-component-second',
                                           options=get_polluants(),
                                           clearable=False,
                                           value='All')]
                )
            ],
        ),
        dcc.Graph(
            id='histogram-graph',
            config={'displayModeBar': False},
            animate=True
        ),
    ],
)


# Show mapbox & histogram related to the CLRTAP Dataset ----------------------------------------------------------------

@app.callback(Output('world-map', 'figure'),
              Input('dropdown-component', 'value'))
def show_initial_elements(country):
    df = country_df_map(country)
    print(df['reportingYear'].unique())
    print(df['pollutant'].unique())

    print(df['countryName'].unique())

    figure = px.scatter_mapbox(df,
                               lat='Latitude', lon='Longitude', hover_name='countryName',
                               hover_data=['EPRTRSectorCode', 'emissions'],
                               color_discrete_sequence=['fuchsia'], zoom=4.5, height=650)
    figure.update_layout(mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                         mapbox_style=MAPBOX_STYLE,
                         margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                         autosize=True,
                         paper_bgcolor='#1e1e1e',
                         plot_bgcolor='#1e1e1e')
    return figure


@app.callback(Output('histogram-graph', 'figure'),
              Input('dropdown-component', 'value'),
              Input('dropdown-component-second', 'value'),
              Input('dropdown-component-sector', 'value'))
def show_initial_elements(country, pollutant, sector):
    df = sector_emissions_per_country(country, pollutant, sector)
    hist = px.bar(df,
                  x='Year', y='Emissions', color='Sector_label_EEA', barmode='overlay',
                  hover_data=['Sector_name'],
                  height=750, color_discrete_sequence=px.colors.qualitative.Vivid)
    hist.update_layout(margin={'t': 30, 'r': 35, 'b': 40, 'l': 50},
                       legend=dict(title=None, orientation='v', y=0.7, yanchor='bottom', x=1, xanchor='right'),
                       font=dict(color='gray'),
                       paper_bgcolor='#2b2b2b',
                       plot_bgcolor='#2b2b2b',
                       autosize=True,
                       bargap=0.1,
                       xaxis={'dtick': 5, 'gridcolor': '#636363', 'showline': False},
                       yaxis={'showgrid': False},
                       height=650)
    return hist


# ----------------------------------------------------------------------------------------------------------------------

# Control panel + map
main_panel_layout = html.Div(
    id="panel-upper-lower",
    children=[
        dcc.Interval(id="interval", interval=1 * 2000, n_intervals=0),
        map_graph2,
        html.Div(
            id="panel",
            children=[
                histogram,
                html.Div(
                    id="panel-lower",
                    children=[
                        html.Div(
                            id="panel-lower-1",
                            children=[
                                html.Div(
                                    id="panel-lower-indicators",
                                    children=[
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# Root
root_layout = html.Div(
    id="root",
    children=[
        dcc.Store(id="store-placeholder"),
        # For the case no components were clicked, we need to know what type of graph to preserve
        dcc.Store(id="store-data-config", data={"info_type": "", "satellite_type": 0}),
        side_panel_layout,
        main_panel_layout,
    ],
)

app.layout = root_layout


@app.callback(
    Output("satellite-name", "children"),
    [Input("dropdown-component", "value")],
)
def update_name(val):
    if val == "France":
        return "France"
    else:
        return ""


@app.callback(
    Output("satellite-description", "children"),
    [Input("dropdown-component", "value")],
)
def update_description(val):
    text = "Select a satellite to view using the dropdown above."

    if val == "France":
        text = (
            "Revolution tam tam tam."
        )

    elif val == "Germany":
        text = (
            "ich liebe dih; und nine"
        )
    return text


if __name__ == "__main__":
    app.run_server(debug=True)
