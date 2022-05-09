import os
import pathlib
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

#-----------------------------------------------------------------------------------------------------------------------

def get_countries_list_clrtap():
    df = pd.read_csv('clean_clrtap.csv', on_bad_lines='skip', sep='\t')
    list_countries = df['Country'].unique()

    print(list_countries)
    # ['Finland' 'France' 'Ireland' 'Portugal' 'Bulgaria' 'Croatia' 'Estonia'
    #  'Latvia' 'Malta' 'Slovenia' 'Norway' 'Denmark' 'Germany' 'Greece'
    #  'Sweden' 'Cyprus' 'Lithuania' 'Poland' 'Romania' 'EU28' 'Iceland'
    #  'Austria' 'Italy' 'United Kingdom' 'Belgium' 'Netherlands' 'Spain'
    #  'Czech Republic' 'Slovakia' 'Hungary' 'Turkey' 'EEA33' 'Switzerland'
    #  'Luxembourg' 'Liechtenstein']


def get_countries_list_air():
    df = pd.read_csv(
        'F1_4_Detailed releases at facility level with E-PRTR Sector and Annex I Activity detail into Air.csv',
        on_bad_lines='skip', sep=',')
    list_countries = df['countryName'].unique()
    return list_countries


def country_list_intersection():
    list_countries_air = get_countries_list_air()
    list_countries_clrtap = get_countries_list_clrtap()

    differences = list(set(list_countries_air) - set(list_countries_clrtap))
    print(differences)  # ['Serbia', 'Czechia']
    # 'Czechia', is used as the 'Czech Republic' in list_countries_clrtap
    # there is no data about Serbia in list_countries_clrtap

#-----------------------------------------------------------------------------------------------------------------------
def create_csv_for_county():
    df = pd.read_csv('clean_clrtap.csv', on_bad_lines='skip', sep='\t')
    list_countries = df['Country'].unique()
    for c in range(len(list_countries)):
        print(list_countries[c])
        grouped = df.groupby(df['Country'])
        country = grouped.get_group(list_countries[c])
        country.to_csv(r'data_' + list_countries[c] + '.csv', index=False, sep='\t')
    return df
