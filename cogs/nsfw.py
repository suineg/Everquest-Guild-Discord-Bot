from collections import namedtuple

import discord
from discord.ext import commands

from interface.gifs import Subreddit

RedditCommand = namedtuple('RedditCommand', ['aliases', 'reddits'])


class nsfw(commands.Cog):
    _reddits = {

        'nsfw': RedditCommand(aliases=['wild'],
                              reddits=['gonewild', 'nsfw_gif', 'nsfw_gifs']),

        'dick': RedditCommand(aliases=['dicks', 'cock', 'girth', 'chode', 'schlong', 'shaft', 'johnson'],
                              reddits=['cospenis', 'penis', 'cock', 'massivecock', 'blackdick', 'ratemycock',
                                       'malesmasturbating', 'ladybonersgw', 'growler']),

        'boob': RedditCommand(aliases=['boobs', 'tit', 'tits', 'titties', 'breast', 'breasts', 'knockers', 'jugs',
                                       'cans', '80085'],
                              reddits=['redditbesttits', 'boobs', 'fortyfivefiftyfive', 'bustypetite', 'boobbounce',
                                       'tittydrop', 'boobies']),

        'hentai': RedditCommand(aliases=['yuri', 'ecchi', 'eechi', 'lestai', 'poonyetah', 'hentei', 'guro'],
                                reddits=['yuri', 'ahegao', 'rule34', 'monstergirl']),

        'gay': RedditCommand(aliases=['fag', 'faggot', 'homo', 'homosexual'],
                             reddits=['nsfw_gay', 'gayblowjobs']),

        'bear': RedditCommand(aliases=['furry'],
                              reddits=['gaybears', 'gaybeards'])
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=_reddits['nsfw'].aliases)
    async def nsfw(self, ctx):
        """This is not for Drillisen"""
        pass

    @commands.command(aliases=_reddits['dick'].aliases)
    async def dick(self, ctx):
        """Stare at it until you're not afraid anymore."""
        pass

    @commands.command(aliases=_reddits['boob'].aliases)
    async def boob(self, ctx):
        """Please tell your boobs to stop staring at my eyes."""
        pass

    @commands.command(aliases=_reddits['hentai'].aliases)
    async def hentai(self, ctx):
        """Can we make sweet memes together Onii-Chan??"""
        pass

    @commands.command(aliases=_reddits['gay'].aliases)
    async def gay(self, ctx):
        """Sorry.  I got semen in your beard"""
        pass

    @commands.command(aliases=_reddits['bear'].aliases)
    async def bear(self, ctx):
        """It's too cold to not have a furry rub up all on you"""
        pass

    @nsfw.after_invoke
    @dick.after_invoke
    @boob.after_invoke
    @hentai.after_invoke
    @gay.after_invoke
    @bear.after_invoke
    async def embed_spoiler(self, ctx):
        reds = self._reddits[ctx.command.name].reddits
        sub = await Subreddit(reds).random()
        embed = discord.Embed(colour=discord.Colour.dark_blue())
        embed.set_author(name=ctx.bot.user.name)
        embed.set_image(url=sub.url)
        await ctx.send(f'|| {sub.url} ||', embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(nsfw(bot))
