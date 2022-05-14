import os
import pathlib
import warnings

import numpy as np
import pandas as pd
from IPython.core.display_functions import display

warnings.filterwarnings('ignore')

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

url = os.path.join(APP_PATH, os.path.join('data', 'F1_4_clean_data.csv'))
df_air = pd.read_csv(url, on_bad_lines='skip', sep=',')

url = os.path.join(APP_PATH, os.path.join('data', 'clean_clrtap.csv'))
df_clrtap = pd.read_csv(url, on_bad_lines='skip', sep='\t')


# -----------------------------------------------------------------------------------------------------------------------

def get_countries_list_clrtap():
    print(df_clrtap.info())
    list_countries = df_clrtap['Country'].unique()

    return list_countries


def get_countries_list_air():
    list_countries = df_air['countryName'].unique()
    return list_countries


def country_list_intersection():
    list_countries_air = get_countries_list_air()
    list_countries_clrtap = get_countries_list_clrtap()

    differences = list(set(list_countries_clrtap) - set(list_countries_air))
    print(differences)

    commun_countries_list = list(set(list_countries_air).intersection(list_countries_clrtap))
    print(commun_countries_list)
    return commun_countries_list

get_countries_list_clrtap()

# -----------------------------------------------------------------------------------------------------------------------
def create_csv_for_county():
    for i in range(len(df_air)):
        if df_air.loc[i, 'countryName'] == 'Czechia':
            df_air.loc[i, 'countryName'] = 'Czech Republic'

    df = df_air.rename(columns={'countryName': 'Country',
                                'pollutant': 'Pollutant',
                                'emissions': 'Emissions',
                                'reportingYear': 'Year'})
    result = df_clrtap.append(df)

    list_countries = country_list_intersection()

    for c in range(len(list_countries)):
        print(list_countries[c])
        grouped = result.groupby(result['Country'])
        country = grouped.get_group(list_countries[c])
        country.to_csv(r'data_' + list_countries[c] + '.csv', index=False, sep='\t')

    return result

create_csv_for_county()
