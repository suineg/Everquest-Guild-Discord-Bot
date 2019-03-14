import typing

from discord.ext import commands

from interface.gifs import get_one_gif


class fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gif(self, ctx, *, search: typing.Optional[str] = 'thomas the tank engine'):
        """Search and get a random result back from Giphy & Tenor"""

        gif_url = get_one_gif(search)
        await ctx.send(gif_url)


def setup(bot: commands.Bot):
    bot.add_cog(fun(bot))
