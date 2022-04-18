import json
import os
import pathlib

import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

with open(os.path.join(APP_PATH, os.path.join('data', 'custom.geo.json')), 'r') as f:
  counties = json.load(f)


def initial_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'F1_4_Detailed releases at facility level with E-PRTR Sector and Annex I Activity detail into Air.csv'))
    return pd.read_csv(url, on_bad_lines='skip', sep=',')

def country_df(country):
    df = initial_df()
    index_pollutant = df[df['countryName'] != country].index
    df.drop(index_pollutant, inplace=True)
    return df

def clrtap_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'CLRTAP_NVFR14_V21_GF.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')

    df = df.dropna(how='any', subset=['Emissions'])

    df['Sector_label_EEA'] = np.nan

    for i, row in df.iterrows():
        val = row['Sector_code']
        dictionary = {'Energy production and distribution': ['1A1a', '1A1b', '1A1c', '1B1a', '1B1b', '1B1c', '1B2ai', '1B2aiv', '1B2av', '1B2b', '1B2c', '1B2d'],
                      'Energy use in industry': ['1A2a', '1A2b', '1A2c', '1A2d', '1A2e', '1A2f', '1A2gvii', '1A2gviii'],
                      'Non-road transport': ['1A3ai(i)', '1A3aii(i)', '1A3c', '1A3di(ii)', '1A3dii', '1A3ei', '1A3eii', '1A4ciii'],
                      'Road transport': ['1A3bi', '1A3bii', '1A3biii', '1A3biv', '1A3bv', '1A3bvi', '1A3bvii'],
                      'Commercial, institutional and households': ['1A4ai', '1A4aii', '1A4bi', '1A4bii', '1A4ci', '1A4cii', '1A5a', '1A5b'],
                      'Industrial processes and product use': ['2A1', '2A2', '2A3', '2A5a', '2A5b', '2A5c', '2A6', '2B1', '2B10a', '2B10b', '2B2', '2B3', '2B5', '2B6', '2B7', '2C1', '2C2', '2C3', '2C4', '2C5', '2C6', '2C7a', '2C7b', '2C7c', '2C7d', '2D3a', '2D3b', '2D3c', '2D3d', '2D3e', '2D3f', '2D3g', '2D3h', '2D3i', '2G', '2H1', '2H2', '2H3', '2I', '2J', '2K', '2L'],
                      'Agriculture': ['3B1a', '3B1b', '3B2', '3B3', '3B4a', '3B4d', '3B4e', '3B4f', '3B4gi', '3B4gii', '3B4giii', '3B4giv', '3B4h', '3Da1', '3Da2a', '3Da2b', '3Da2c', '3Da3', '3Da4', '3Db', '3Dc', '3Dd', '3De', '3Df', '3F', '3I'],
                      'Waste': ['5A', '5B1', '5B2', '5C1a', '5C1bi', '5C1bii', '5C1biii', '5C1biv', '5C1bv', '5C1bvi', '5C2', '5D1', '5D2', '5D3', '5E', '6A'],
                      'Other': ['6A'],
                      'National total for the entire territory (based on fuel sold)': ['National total for the entire territory (based on fuel sold)']
                      }
        result = [k for k, v in dictionary.items() if val in v]
        result = ''.join(result)
        #df.at[i, 'Sector label EEA'] = result
        row['Sector_label_EEA'] = result
        print(row['Sector_label_EEA'])
    df.to_csv(r'clean_clrtap.csv', index=False, sep='\t')
    print('ok')
    print(df.head(5))
    return df

def country_emissions():
    url = os.path.join(APP_PATH, os.path.join('data', 'CLRTAP_NVFR14_V21_GF.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    df = df.dropna(how='any', subset=['Emissions'])
    return df

def sector_emissions_per_country(country):
    df = clrtap_df()
    df = df.dropna(how='any', subset=['Emissions'])

    index_country = df[df['Country'] != country].index
    df.drop(index_country, inplace=True)
    return df

def emissions_by_pollutant_per_country(): # check if data was updated & country
    df = clrtap_df()
    df = df.dropna(how='any', subset=['Emissions'])
    df = df[['Emissions', 'Sector_name', 'Year', 'Pollutant_name']]
    #df['Sector_name'].unique()
    df.sort_values(by ='Emissions')


'''''fig = px.choropleth_mapbox(sector_emissions_per_country('France'),
                           geojson=counties, locations='Country', color='Emissions',
                               color_continuous_scale="Viridis",
                               #range_color=(0, 12),
                               mapbox_style="carto-positron",
                               zoom=3,
                               opacity=0.5
                              )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
'''''