import discord
from discord.ext import commands

from interface.gifs import Subreddit


class nsfw(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dicks', 'cock', 'girth', 'chode', 'schlong', 'shaft'])
    @commands.guild_only()
    async def dick(self, ctx):
        """Get a random dick pic from reddit"""

        sub = await Subreddit.dicks().random()
        embed = discord.Embed(
            author=ctx.bot.user.name,
            colour=discord.Colour.dark_blue()
        )
        embed.set_image(url=sub.url)
        await ctx.send(f'|| {sub.url} ||', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(nsfw(bot))
