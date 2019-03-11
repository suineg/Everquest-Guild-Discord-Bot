import datetime
import os

import discord
from dateutil import tz
from discord.ext import commands

from helpers import twitter


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def tweet(self, ctx, *, message):
        """Send a tweet to the AmtrakEQ Twitter account. Required role: @Admin or @Raid Leader"""

        now = datetime.datetime.now(tz=tz.gettz('America/New_York'))
        status = twitter.post_tweet(f'{message} ({now.strftime("%I:%M %p")})')

        if type(status) == str:
            return await ctx.send(f'`Tweet failed: {status}`')
        else:
            await ctx.send(f'`Batphone sent: {status.text}`')

            embed = discord.Embed(title='Batphone',
                                  description=f'@everyone {status.text}',
                                  colour=discord.Colour.teal(),
                                  author=ctx.author.display_name,
                                  timestamp=now)
            discord_server = self.bot.get_guild(os.environ['DISCORD_GUILD_ID'])
            batphone_channel = discord_server.get_channel(os.environ['DISCORD_BATPHONE_CHANNEL_ID'])

            await batphone_channel.send(embed=embed)
