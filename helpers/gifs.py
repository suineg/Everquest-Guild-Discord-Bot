import os
import random

import requests


class Gif:
    limit = 10
    rating = 'R'
    lang = 'en'

    def __init__(self, url):
        self.url = url

    @classmethod
    def Giphy(cls, search):
        api_token = os.environ.get('GIPHY_API', 'wjP0OE12ghrnnxdOPtKH4AE2bfrdnVl0')
        url = 'https://api.giphy.com/v1/gifs/search'
        params = {
            'api_key': api_token,
            'q': f'"{search}"',
            'limit': cls.limit,
            'offset': random.choice(range(5)),
            'rating': cls.rating,
            'lang': cls.lang
        }
        response = requests.get(url=url, params=params)

        if response.ok and response.status_code == 200:
            list_of_images = response.json()['data']
            random_image = random.choice(list_of_images)['images']['fixed_height']['url']
            print(random_image)
            return cls(random_image)
