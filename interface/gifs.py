import asyncio
import os
import random

import praw
import requests


class Subreddit:

    _valid_exts = ['gif', 'png', 'jpg', 'mp4']

    def __init__(self, subreddits):
        self.reddit = praw.Reddit(user_agent='linux:amtrak-discord-bot:v0.1.0')
        self.subreddits = subreddits

    @property
    def subreddits(self):
        return self._subreddits

    @subreddits.setter
    def subreddits(self, value):
        if type(value) == list:
            self._subreddits = '+'.join(value)
        else:
            self._subreddits = value.replace(' ', '+').replace(',', '+')

    async def random(self):
        is_gif = False
        random = None
        while not is_gif:
            random = self.reddit.subreddit(self.subreddits).random()
            if not random.is_self and random.url and random.url[-3:] in self._valid_exts:
                is_gif = True
            await asyncio.sleep(.25)
        return random


class Gif:

    def __init__(self, api_key, host_url, query_key, params, headers=None):
        self.api_key = api_key
        self.host_url = host_url
        self.query_key = query_key
        self.params = params
        self.headers = headers

    @classmethod
    def Giphy(cls):
        api_key = os.getenv('GIPHY_API')
        host_url = 'http://api.giphy.com/v1/gifs/search'
        query_key = 'q'
        params = {
            'limit': 100,
            'rating': 'R',
            'api_key': api_key
        }
        return cls(api_key=api_key, host_url=host_url, query_key=query_key, params=params)

    def search(self, query_value):
        self.params[self.query_key] = query_value
        response = requests.get(url=self.host_url,
                                params=self.params)
        if response.ok and response.status_code == 200:
            data = response.json()['data']
            gif = random.choice(data)
            return gif['bitly_gif_url']

        return None
