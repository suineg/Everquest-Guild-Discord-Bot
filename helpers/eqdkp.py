import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache

from helpers import config

cache = TTLCache(maxsize=100, ttl=180)


@cached(cache)
def get_raw_data():

    # Get the HTML & Parse it
    response = requests.get(os.environ['EQDKP_URL']+config.POINTS_URL)
    raw_html = BeautifulSoup(response.text, 'html.parser')
    overview_table_html = raw_html.find(name='table', class_='hptt')
    player_data_html = overview_table_html.find_all(name='span', attrs={'positive',
                                                                        'negative',
                                                                        'neutral',
                                                                        re.compile('class_*')})
    player_data_raw = [data.string for data in player_data_html]
    n = len(config.EQDKP_COLUMNS)
    data_by_player = [player_data_raw[i:i + n] for i in range(0, len(player_data_raw), n)]

    # Create the DataFrame
    df = pd.DataFrame(data_by_player, columns=config.EQDKP_COLUMNS)

    # Convert DKP & Attendance columns
    attendance_cols = ["30DAY", "60DAY", "90DAY"]
    df[attendance_cols] = df[attendance_cols].applymap(lambda x: Attendance(x))
    df['DKP'] = df['DKP'].apply(lambda x: int(x))

    # Apply default sorting and index
    df = df.sort_values(by=list(config.INDEX_SORT.keys()), ascending=list(config.INDEX_SORT.values()))
    df = df.reset_index(drop=True)
    df.index += 1

    return df


def get_points(filters=None):

    # Get a Cached Dataframe if available, otherwise query new one
    df = get_raw_data()

    # Apply Custom Sorting
    if 'ORDERBY' in filters:
        order_by = [o.upper() for o in filters['ORDERBY']]
        ascending = [config.ORDER_BY_ASC_DEFAULTS[o] for o in order_by]
        df = df.sort_values(by=order_by, ascending=ascending)

    # Set Top N (applied in return)
    n = 50
    if 'TOP' in filters and filters['TOP'][0].isnumeric():
        n = int(filters['TOP'][0])
        n = 50 if n > 50 else n

    # Apply filters
    for key, value in filters.items():
        if key in config.ADDITIONAL_FILTERS:
            continue
        if type(value) == list:
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

    def parse_args(*s):
        if s is None:
            return None
        filters = {}
        operators = ['=', ':', ';']
        comparisons = ['>', '<', '>=', '<=']
        value_splits = [',', '/']
        arg_pairs = [re.split(r'(\W)', arg_pair, maxsplit=1) for arg_pair in s]
        try:
            for arg_pair in arg_pairs:

                # Define the filter key
                key = arg_pair[0].upper()
                key = "CHARACTER" if key == "NAME" or key == "CHAR" else key

                if key not in (config.EQDKP_COLUMNS + config.ADDITIONAL_FILTERS):
                    continue

                if arg_pair[1] not in operators and arg_pair[1] not in comparisons:
                    raise SyntaxError(''.join(arg_pair))

                if arg_pair[1] in operators:
                    value = re.split('|'.join(value_splits), arg_pair[2])

                else:
                    value = ' '.join(arg_pair[1:])

                filters[key] = value

        except SyntaxError:
            pass
        finally:
            return filters
