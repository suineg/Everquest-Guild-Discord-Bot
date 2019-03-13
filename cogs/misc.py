import re
import typing
from collections import namedtuple
from difflib import get_close_matches
from urllib import parse

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from interface import gifs


class Misc(commands.Cog, name="Miscellaneous"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, search: typing.Optional[str] = "thomas the train"):
        """Random GIPHY"""

        if ctx.channel.is_nsfw():
            await ctx.send(gifs.Giphy.NSFW(search).url)
        else:
            await ctx.send(gifs.Giphy.NSFW(search).url)

    @commands.command()
    async def alla(self, ctx, *, search):
        """Find Eq Item on Allakhazam"""

        def extract_alla_data(tag):
            AllaMatch = namedtuple('AllaMatch', ['name', 'url', 'type'])
            _name = tag.string
            _url = tag['href']
            _type = 'Unknown'
            match = re.search(r'/db/(\w*).html\?.*', _url)
            if match:
                _type = match.group(1).capitalize()
            return AllaMatch(name=_name, url=_url[1:], type=_type)

        url = 'http://everquest.allakhazam.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        }

        search_url = parse.quote_plus(f'{url}search.html?q={search.replace(" ", "+")}', safe='/:?=+')
        response = requests.get(search_url, headers=headers)
        raw = BeautifulSoup(response.text, 'html.parser')
        all_divs = raw.find_all(name='div', class_='tbcont')
        if all_divs:
            a_href_tags = [item
                           for sublist in [div.find_all(name='a', href=True) for div in all_divs]
                           for item in sublist]
            alla_matches = [extract_alla_data(a)
                            for a in a_href_tags
                            if a.string]
            close_matches = get_close_matches(search, [am.name for am in alla_matches], n=15, cutoff=0.25)
            am_match_list = [am for am in alla_matches if am.name in close_matches]
            description = '\n'.join([f"{am.type}: [{am.name}]({url}{am.url})"
                                     for am in am_match_list])
        else:
            description = f'No good matches for `{search}`'

        embed = discord.Embed(title='Allakhazam Matches',
                              description=description,
                              colour=discord.Colour.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
