import os
import pathlib
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#-----------------------------------------------------------------------------------------------------------------------

def get_countries_list_clrtap():
    url = os.path.join(APP_PATH, os.path.join('data', 'clean_clrtap.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')

    print(df.info())
    list_countries = df['Country'].unique()

    return list_countries

def get_countries_list_air():
    url = os.path.join(APP_PATH, os.path.join('data', 'F1_4_Detailed releases at facility level with E-PRTR Sector '
                                                      'and Annex I Activity detail into Air.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep=',')
    list_countries = df['countryName'].unique()
    return list_countries

def country_list_intersection():
    list_countries_air = get_countries_list_air()
    list_countries_clrtap = get_countries_list_clrtap()

    differences = list(set(list_countries_clrtap) - set(list_countries_air))
    print(differences)

    commun_countries_list = list(set(list_countries_air).intersection(list_countries_clrtap))
    print(commun_countries_list)


get_countries_list_clrtap()
#-----------------------------------------------------------------------------------------------------------------------
def create_csv_for_county():
    url = os.path.join(APP_PATH, os.path.join('data', 'clean_clrtap.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')

    list_countries = df['Country'].unique()
    for c in range(len(list_countries)):
        print(list_countries[c])
        grouped = df.groupby(df['Country'])
        country = grouped.get_group(list_countries[c])
        country.to_csv(r'data_' + list_countries[c] + '.csv', index=False, sep='\t')
    return df
