import asyncio

import praw


class Subreddit:
    _valid_exts = ['gif', 'png', 'jpg', 'mp4']
    _nsfw = ['gonewild', 'nsfw_gif', 'nsfw_gay']

    def __init__(self, subreddits):
        self.reddit = praw.Reddit(user_agent='linux:amtrak-discord-bot:v0.1.0 (by /u/superdonkeyts)')
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

    @classmethod
    def dicks(cls):
        subreddits = ['cospenis', 'penis', 'cock', 'massivecock', 'blackdick', 'ratemycock', 'malesmasturbating',
                      'ladybonersgw', 'growler']
        return cls(subreddits)

    async def random(self):
        is_gif = False
        random = None
        while not is_gif:
            random = self.reddit.subreddit(self.subreddits).random()
            if not random.is_self and random.url and random.url[-3:] in self._valid_exts:
                is_gif = True
            await asyncio.sleep(.25)
        return random
