import os
import pathlib
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

#-----------------------------------------------------------------------------------------------------------------------

def separate_by_county():

    df = pd.read_csv('clean_clrtap.csv', on_bad_lines='skip', sep='\t')

    all_countries = df['Country'].unique()
    print(all_countries)

    grouped = df.groupby(df.Country)

   # coutry = grouped.get_group("name")
    return df




separate_by_county()