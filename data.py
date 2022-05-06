import os
import pathlib
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#-----------------------------------------------------------------------------------------------------------------------

def get_clrtap_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'clean_clrtap.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    return df

def get_map_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'F1_4_Detailed releases at facility level with E-PRTR Sector '
                                                      'and Annex I Activity detail into Air.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep=',')
    return df
get_map_df()

#-----------------------------------------------------------------------------------------------------------------------

def clear_clrtap_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'CLRTAP_NVFR14_V21_GF.csv'))
    df = pd.read_csv(url, sep='\t')

    df = df.dropna(how='any', subset=['Emissions'])

    # TODO: replace data with random one to check if we can drop those rows, ref lib for check a pattern of missing value
    # https://github.com/ResidentMario/missingno = > amputation missing values

    sector_conditions = [
        (df['Sector_code'].isin(['1A1a', '1A1b', '1A1c', '1B1a', '1B1b', '1B1c', '1B2ai', '1B2aiv', '1B2av', '1B2b', '1B2c', '1B2d'])),
        (df['Sector_code'].isin(['1A2a', '1A2b', '1A2c', '1A2d', '1A2e', '1A2f', '1A2gvii', '1A2gviii'])),
        (df['Sector_code'].isin(['1A3ai(i)', '1A3aii(i)', '1A3c', '1A3di(ii)', '1A3dii', '1A3ei', '1A3eii', '1A4ciii'])),
        (df['Sector_code'].isin(['1A3bi', '1A3bii', '1A3biii', '1A3biv', '1A3bv', '1A3bvi', '1A3bvii'])),
        (df['Sector_code'].isin(['1A4ai', '1A4aii', '1A4bi', '1A4bii', '1A4ci', '1A4cii', '1A5a', '1A5b'])),
        (df['Sector_code'].isin(['2A1', '2A2', '2A3', '2A5a', '2A5b', '2A5c', '2A6', '2B1', '2B10a', '2B10b', '2B2', '2B3', '2B5', '2B6', '2B7', '2C1', '2C2', '2C3', '2C4', '2C5', '2C6', '2C7a', '2C7b', '2C7c', '2C7d', '2D3a', '2D3b', '2D3c', '2D3d', '2D3e', '2D3f', '2D3g', '2D3h', '2D3i', '2G', '2H1', '2H2', '2H3', '2I', '2J', '2K', '2L'])),
        (df['Sector_code'].isin(['3B1a', '3B1b', '3B2', '3B3', '3B4a', '3B4d', '3B4e', '3B4f', '3B4gi', '3B4gii', '3B4giii', '3B4giv', '3B4h', '3Da1', '3Da2a', '3Da2b', '3Da2c', '3Da3', '3Da4', '3Db', '3Dc', '3Dd', '3De', '3Df', '3F', '3I'])),
        (df['Sector_code'].isin(['5A', '5B1', '5B2', '5C1a', '5C1bi', '5C1bii', '5C1biii', '5C1biv', '5C1bv', '5C1bvi', '5C2', '5D1', '5D2', '5D3', '5E', '6A'])),
        (df['Sector_code'].isin(['6A', 'test'])),
        (df['Sector_code'].isin(['National total for the entire territory (based on fuel sold)', 'NATIONAL TOTAL']))]

    sector_values = ['Energy production and distribution', 'Energy use in industry', 'Non-road transport',
              'Road transport', 'Commercial, institutional and households', 'Industrial processes and product use',
              'Agriculture', 'Waste', 'Other', 'National total for the entire territory']

    df['Sector_label_EEA'] = np.select(sector_conditions, sector_values, default='Other')

    unit_conditions = [
        (df['Sector_code'] == 'Mg'),
        (df['Sector_code'] == 'Gg'),
        (df['Sector_code'] == 'g')]

    unit_values = [df['Emissions']/1000000, df['Emissions']*1000000, df['Emissions']/1000]
    df['Emissions'] = np.select(unit_conditions, unit_values, default=df['Emissions'])

    df.drop(columns='Unit', inplace=True) #  TODO : data standardization ?? impossible to drop column, check for later
    # min max model, drop national total

    df.to_csv(r'clean_clrtap.csv', index=False, sep='\t')


def get_polluants():
    df = pd.DataFrame(get_clrtap_df(), columns=['Country', 'Pollutant_name'])
    df = df.groupby('Pollutant_name')['Country'].apply(list).reset_index(name='Country_Pollutant')
    df['count'] = df['Country_Pollutant'].str.len()

    index_pollutant = df[df['count'] < df['count'].mean()].index
    df.drop(index_pollutant, inplace=True)

    return np.append('All', df['Pollutant_name'])

#----------------------------------------------------------------------------------------------------------------------
def country_df_map(country):
    map_df = get_map_df()
    index_pollutant = map_df[map_df['countryName'] != country].index
    map_df.drop(index_pollutant, inplace=True)
    return map_df

def sector_emissions_per_country(country, pollutant, sector):
    df = get_clrtap_df()
    index_country = df[df['Country'] != country].index
    df.drop(index_country, inplace=True)

    if pollutant != 'All':
        index_pollutant = df[df['Pollutant_name'] != pollutant].index
        df.drop(index_pollutant, inplace=True)

    if sector != 'All':
        index_sector = df[df['Sector_label_EEA'] != sector].index
        df.drop(index_sector, inplace=True)

    index_country = df[df['Country'] != country].index
    df.drop(index_country, inplace=True)

    return df

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