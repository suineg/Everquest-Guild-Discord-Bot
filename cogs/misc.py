import typing

from discord.ext import commands

from interface import gifs


class Misc(commands.Cog, name="Miscellaneous"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, search: typing.Optional[str] = "thomas the train"):
        if ctx.channel.is_nsfw():
            await ctx.send(gifs.Giphy.NSFW(search).url)
        else:
            await ctx.send(gifs.Giphy.NSFW(search).url)
