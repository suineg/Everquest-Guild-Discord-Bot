import datetime
import os
import random

import requests
from discord.ext import commands

import helpers.config as config
import helpers.eqdkp as eqdkp

_EQDKP_URL = os.environ['EQDKP_URL']
_EQDKP_API_URL = _EQDKP_URL + 'api.php'
_EQDKP_API_TOKEN = os.environ['EQDKP_API_TOKEN']
_EQDKP_API_HEADERS = {'X-Custom-Authorization': f'token={_EQDKP_API_TOKEN}&type=api'}
_EQDKP_API_PARAMS = {'format': 'json'}


class DKP(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dkp(self, ctx, *, filters):
        """
        Get DKP standings

        Filters:
            1.) Each filter is designed as a key=value pairing.
            2.) Text filters will be set with = and can include a comma separated list for value
            3.) Numeric filters can be set with >, <, >=, <= and must include an integer for value
            4.) Additional filters will be separated by a space.  No spaces must exist in a key=value pairing

        Output Columns:
            Filters can be built around the following 6 columns (orderby defaults)
            1.) Character (Asc)
            2.) Class (Asc)
            3.) DKP (Desc)
            4.) 30Day (Desc)
            5.) 60Day (Desc)
            6.) 90Day (Desc)

        Additional Filters:
            In addition to be able to filter on each column, can you can provide these extras:
            1.) orderby=(comma separated list of columns)
            2.) top=#.  (Bot will not ever give more than 50)

        Examples:
            Top 5 warriors by 30 day:       !dkp class=war orderby=30day top=5
            Top 10 tanks over 2k DKP:       !dkp class=war,pal,sk dkp>2000 top=10
            [WRONG] No spaces in filter:    !dkp class=shadow knight
            Top 20 players by DKP, 30day:   !dkp top=20                              (Default sort)
        """

        seconds_remaining = config.SPAM_DELAY_IN_SECONDS - (datetime.now() - config.LAST_RUN).seconds
        if seconds_remaining > 0:
            await ctx.send(f"{random.choice(config.INSULTS)} [{seconds_remaining} seconds remaining...]")
        else:
            config.LAST_RUN = datetime.now()
            filters = self.parse_args(*filters)
            points = eqdkp.get_points(filters)
            chunks = [points[i:i + 10] for i in range(0, len(points), 10)]
            for chunk in chunks:
                await ctx.send(f"""```
{chunk}```""")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addraid(self, ctx, *, message):
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def additem(self, ctx, *, message):
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addadjustment(self, ctx, *, message):
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addcharacter(self, ctx, character):
        """Add a character to the EQDKP site"""

        json = {
            'name': f'{character}',
            'servername': 'Amtrak'
        }
        params = _EQDKP_API_PARAMS
        params['function'] = 'character'

        response = requests.post(_EQDKP_API_URL, headers=_EQDKP_API_HEADERS, params=params, json=json)

        if response and response.json()['status'] == 1:
            character_id = response.json()['character_id']
            await ctx.send(f'''```{character} was successfully added to {_EQDKP_URL}.
Character Id: {character_id}````''')
