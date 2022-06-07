import dash
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, Input, Output
from data import *

import os
from dotenv import load_dotenv

load_dotenv()

MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')

# -----------------------------------------------------------------------------------------------------------------------
#MAPBOX_ACCESS_TOKEN: str = open('mapbox_token').read()
MAPBOX_STYLE = 'mapbox://styles/plotlymapbox/cjyivwt3i014a1dpejm5r7dwr'

countries = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland',
             'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania',
             'Luxembourg', 'Malta', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
             'Spain', 'Sweden', 'Switzerland', 'United Kingdom']

sectors = ['All', 'National total for the entire territory', 'Energy production and distribution',
           'Energy use in industry', 'Road transport', 'Non-road transport', 'Commercial, institutional and households',
           'Industrial processes and product use', 'Agriculture', 'Waste', 'Other']

pollutants = ['All', 'CO', 'NH3', 'NMVOC', 'NOx', 'PM10', 'PM2.5', 'SOx', 'TSP']
years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

models = ['Random Forest Regressor', 'Decision Tree Regressor', 'Linear Regression']
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
                 children=dcc.Dropdown(id='dropdown-component', options=countries, clearable=False, value='Germany')),
        html.Br(),
        html.Div(id='city-dropdown',
                 children=dcc.Dropdown(
                     id='city-dropdown-component',
                     options=[],
                     clearable=False,
                     value='Hamburg')),
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
                        options=sectors,
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
        ),
        dcc.Graph(id='histogram-graph', config={'displayModeBar': False}, animate=True),
    ],
)

# Map


map_graph = html.Div(
    id='world-map-wrapper',
    children=[dcc.Graph(id='world-map', config={'displayModeBar': False, 'scrollZoom': True})]
)
slider = html.H1(dcc.Slider(
    2007,
    2020,
    value=2007,
    step=None,
    marks={str(year): str(year) for year in years},
    id='year-slider'
))


@app.callback(Output('world-map', 'figure'),
              Output('city-dropdown-component', 'options'),
              Output('sector-dropdown-component', 'options'),
              Input('dropdown-component', 'value'),
              Input('city-dropdown-component', 'value'),
              Input('sector-dropdown-component', 'value'),
              Input('year-slider', 'value')
              )
def show_initial_elements(country, city, sector, year):
    df = country_df_map(country, city, sector)
    filtered_df = df[df.Year == year]

    figure = px.scatter_mapbox(filtered_df,
                               lat='Latitude', lon='Longitude', hover_name='Country',
                               hover_data=['eprtrSectorName', 'Emissions', 'EPRTRAnnexIMainActivityCode', 'City'],
                               color_discrete_sequence=['fuchsia'], zoom=5, height=655)

    figure.update_layout(mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
                         mapbox_style=MAPBOX_STYLE,
                         margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                         autosize=True,
                         paper_bgcolor='#1e1e1e',
                         plot_bgcolor='#1e1e1e')

    # figure = go.Figure(go.Scattermapbox(
    #     lat=df['Latitude'],
    #     lon=df['Longitude'],
    #     mode='markers',
    #     marker=go.scattermapbox.Marker(
    #         autocolorscale=False,
    #         showscale=True,
    #         size=filtered_df['Emissions'],
    #         opacity=0.8,
    #         color=filtered_df['Emissions'],
    #         colorscale='blues',
    #         colorbar=dict(
    #             title='',
    #             thickness=20,
    #             titleside='top',
    #             outlinecolor='rgba(68,68,68,0)',
    #             ticks='outside',
    #             ticklen=3)
    #     ),
    # ))
    #
    # figure.update_layout(
    #     autosize=True,
    #      height=655,
    #      plot_bgcolor='#1e1e1e',
    #     paper_bgcolor='#1e1e1e',
    #
    #      mapbox=dict(
    #         accesstoken=MAPBOX_ACCESS_TOKEN,
    #         style=MAPBOX_STYLE,
    #           zoom=5
    #     ),
    # )
    city_options = np.append('All', filtered_df['City'].unique())
    sector_options = np.append('All', filtered_df['eprtrSectorName'].unique())

    return figure, city_options, sector_options


#--------- predictions--------------------------------------------------------------------------------------------------


