from collections import namedtuple

from discord.ext import commands

from interface.reddit import Subreddit

RedditCommand = namedtuple('RedditCommand', ['aliases', 'reddits'])


class nsfw(commands.Cog):
    _reddits = {
        'nsfw': RedditCommand(aliases=['wild'],
                              reddits=['gonewild', 'nsfw_gif', 'nsfw_gifs']),

        'dick': RedditCommand(aliases=['dicks', 'cock', 'girth', 'chode', 'schlong', 'shaft', 'johnson'],
                              reddits=['cospenis', 'penis', 'cock', 'massivecock', 'blackdick', 'ratemycock',
                                       'malesmasturbating', 'ladybonersgw', 'growler', 'thickdick']),

        'boob': RedditCommand(aliases=['boobs', 'tit', 'tits', 'titties', 'breast', 'breasts', 'knockers', 'jugs',
                                       'cans', '80085'],
                              reddits=['redditbesttits', 'boobs', 'fortyfivefiftyfive', 'bustypetite', 'boobbounce',
                                       'tittydrop', 'boobies']),

        'hentai': RedditCommand(aliases=['yuri', 'ecchi', 'eechi', 'lestai', 'poonyetah', 'hentei', 'guro'],
                                reddits=['yuri', 'ahegao', 'rule34', 'monstergirl', 'Rule34Overwatch']),

        'gay': RedditCommand(aliases=['fag', 'faggot', 'homo', 'homosexual'],
                             reddits=['nsfw_gay', 'gayblowjobs', 'guysfrombehind', 'gaygifs']),

        'bear': RedditCommand(aliases=['furry'],
                              reddits=['gaybears']),

        'jesus': RedditCommand(aliases=['christ', 'christian', 'lordsavior', 'god'],
                               reddits=['jesus', 'dankchristianmemes', 'funnyjesus']),

        'honeyhole': RedditCommand(aliases=['hh'],
                                   reddits=['guysfrombehind']),

        'tranny': RedditCommand(aliases=['kontra', 'chickswithdicks', 'shemale', 'trap', 'ladyboy', 'trans'],
                                reddits=['ShemalesParadise', 'shemales']),

        'eqgirls': RedditCommand(aliases=['eqgirl', 'wowgirl', 'chub', 'fat', 'chubby'],
                                 reddits=['voluptuous', 'gonewildchubby', 'bww_chubby'])
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=_reddits['nsfw'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def nsfw(self, ctx):
        """This is not for Drillisen"""
        pass

    @commands.command(aliases=_reddits['dick'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def dick(self, ctx):
        """Stare at it until you're not afraid anymore."""
        pass

    @commands.command(aliases=_reddits['boob'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def boob(self, ctx):
        """Please tell your boobs to stop staring at my eyes."""
        pass

    @commands.command(aliases=_reddits['hentai'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def hentai(self, ctx):
        """Can we make sweet memes together Onii-Chan??"""
        pass

    @commands.command(aliases=_reddits['gay'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def gay(self, ctx):
        """Sorry.  I got semen in your beard"""
        pass

    @commands.command(aliases=_reddits['bear'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def bear(self, ctx):
        """It's too cold to not have a furry rub up all on you"""
        pass

    @commands.command(aliases=_reddits['jesus'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def jesus(self, ctx):
        """Praise our Lord and Savior Jesus Christ"""
        pass

    @commands.command(aliases=_reddits['honeyhole'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def honeyhole(self, ctx):
        """How far does this honey hole go?"""
        pass

    @commands.command(aliases=_reddits['honeyhole'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def honeyhole(self, ctx):
        """How far does this honey hole go?"""
        pass

    @commands.command(aliases=_reddits['tranny'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def tranny(self, ctx):
        """Is that what I think it is?"""
        pass

    @commands.command(aliases=_reddits['eqgirls'].aliases)
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.default)
    async def eqgirls(self, ctx):
        """She's in my static group <3"""
        pass

    async def cog_after_invoke(self, ctx):
        reds = self._reddits[ctx.command.name].reddits
        sub = await Subreddit(reds).random()
        url = f'|| {sub.url} ||' if sub.over_18 else sub.url
        await ctx.send(url)


def setup(bot: commands.Bot):
    bot.add_cog(nsfw(bot))
