import os

import discord
from discord.ext import commands

from helpers import twitter, gifs
from helpers.utils import *


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def batphone(self, ctx, *, message: add_est_timestamp = None):
        """Send a tweet to the AmtrakEQ Twitter account."""

        if not message:
            return ctx.send(f"""{ctx.author.mention} I'm already doing 90% of the work.  
Do you want me to come up with the message too?""")

        status = twitter.post_tweet(message)

        if type(status) == str:
            return await ctx.send(f'`Tweet failed: {status}`')

        embed = discord.Embed(title='Batphone',
                              url=f'https://twitter.com/AmtrakEq/status/{status.id}',
                              description=message,
                              colour=discord.Colour.red(),
                              author=ctx.author.display_name, timestamp=datetime.datetime.now())
        embed.set_image(url=gifs.Gif.Giphy("thomas the train").url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        guild_id = int(os.environ.get('DISCORD_GUILD_ID', 0))
        batphone_channel_id = int(os.environ.get('DISCORD_BATPHONE_CHANNEL_ID', 0))
        batphone_channel = self.bot.get_guild(guild_id).get_channel(batphone_channel_id)

        await ctx.send(f'`Batphone sent: {status.text}`')
        await batphone_channel.send(f'@everyone {status.text}', embed=embed)
