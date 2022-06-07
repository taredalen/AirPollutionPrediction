import os
import pathlib
import pandas as pd
import numpy as np
import warnings

from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings('ignore')


from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

url = os.path.join(APP_PATH, os.path.join('data', 'F1_4_clean_data.csv'))
df = pd.read_csv(url, on_bad_lines='skip', sep=',',  na_filter=True)
df = df.rename(columns={'countryName': 'country', 'reportingYear':'year'}).drop(columns=['Unnamed: 0'], axis=1)
df_pivoted = df.pivot_table(index=['City', 'year'], columns=['pollutant'], values='emissions', aggfunc=np.sum, fill_value=0)
df_pivoted.reset_index(inplace=True)

models = {'Random Forest Regressor': RandomForestRegressor(n_estimators=1000, max_depth=2, random_state=1),
          'Decision Tree Regressor': DecisionTreeRegressor(random_state=1),
          'Linear Regression': LinearRegression()}

# -----------------------------------------------------------------------------------------------------------------------

def get_clrtap_df(country):
    url = os.path.join(APP_PATH, os.path.join('data', 'clrtap_data_' + country + '.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    df.dropna()
    return df

def get_air_df(country):
    url = os.path.join(APP_PATH, os.path.join('data', 'air_data_' + country + '.csv'))
    df = pd.read_csv(url, on_bad_lines='skip', sep='\t')
    df.dropna()
    return df

# ----------------------------------------------------------------------------------------------------------------------
def country_df_map(country, city, sector):
    map_df = get_air_df(country)

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
    df = get_clrtap_df(country)

    if pollutant != 'All':
        index_pollutant = df[df['Pollutant_name'] != pollutant].index
        df.drop(index_pollutant, inplace=True)

    if sector != 'All':
        index_sector = df[df['Sector_label_EEA'] != sector].index
        df.drop(index_sector, inplace=True)

    return df
# ----------------------------------------------------------------------------------------------------------------------

def get_test_train_city(city):

    df_pivoted = df.pivot_table(index=['City', 'year'], columns=['pollutant'], values='emissions', aggfunc=np.sum, fill_value=0)

    df_pivoted.reset_index(inplace=True)
    index_country = df_pivoted[df_pivoted['City'] != city].index
    df_pivoted.drop(index_country, inplace=True)

    df_pivoted['total'] = df_pivoted.iloc[:,2:50].sum(axis=1)
    years = df_pivoted['year'].unique().tolist()
    splits = {'train': [], 'test': []}

    for index, yr in enumerate(years[:-1]):

        df_test = df_pivoted.loc[df_pivoted.year.isin([years[index+1]]), :]
        df_train = df_pivoted.loc[df_pivoted.year.isin(years[:index+1]), :]

        splits['test'].append(df_test[['total', 'year']])
        splits['train'].append(df_train[['total', 'year']])

    year_list = df_pivoted['year'].unique().tolist()

    return splits, year_list



def get_predictions(splits, year_list, model, option):

    predictions = []
    expectations = []

    for i in range(1, len(year_list)-1):

        X_train = splits['train'][i][['year']]
        y_train = splits['train'][i][['total']]
        X_test = splits['test'][i][['year']]
        y_test = splits['test'][i][['total']]

        StandardScaler().fit_transform(X_train, X_test)

        model.fit(X_train, y_train.values.ravel())

        y_pred = model.predict(X_test)
        predictions.append(y_pred)
        expectations.append(y_test.values.ravel())

        mean_absolute_error(y_test, y_pred)

    if option:
        return expectations
    else:
        return predictions

def get_predictions_with_model(city, model):

    splits, year_list = get_test_train_city(city)
    predictions = get_predictions(splits, year_list, models[model], False)
    expectations = get_predictions(splits, year_list, models[model], True)

    return predictions, expectations




def get_scatter(city, year, model):
    years = [2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    splits, y = get_test_train_city(city)
    index = years.index(year)
    print(index)

    X_train = splits['train'][index][['year']]
    y_train = splits['train'][index][['total']]
    X_test = splits['test'][index][['year']]
    y_test = splits['test'][index][['total']]

    StandardScaler().fit_transform(X_train, X_test)

    model = models[model]
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return y_pred, y_test

   # print(f'RMSE of {model} :', np.sqrt(mean_squared_error(y_pred, y_test)))
   # print(f'R² score on test set using {model} :', r2_score(y_test, y_pred))


