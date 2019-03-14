import os
import random
from abc import *

import requests


class Gif(ABC):

    def __init__(self, api_key, host_url, query_key, params, headers=None):
        self.api_key = api_key
        self.host_url = host_url
        self.query_key = query_key
        self.params = params
        self.headers = headers

    @abstractmethod
    def search(self, query_value):
        self.params[self.query_key] = query_value
        response = requests.get(url=self.host_url,
                                params=self.params)
        return response if response.ok and response.status_code == 200 else None


class Giphy(Gif):

    def __init__(self):
        api_key = os.getenv('GIPHY_API')
        host_url = 'http://api.giphy.com/v1/gifs/search'
        query_key = 'q'
        params = {
            'limit': 40,
            'key': api_key
        }
        super().__init__(api_key=api_key, host_url=host_url,
                         query_key=query_key, params=params)

    def search(self, query_value):
        response = super().search(query_value)
        return [gif['bitly_gif_url'] for gif in response.json()['data']] if response else []


class Tenor(Gif):

    def __init__(self):
        api_key = os.getenv('TENOR_API')
        host_url = 'https://api.tenor.com/v1/search'
        query_key = 'q'
        params = {
            'limit': 40,
            'rating': 'R',
            'api_key': api_key
        }
        super().__init__(api_key=api_key, host_url=host_url,
                         query_key=query_key, params=params)

    def search(self, query_value):
        response = super().search(query_value)
        return [gif['url'] for gif in response.json()['results']] if response else []


def get_one_gif(query):
    giphy = Giphy().search(query)
    tenor = Tenor().search(query)
    return random.choice(giphy + tenor)
