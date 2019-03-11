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
pd.set_option('display.max_columns', 6)
pd.set_option('display.width', 1000)
pd.set_option('display.column_space', 25)

# EQDKP API CONFIGURATION
_URL = os.environ['EQDKP_URL']
_API_URL = _URL + 'api.php'
_API_TOKEN = os.environ['EQDKP_API_TOKEN']
_API_HEADERS = {'X-Custom-Authorization': f'token={_API_TOKEN}&type=user'}
_API_PARAMS = {'format': 'json'}


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

    payload = {
        'name': f'{character}',
        'servername': 'Amtrak'
    }
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
    eqdkp_columns = ['CHARACTER', 'CLASS', 'DKP', '30DAY', '60DAY', '90DAY']
    n = len(eqdkp_columns)
    data_by_player = [player_data_raw[i:i + n] for i in range(0, len(player_data_raw), n)]

    # Create the DataFrame
    df = pd.DataFrame(data_by_player, columns=eqdkp_columns)

    # Convert DKP & Attendance columns
    attendance_cols = ["30DAY", "60DAY", "90DAY"]
    df[attendance_cols] = df[attendance_cols].applymap(lambda x: Attendance(x))
    df['DKP'] = df['DKP'].apply(lambda x: float(x))

    # Apply default sorting and index
    df = df.sort_values(by=['DKP', '30DAY'], ascending=[False, False])
    df = df.reset_index(drop=True)
    df.index += 1

    return df


def get_points(filters=None):

    # Get a Cached Dataframe if available, otherwise query new one
    df = get_raw_data()

    # Apply Custom Sorting
    if 'ORDERBY' in filters:
        order_by = filters.pop('ORDERBY')
        ascending = [True if o in ['CHARACTER', 'CLASS'] else False for o in order_by]
        df = df.sort_values(by=order_by, ascending=ascending)

    # Set Top N (applied in return)
    n = 50
    if 'TOP' in filters:
        n_str = filters.pop('TOP')[0]
        n = int(n_str) if n_str.is_numeric() else n
        n = 50 if n > 50 else n

    # Apply filters
    if filters:
        for key, value in filters.items():
            if type(value) == list:
                good_values = []
                if key == "CLASS":
                    good_values = [k
                                   for x in value
                                   for k, v in config.EQ_CLASS_SIMILARITIES.items()
                                   if x.lower() in v or x.lower() == k.lower()]
                if key == "CHARACTER":
                    good_values = [v.capitalize() for v in value]
                df_filter = df.__getattr__(key).isin(good_values)
            else:
                df_filter = eval(f"df.__getattr__('{key}') {value}")
            df = df[df_filter]

    return df.head(n)
