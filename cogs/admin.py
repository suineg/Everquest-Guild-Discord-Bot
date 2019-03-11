import os

import discord
from discord.ext import commands

from helpers import twitter
from helpers.utils import *


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def tweet(self, ctx, *, message: add_est_timestamp = None):
        """Send a tweet to the AmtrakEQ Twitter account. Required role: @Admin or @Raid Leader"""

        if not message:
            return ctx.send(f"""{ctx.author.mention} I'm already doing 90% of the work.  
Do you want me to come up with the message too?""")

        status = twitter.post_tweet(message)

        if type(status) == str:
            return await ctx.send(f'`Tweet failed: {status}`')

        embed = discord.Embed(title='Batphone',
                              description=f'@everyone {status.text}',
                              colour=discord.Colour.teal(),
                              author=ctx.author.display_name)
        discord_server = self.bot.get_guild(os.environ['DISCORD_GUILD_ID'])
        batphone_channel = discord_server.get_channel(os.environ['DISCORD_BATPHONE_CHANNEL_ID'])

        await ctx.send(f'`Batphone sent: {status.text}`')
        await batphone_channel.send(embed=embed)
