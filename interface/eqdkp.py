import os
import re
from collections import namedtuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache

from helpers import config
from models.attendance import Attendance
from models.raid import Raid
from models.raidevent import RaidEvent

# CACHE CONFIGURATION
_cache = TTLCache(maxsize=100, ttl=60)

# PANDAS DISPLAY CONFIGURATION
pd.set_option('display.max_rows', 25)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)
pd.set_option('display.column_space', 25)

# EQDKP API CONFIGURATION
_URL = os.getenv('EQDKP_URL')
_API_URL = _URL + 'api.php'
_API_TOKEN = os.getenv('EQDKP_API_TOKEN')
_API_HEADERS = {'X-Custom-Authorization': f'token={_API_TOKEN}&type=api'}

# GET STANDINGS CONFIGURATION
EQDKP_COLUMNS = ['CHARACTER', 'CLASS', 'DKP', '30DAY', '60DAY', '90DAY']
ATTENDANCE_COLUMNS = ["30DAY", "60DAY", "90DAY"]
DEFAULT_ORDER = ['DKP', '30DAY']
TOP_N = 50

Character = namedtuple('Character', ['id',
                                     'name',
                                     'active',
                                     'hidden',
                                     'main_id',
                                     'main_name',
                                     'class_id',
                                     'class_name',
                                     'points',
                                     'items',
                                     'adjustments'])


def post(function, payload):
    params = {'format': 'json', 'function': function}
    response = requests.post(url=_API_URL, headers=_API_HEADERS, params=params, json=payload)
    success = response.ok and response.status_code == 200
    if success:
        data = response.json()
        status = data.pop('status')
        return data if status == 1 else None
    else:
        return None


def get(function, params=None):
    default_params = {'format': 'json', 'function': function}
    if params:
        for param, value in params.items():
            default_params[param] = value
    response = requests.get(url=_API_URL, headers=_API_HEADERS, params=default_params)
    success = response.ok and response.status_code == 200
    if success:
        data = response.json()
        status = data.pop('status')
        return data if status == 1 else None
    else:
        return None


def create_character(character):
    """This will create a character on eqdkp"""

    Character = namedtuple('Character', 'id name')
    payload = {'name': character}
    response = post(function='character', payload=payload)
    return Character(id=response['character_id'], name=character) if response else None


def create_raid(raid_date, raid_attendees, raid_value, raid_event_id, raid_note=None):
    """This will create a raid on eqdkp"""

    payload = {
        'raid_date': raid_date,
        'raid_attendees': {'member': raid_attendees},
        'raid_value': raid_value,
        'raid_event_id': raid_event_id,
        'raid_note': raid_note or ''
    }
    return post(function='add_raid', payload=payload)


def create_raid_item(item_date, item_buyers, item_value, item_name, item_raid_id, item_itempool_id=1):
    """This will add a raid item on eqdkp"""

    payload = {
        'item_date': item_date,
        'item_buyers': {'member': item_buyers},
        'item_value': item_value,
        'item_name': item_name,
        'item_raid_id': item_raid_id,
        'item_itempool_id': item_itempool_id
    }
    return post(function='add_item', payload=payload)


def create_adjustment(adjustment_date,
                      adjustment_reason,
                      adjustment_members,
                      adjustment_value,
                      adjustment_raid_id,
                      adjustment_event_id):
    """This will create a raid adjustment on eqdkp"""

    payload = {
        'adjustment_date': adjustment_date,
        'adjustment_reason': adjustment_reason,
        'adjustment_members': {'member': adjustment_members},
        'adjustment_value': adjustment_value
    }
    if adjustment_raid_id:
        payload['adjustment_raid_id'] = adjustment_raid_id
    elif adjustment_event_id:
        payload['adjustment_event_id'] = adjustment_event_id

    return post(function='add_adjustment', payload=payload)


def get_events():
    """This will get all characters in eqdkp and their corresponding id's"""

    response = get('events')
    return [RaidEvent(**data) for event, data in response.items()] if response else None


def get_raids(n: int = 100):
    """This will get the last N raids from eqdkp (Default: 100)"""

    params = {'number': n}
    response = get('raids', params=params)
    return [Raid(**data) for raid, data in response.items()] if response else None


def get_characters():
    """This will get all characters in eqdkp and their corresponding id's"""

    response = get('points')
    return [Character(**data) for player, data in response['players'].items()] if response else None


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
    n = TOP_N

    # Get a Cached Dataframe if available, otherwise query new one
    df = get_raw_data()

    if filters:

        # Apply Custom Sorting
        if 'ORDERBY' in filters:
            columns = filters.pop('ORDERBY')

        # Set Top N (applied in return)
        if 'TOP' in filters:
            n_str = filters.pop('TOP')
            n = 50 if not n_str.isnumeric() else 50 if int(n_str) > 50 else int(n_str)

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

    return df.head(n or TOP_N)


def order_df(df, columns):
    if type(columns) == str:
        columns = [columns]
    columns = ['CHARACTER' if col in ['CHAR', 'NAME'] else col.upper() for col in columns]
    ascending = [True if col in ['CHARACTER', 'CLASS'] else False for col in columns]
    df = df.sort_values(by=columns, ascending=ascending)
    df = df.reset_index(drop=True)
    df.index += 1
    return df
