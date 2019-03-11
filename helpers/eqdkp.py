import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache

from helpers import config
from models.attendance import Attendance

# CACHE CONFIGURATION
_cache = TTLCache(maxsize=100, ttl=180)

# PANDAS DISPLAY CONFIGURATION
pd.set_option('display.max_rows', 25)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
pd.set_option('display.column_space', 25)

# EQDKP API CONFIGURATION
_URL = os.environ['EQDKP_URL']
_API_URL = _URL + 'api.php'
_API_TOKEN = os.environ['EQDKP_API_TOKEN']
_API_HEADERS = {'X-Custom-Authorization': f'token={_API_TOKEN}&type=api'}
_API_PARAMS = {'format': 'json'}

# GET STANDINGS CONFIGURATION
EQDKP_COLUMNS = ['CHARACTER', 'CLASS', 'DKP', '30DAY', '60DAY', '90DAY']
ATTENDANCE_COLUMNS = ["30DAY", "60DAY", "90DAY"]
DEFAULT_ORDER = ['DKP', '30DAY']
TOP_N = 50


def post(function, payload):
    params = _API_PARAMS
    params['function'] = function
    response = requests.post(url=_API_URL,
                             headers=_API_HEADERS,
                             params=params,
                             json=payload)
    return response.json() if response.ok else None


def create_character(character):
    """This will create a character on eqdkp"""

    payload = {'name': character}
    return post('character', payload)


def create_raid():
    """This will create a raid on eqdkp"""
    # TODO Implement
    pass


def create_raid_item():
    """This will add a raid item on eqdkp"""
    # TODO Implement
    pass


def create_adjustment():
    """This will create a raid adjustment on eqdkp"""
    # TODO Implement
    pass


@cached(_cache)
def get_raw_data():

    # Get the HTML & Parse it
    response = requests.get(os.environ['EQDKP_URL'] + 'index.php/Points')
    raw_html = BeautifulSoup(response.text, 'html.parser')
    overview_table_html = raw_html.find(name='table', class_='hptt')
    player_data_html = overview_table_html.find_all(name='span', attrs={'positive',
                                                                        'negative',
                                                                        'neutral',
                                                                        re.compile('class_*')})
    player_data_raw = [data.string for data in player_data_html]
    n = len(EQDKP_COLUMNS)
    data_by_player = [player_data_raw[i:i + n] for i in range(0, len(player_data_raw), n)]

    # Create the DataFrame
    df = pd.DataFrame(data_by_player, columns=EQDKP_COLUMNS)

    # Convert DKP & Attendance columns
    df[ATTENDANCE_COLUMNS] = df[ATTENDANCE_COLUMNS].applymap(lambda x: Attendance(x))
    df['DKP'] = df['DKP'].apply(lambda x: float(x))

    # Apply default sorting and dkp ranking columns
    df = order_df(df, DEFAULT_ORDER)
    df.insert(loc=3, column='DKP RANK', value=df.index)

    return df


def get_points(filters=None):
    columns = DEFAULT_ORDER

    # Get a Cached Dataframe if available, otherwise query new one
    df = get_raw_data()

    if filters:

        # Apply Custom Sorting
        if 'ORDERBY' in filters:
            columns = filters.pop('ORDERBY')

        # Set Top N (applied in return)
        if 'TOP' in filters:
            n_str = filters.pop('TOP')
            n = 50 if not n_str.is_numeric() else 50 if int(n_str) > 50 else int(n_str)

        # Apply column filters
        for key, value in filters.items():

            key = 'CHARACTER' if key in ['NAME', 'CHAR'] else key
            if key in ['CLASS', 'CHARACTER']:
                if type(value) == str:
                    value = [value]

                if key == 'CLASS':
                    good_values = [k
                                   for x in value
                                   for k, v in config.EQ_CLASS_SIMILARITIES.items()
                                   if x.lower() in v or x.lower() == k.lower()]
                else:
                    good_values = [v.capitalize() for v in value]

                df_filter = df.__getattr__(key).isin(good_values)

            else:
                value = value.replace('GTE', '>=').replace('LTE', '<=').replace('GT', '>').replace('LT', '<')
                print(f'Converted value: {value}')
                df_filter = eval(f"df.__getattr__('{key}') {value}")

            df = df[df_filter]

    # Reindex before returning
    df = order_df(df, columns)

    return df.head(n)


def order_df(df, columns):
    if type(columns) == str:
        columns = [columns]
    columns = ['CHARACTER' if col in ['CHAR', 'NAME'] else col.upper() for col in columns]
    ascending = [True if col in ['CHARACTER', 'CLASS'] else False for col in columns]
    df = df.sort_values(by=columns, ascending=ascending)
    df = df.reset_index(drop=True)
    df.index += 1
    return df