predictions = html.Div(
    id='predictions-container',
    children=[
        html.Div(
            id='predictions-header',
            children=[
                html.H1(id='predictions-title', children=['Predictions for Emissions']),
                html.H1(
                    id='predictions-dropdown-sector',
                    children=[dcc.Dropdown(
                        id='predictions-component-sector',
                        options=models,
                        clearable=False,
                        value='Decision Tree Regressor'
                    )]
                ),
                html.H1(
                    id='predictions-dropdown',
                    children=[dcc.Dropdown(
                        id='predictions-component-second',
                        options=pollutants,
                        clearable=False,
                        value='All'
                    )]
                )
            ],
        ),
        dcc.Graph(id='predictions-graph', config={'displayModeBar': False}, animate=True),
    ],
)


#--------- predictions--------------------------------------------------------------------------------------------------


predictions2 = html.Div(
    id='predictions-container2',
    children=[
        html.Div(
            id='predictions-header2',
            children=[
                html.H1(id='predictions-title2', children=['Predictions for Emissions']),
                html.H1(
                    id='predictions-dropdown-sector2',
                    children=[dcc.Dropdown(
                        id='predictions-component-sector2',
                        options=models,
                        clearable=False,
                        value='Decision Tree Regressor'
                    )]
                ),
                html.H1(
                    id='predictions-dropdown2',
                    children=[dcc.Dropdown(
                        id='predictions-component-second2',
                        options=years,
                        clearable=False,
                        value=2014
                    )]
                )
            ],
        ),
        dcc.Graph(id='predictions-graph2', config={'displayModeBar': False}, animate=True),
    ],
)

# Show histogram with predictions --------------------------------------------------------------------------------------

@app.callback(Output('predictions-graph', 'figure'),
              Input('city-dropdown-component', 'value'),
              Input('predictions-component-sector', 'value'))
def show_initial_elements(city, model):

    predictions_, expectations_ = get_predictions_with_model(city, model)

    fig1 = px.line(predictions_)
    fig2 = px.line(expectations_)

    fig1.update_traces(line_color='#fec036', line_width=2)
    fig2.update_traces(line_color='#FF00FF', line_width=2)


    fig3 = go.Figure(data=fig1.data + fig2.data,
                     layout=go.Layout(
                         margin={'t': 30, 'r': 35, 'b': 40, 'l': 50},
                         legend=dict(title=None, orientation='v', y=0.7, yanchor='bottom', x=1, xanchor='right'),
                         font=dict(color='gray'),
                         paper_bgcolor='#2b2b2b',
                         plot_bgcolor='#2b2b2b',
                         autosize=True,
                         bargap=0.1,
                         xaxis={'gridcolor': '#636363', 'showline': False},
                         yaxis={'showgrid': False, 'showline': False}
                     )
                     )
    return fig3



@app.callback(Output('predictions-graph2', 'figure'),
              Input('city-dropdown-component', 'value'),
              Input('predictions-component-second2', 'value'),
              Input('predictions-component-sector2', 'value'))
def show_initial_elements(city, year, model):

    y_pred, y_test = get_scatter(city, year, model)

    #fig1 = px.scatter(df, x="sepal_width", y="sepal_length", color='petal_length')
    fig = go.Figure()


    fig.add_trace(go.Scatter(x=np.arange(1, len(y_pred) + 1), y=y_pred,

                             name='ŷ'))
    fig.add_trace(go.Scatter(x=np.arange(1, len(y_test) + 1), y=y_test,

                             name='y'))

    fig.update_layout(margin={'t': 30, 'r': 35, 'b': 40, 'l': 50},
                       legend=dict(title=None, orientation='v', y=0.7, yanchor='bottom', x=1, xanchor='right'),
                      font=dict(color='gray'),
                      paper_bgcolor='#2b2b2b',
                      plot_bgcolor='#2b2b2b',
                      autosize=True,
                      bargap=0.1,
                      xaxis={'dtick': 5, 'gridcolor': '#636363', 'showline': False},
                      yaxis={'showgrid': False})
    return fig

# ----------------------------------------------------------------------------------------------------------------------

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
        slider,
        html.Div(
            id='panel',
            children=[
                histogram,
                html.Div(),
            ],
        ),
        html.H1(),
        html.Div(
            children=[
                predictions,
                html.Div(),
            ],
        ),
        html.H1(),
        html.Div(
            children=[
                predictions2,
                html.Div(id='panel-lower' ),
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
     return 'Predictions are in yellow'
#
#
# @app.callback(
#     Output('country-description', 'children'),
#     [Input('dropdown-component', 'value')],
# )
# def update_description(val):
#     text = ' '
#
#     if val == "France":
#         text = ( ' ' )
#
#     elif val == "Germany":
#         text = (  ' '  )
#     return text
#
if __name__ == "__main__":
    app.run_server(debug=True)
