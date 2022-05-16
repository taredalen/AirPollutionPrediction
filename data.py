import os
import pathlib
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
# -----------------------------------------------------------------------------------------------------------------------

def get_clrtap_df():
    url = os.path.join(APP_PATH, os.path.join('data', 'clean_clrtap.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    return df

def get_df(country):
    url = os.path.join(APP_PATH, os.path.join('data', 'data_' + country + '.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    df.dropna()
    return df

# ----------------------------------------------------------------------------------------------------------------------
def country_df_map(country, city, sector):
    map_df = get_df(country)

    if city != 'All':
        index_city = map_df[map_df['City'] != city].index
        map_df.drop(index_city, inplace=True)

    if sector != 'All':
        index_sector = map_df[map_df['eprtrSectorName'] != sector].index
        map_df.drop(index_sector, inplace=True)

    # index_pollutant = map_df[map_df['pollutant'] != 'Sulphur oxides (SOX)'].index
    # map_df.drop(index_pollutant, inplace=True)

    return map_df


def sector_emissions_per_country(country, pollutant, sector):
    df = get_df(country)

    df = df[df['Country_Code'].notna()]

    if pollutant != 'All':
        index_pollutant = df[df['Pollutant_name'] != pollutant].index
        df.drop(index_pollutant, inplace=True)

    if sector != 'All':
        index_sector = df[df['Sector_label_EEA'] != sector].index
        df.drop(index_sector, inplace=True)

    return df
