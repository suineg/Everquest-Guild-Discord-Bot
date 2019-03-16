import typing

import discord
from discord.ext import commands

from interface.gifs import get_one_gif


class Fun(commands.Cog, name="fun"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, search: typing.Optional[str] = 'thomas the tank engine'):
        """Search and get a random result back from Giphy & Tenor"""

        gif_url = get_one_gif(search)
        embed = discord.Embed(colour=discord.Colour.dark_red())
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
