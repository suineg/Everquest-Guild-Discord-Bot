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
        gif_urls = [data['images']['original']['url']
                    for data in response.json()['data']] if response else []
        return gif_urls


class Tenor(Gif):

    def __init__(self):
        api_key = os.getenv('TENOR_API')
        host_url = 'https://api.tenor.com/v1/search'
        query_key = 'q'
        params = {
            'limit': 40,
            'rating': 'R',
            'media_filter': 'basic',
            'api_key': api_key
        }
        super().__init__(api_key=api_key, host_url=host_url,
                         query_key=query_key, params=params)

    def search(self, query_value):
        response = super().search(query_value)
        gif_urls = [image['gif']['url']
                    for result in response.json()['results']
                    for image in result['media']] if response else []
        return gif_urls


def get_one_gif(query):
    giphy = Giphy().search(query)
    tenor = Tenor().search(query)
    return random.choice(giphy + tenor)
