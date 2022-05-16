import dash
import plotly.express as px

from dash import dcc, html, Input, Output
from data import *
# -----------------------------------------------------------------------------------------------------------------------
MAPBOX_ACCESS_TOKEN: str = open('mapbox_token').read()
MAPBOX_STYLE = 'mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr'

countries = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland',
             'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania',
             'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
             'Spain', 'Sweden', 'Switzerland', 'United Kingdom']

pollutants = ['All', 'CO', 'NH3', 'NMVOC', 'NOx', 'PM10', 'PM2.5', 'SOx', 'TSP']
# -----------------------------------------------------------------------------------------------------------------------

app = dash.Dash(__name__, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# This is for gunicorn
server = app.server
suppress_callback_exceptions = True

# Side panel

side_panel_layout = html.Div(
    id='panel-side',
    children=[
        html.P(id='country-dropdown-text', children=['Air Pollution', html.Br(), ' Dashboard']),
        html.Div(id='country-dropdown',
                 children=dcc.Dropdown(id='dropdown-component', options=countries, clearable=False, value='France')),
        html.Br(),
        html.Div(id='city-dropdown',
                 children=dcc.Dropdown(
                     id='city-dropdown-component',
                     options=[],
                     clearable=False,
                     value='All')),
        html.Br(),
        html.Div(id='sector-dropdown',
                 children=dcc.Dropdown(
                     id='sector-dropdown-component',
                     options=[],
                     clearable=False,
                     value='All')),
        html.Br(),
        html.Div(id='panel-side-text', children=[
            html.H1(id='country-name', children=''),
            html.P(className='country-description', id='country-description', children=[''])
        ]),
    ],
)

# Histogram

histogram = html.Div(
    id='histogram-container',
    children=[
        html.Div(
            id='histogram-header',
            children=[
                html.H1(id='histogram-title', children=['Gothenburg Protocol, LRTAP Convention']),
                html.H1(
                    id='histogram-dropdown-sector',
                    children=[dcc.Dropdown(
                        id='dropdown-component-sector',
                        options=np.append('All', get_clrtap_df()['Sector_label_EEA'].unique()),
                        clearable=False,
                        value='All'
                    )]
                ),
                html.H1(
                    id='histogram-dropdown',
                    children=[dcc.Dropdown(
                        id='dropdown-component-second',
                        options=pollutants,
                        clearable=False,
                        value='All'
                    )]
                )
            ],
        ), dcc.Graph(id='histogram-graph', config={'displayModeBar': False}, animate=True),
    ],
)

# Map

map_graph = html.Div(
    id='world-map-wrapper',
    children=[
        dcc.Graph(id='world-map', config={'displayModeBar': False, 'scrollZoom': True}),
        dcc.Slider(id='year-slider',
        min=1,
        max=10,
        value=1,
        marks={k: '{}'.format(k) for k in range(1,11)})
    ]
)

@app.callback(Output('year-slider', 'min'),
              Output('year-slider', 'max'),
              Output('year-slider', 'value'),
              Output('year-slider', 'marks'),
              Input('dropdown-component', 'value')
              )
def show_year_slider(country):
    df = get_df(country)
    marks = {str(year): str(year) for year in df['Year'].unique()},
    return df['Year'].min(), df['Year'].max(), df['Year'].min(), marks

# Show mapbox related to the  ------------------------------------------------------------------------------------------

@app.callback(Output('world-map', 'figure'),
              Output('city-dropdown-component', 'options'),
              Output('sector-dropdown-component', 'options'),
              Input('dropdown-component', 'value'),
              Input('city-dropdown-component', 'value'),
              Input('sector-dropdown-component', 'value'),
              )
def show_initial_elements(country, city, sector):
    df = country_df_map(country, city, sector)
    figure = px.scatter_mapbox(df,
                               lat='Latitude', lon='Longitude', hover_name='Country',
                               hover_data=['eprtrSectorName', 'Emissions', 'EPRTRAnnexIMainActivityCode', 'City'],
                               color_discrete_sequence=['fuchsia'], zoom=4.5, height=650)
    figure.update_layout(mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                         mapbox_style=MAPBOX_STYLE,
                         margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                         autosize=True,
                         paper_bgcolor='#1e1e1e',
                         plot_bgcolor='#1e1e1e')

    city_options = np.append('All', df['City'].unique())
    sector_options = np.append('All', df['eprtrSectorName'].unique())

    print(sector_options)
    return figure, city_options, sector_options

# Show histogram related to the CLRTAP Dataset -------------------------------------------------------------------------

@app.callback(Output('histogram-graph', 'figure'),
              Input('dropdown-component', 'value'),
              Input('dropdown-component-second', 'value'),
              Input('dropdown-component-sector', 'value'))
def show_initial_elements(country, pollutant, sector):
    hist = px.bar(sector_emissions_per_country(country, pollutant, sector),
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
    id='panel-upper-lower',
    children=[
        map_graph,
        html.Div(
            id='panel',
            children=[
                histogram,
                html.Div(
                    id='panel-lower',
                    children=[
                        html.Div(
                            id='panel-lower-1',
                            children=[
                                html.Div(
                                    id='panel-lower-indicators',
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
    id='root',
    children=[
        dcc.Store(id='store-placeholder'),
        # For the case no components were clicked, we need to know what type of graph to preserve
        dcc.Store(id='store-data-config', data={'info_type': '', 'satellite_type': 0}),
        side_panel_layout,
        main_panel_layout,
    ],
)

app.layout = root_layout


@app.callback(
    Output('country-name', 'children'),
    [Input('dropdown-component', 'value')],
)
def update_name(val):
    if val == 'France':
        return 'France'
    else:
        return ''


@app.callback(
    Output('country-description', 'children'),
    [Input('dropdown-component', 'value')],
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
