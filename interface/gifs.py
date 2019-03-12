import os
import random

import requests


class Giphy:
    def __init__(self, search, rating):
        api_token = os.environ.get('GIPHY_API', 'wjP0OE12ghrnnxdOPtKH4AE2bfrdnVl0')
        url = 'https://api.giphy.com/v1/gifs/search'
        params = {
            'api_key': api_token,
            'q': f'"{search}"',
            'limit': 15,
            'offset': random.choice(range(5)),
            'rating': rating,
            'lang': 'en'
        }
        response = requests.get(url=url, params=params)

        if response.ok and response.status_code == 200:
            list_of_images = response.json()['data']
            self.url = random.choice(list_of_images)['images']['fixed_height']['url']

    @classmethod
    def NSFW(cls, search):
        return cls(search, 'R')

    @classmethod
    def SFW(cls, search):
        return cls(search, 'PG-13')
