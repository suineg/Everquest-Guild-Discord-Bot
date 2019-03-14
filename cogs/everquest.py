from collections import namedtuple
from datetime import datetime
from difflib import get_close_matches
from urllib import parse

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

from helpers.utils import *
from interface import eqdkp, twitter, gifs
from models.raidevent import RaidEvent


class EverQuest(commands.Cog, name='everquest'):

    def __init__(self, bot):
        self.bot = bot
        self.characters = []

    @commands.command()
    async def alla(self, ctx, *, search):
        """Find Eq Item on Allakhazam"""

        def extract_alla_data(tag):
            AllaMatch = namedtuple('AllaMatch', ['name', 'url', 'type'])
            _name = tag.string
            _url = tag['href']
            _type = 'Unknown'
            match = re.search(r'/db/(\w*).html\?.*', _url)
            if match:
                _type = match.group(1).capitalize()
            return AllaMatch(name=_name, url=_url[1:], type=_type)

        url = 'http://everquest.allakhazam.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        }

        search_url = parse.quote_plus(f'{url}search.html?q={search.replace(" ", "+")}', safe='/:?=+')
        response = requests.get(search_url, headers=headers)
        raw = BeautifulSoup(response.text, 'html.parser')
        all_divs = raw.find_all(name='div', class_='tbcont')
        if all_divs:
            a_href_tags = [item
                           for sublist in [div.find_all(name='a', href=True) for div in all_divs]
                           for item in sublist]
            alla_matches = [extract_alla_data(a)
                            for a in a_href_tags
                            if a.string]
            close_matches = get_close_matches(word=search,
                                              possibilities=[am.name for am in alla_matches],
                                              n=10,
                                              cutoff=0.25)
            am_match_list = [am for am in alla_matches if am.name in close_matches]
            description = '\n'.join([f"{am.type}: [{am.name}]({url}{am.url})"
                                     for am in am_match_list])
        else:
            description = f'No good matches for `{search}`'

        embed = discord.Embed(title='Allakhazam Matches',
                              description=description,
                              colour=discord.Colour.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(rate=3, per=10.0, type=commands.BucketType.user)
    async def dkp(self, ctx, *, filters: to_kwargs = None):
        """
        Get standings directly from EQDKP.

        Filters:                            Examples:
        - class=list of classes               !dkp class=war,sk,pal
        - char=list of characters             !dkp char=grisvok,venun,drillisen
        - 30day>percentage of raids           !dkp 30day>50
        - ^ 60day and 90day also              !dkp 90day<35
        - orderby=list of columns             !dkp class=war orderby=dkp,30day
        - top=number to return                !dkp class=war,sk,pal orderby=dkp top=5


        Note: This data is cached every 60 seconds live from our eqdkp site

        """

        points = eqdkp.get_points(filters)
        chunks = [points[i:i + 10] for i in range(0, len(points), 10)]
        for chunk in chunks:
            await ctx.send(f"""```
{chunk}```""")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addraid(self, ctx, *, event: RaidEvent):
        """Add a raid to the eqdkp site

         1. You need to attach a RaidRoster file along with this command.
         2. You can enter a part of an event name, or the event id in order to select it
            __Please note: Because of this, make sure what you're entering is enough of a partial
            to match the correct event you're looking for.__


        :param event: Partial name of event, or ID
        :return: EQDKP Raid
        """

        def check_author(m):
            return m.author == ctx.author

        if not event:
            return await ctx.send("`Error: A valid raid event is required.`")

        msg = None
        if not ctx.message.attachments:
            try:
                await ctx.send("`It appears you forgot to attach a RaidRoster file.  Please do that now.`")
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                if not msg.attachments or 'RaidRoster' not in msg.attachments[0].filename:
                    raise Exception
            except Exception:
                return await ctx.send("Addraid cancelled: You did not upload a RaidRoster file.")

        attachments = ctx.message.attachments or msg.attachments
        raid_files = [file for file in attachments if 'RaidRoster' in file.filename]

        characters = eqdkp.get_characters()

        async with ctx.typing():
            for file in raid_files:
                await download_attachment(file.url)
                with open(file.filename, 'r') as f:
                    content = f.readlines()
                os.remove(file.filename)
                datetime_str = ' '.join(file.filename.replace('.txt', '').split('-')[1:])
                raid_datetime = datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M%S').strftime('%Y-%m-%d %H:%M')
                raiders = [x.split('\t')[1] for x in content]
                raiders_missing = [raider
                                   for raider in raiders
                                   if raider not in [character.name
                                                     for character in characters]]

                if raiders_missing:
                    await ctx.send(f"""```md
# Missing Players

The following [{len(raiders_missing)}][raiders] are not currently in EqDkp:
{', '.join(raiders_missing)}

1. Would you like to add them to eqdkp & raid? [Yes/No, default=Yes]```""")
                    try:
                        msg = await ctx.bot.wait_for('message', check=check_author, timeout=10)
                        add_raiders = False if "no" in msg.content.lower() else True
                    except Exception:
                        add_raiders = True

                    if add_raiders:
                        for raider in raiders_missing[:]:
                            new_character = None  # eqdkp.create_character(raider)
                            if new_character:
                                characters.append(new_character)
                                raiders_missing.remove(raider)
                                await ctx.send(f"Created `{new_character.name}` on eqdkp.  Please link to proper user")
                            else:
                                # raiders.remove(raider)
                                await ctx.send(f"Failed to created `{raider}`.  Please create manually and add to raid")

                await ctx.send(f"""```md
# Raid Note

> If you don't enter anything, the note will be set to {event.name}

1. Please enter a note for this raid:```""")
                try:
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=15)
                    note = msg.content.upper()
                except Exception:
                    note = None

                raid_attendees = [c.id
                                  for c in characters
                                  if c.name in raiders
                                  and c.name not in raiders_missing]
                raid = eqdkp.create_raid(raid_datetime, raid_attendees, event.value, event.id, note)

                if raid:
                    raid_url = f"index.php/Raids/{event.name.replace(' ', '-')}-r{raid['raid_id']}.html?s="
                    url = os.getenv('EQDKP_URL') + raid_url
                    embed = discord.Embed(title='Raid Created',
                                          url=url,
                                          description=event.name,
                                          colour=discord.Colour.red())
                    embed.set_thumbnail(url=gifs.Giphy.NSFW("thomas the train").url)
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    embed.add_field(name='DKP', value=event.value)
                    embed.add_field(name='Raiders', value=str(len(raid_attendees)))
                    embed.add_field(name='Date', value=raid_datetime)
                    embed.add_field(name='Note', value=note)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send('Raid failed to create.  Please upload manually')

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
        embed.set_image(url=gifs.Giphy.NSFW("thomas the train").url)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        guild = self.bot.get_guild(int(os.environ.get('DISCORD_GUILD_ID', 0)))
        batphone_channel = guild.get_channel(int(os.environ.get('DISCORD_BATPHONE_CHANNEL_ID', 0)))

        await ctx.send(f'`Batphone sent: {status.text}`')
        await batphone_channel.send(f'@everyone {status.text}', embed=embed)

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def additem(self, ctx, *, character):
        """Not enabled yet"""

        # TODO Implement
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addadjustment(self, ctx, *, message=None):
        """Not enabled yet"""

        # TODO Implement
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addcharacter(self, ctx, character=None):
        """Add a character to the eqdkp site"""

        created_char = eqdkp.create_character(character.capitalize())
        if created_char:
            self.characters.append(created_char)
            await ctx.send(f"{created_char.name} was created!")
        else:
            await ctx.send(f"Failed to create {character}.  Please try again later, or create them manually.")

    @addraid.before_invoke
    async def get_data(self, ctx):
        self.characters = eqdkp.get_characters()

    @addraid.error
    async def addraid_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('`Error: Missing Raid Name/ID.  Syntax: !addraid [raid event name|raid event id]`')

    @addcharacter.error
    async def addcharacter_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('`Error: Missing Character Name.  Syntax: !addcharacter [character name]`')


def setup(bot: commands.Bot):
    bot.add_cog(EverQuest(bot))
