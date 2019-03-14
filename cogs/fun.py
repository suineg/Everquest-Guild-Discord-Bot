import typing

from discord.ext import commands

from interface.gifs import Gif


class fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, search: typing.Optional[str] = 'thomas the tank engine'):
        gif = Gif.Giphy().search(search)
        await ctx.send(gif)


def setup(bot: commands.Bot):
    bot.add_cog(fun(bot))
