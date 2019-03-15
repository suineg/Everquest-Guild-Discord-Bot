from datetime import datetime

import discord
from discord.ext import commands

from helpers.errors import *
from helpers.utils import *
from interface import eqdkp, twitter, gifs, allakhazam
from models.raid import Raid
from models.raidevent import RaidEvent


class EverQuest(commands.Cog, name='everquest'):

    def __init__(self, bot):
        self.guild_id = int(os.getenv('DISCORD_GUILD_ID', 0))
        self.batphone_id = int(os.getenv('DISCORD_BATPHONE_CHANNEL_ID', 0))
        self.dkp_log_id = int(os.getenv('DISCORD_DKP_ENTRY_LOG_CHANNEL_ID', 0))
        self.bot = bot
        self.characters = []

    @commands.command(aliases=['item', 'quest', 'mob', 'spell', 'recipe'])
    async def alla(self, ctx, *, query: str):
        """Find Eq Item on Allakhazam"""

        description = allakhazam.search_alla(query)
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

        # Check for RaidRoster file
        msg = None
        if not ctx.message.attachments:
            try:
                await ctx.send("`It appears you forgot to attach a RaidRoster file.  Please do that now.`")
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                if not msg.attachments or 'RaidRoster' not in msg.attachments[0].filename:
                    raise InvalidRaidRosterFile
            except InvalidRaidRosterFile:
                return await ctx.send("Add raid cancelled: You did not upload a valid RaidRoster file.")

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
                raid_datetime = datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M%S')
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
                            new_character = eqdkp.create_character(raider)
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
                raid = eqdkp.create_raid(raid_datetime.strftime('%Y-%m-%d %H:%M'),
                                         raid_attendees,
                                         event.value,
                                         event.id,
                                         note)

                if raid:
                    raid_url = f"index.php/Raids/{event.name.replace(' ', '-')}-r{raid['raid_id']}.html?s="
                    url = os.getenv('EQDKP_URL') + raid_url
                    embed = discord.Embed(title=f'Raid {raid["raid_id"]} Created',
                                          url=url,
                                          description=event.name,
                                          colour=discord.Colour.red())
                    embed.set_thumbnail(url=gifs.get_one_gif("thomas the train"))
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    embed.add_field(name='Raid Id', value=raid['raid_id'])
                    embed.add_field(name='Raid Date', value=raid_datetime)
                    embed.add_field(name='# of Killers', value=str(len(raid_attendees)))
                    embed.add_field(name='DKP Value', value=event.value)
                    embed.add_field(name='Raid Note', value=note, inline=False)

                    channel = ctx.bot.get_guild(self.guild_id).get_channel(self.dkp_log_id)
                    await channel.send(embed=embed)
                    await ctx.send(f'Raid `ID: {raid["raid_id"]} EVENT: {event.name}` was successfully created')
                else:
                    await ctx.send('Raid failed to create.  Please upload manually')

    @commands.command(aliases=['tweet', 'letsgo', 'wakeup'])
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
        embed.set_image(url=gifs.get_one_gif("thomas the train"))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        channel = ctx.bot.get_guild(self.guild_id).get_channel(self.batphone_id)
        await ctx.send(f'`Batphone sent: {status.text}`')
        await channel.send(f'@everyone {status.text}', embed=embed)

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def additem(self, ctx, raid: Raid):
        """
        Add an item to an EQDKP raid

        Please enter a valid raid id for the <raid> parameter.

        Where is the raid id?
        - It's posted in the Raid Confirmation message from me after !addraid
        - It's available in the URL of the raid.  It's the r number right before the '.html'
        """

        def check_author(m):
            return m.author == ctx.author

        if raid:
            await ctx.send(f"""```md
# Raid Found!

You have selected Raid #[{raid.id}][{raid.event_name}] on {raid.date}

> If this is the wrong raid, please enter <cancel> now

1. Please enter the items from this raid in the following format: <Character> <DKP> <Item Name>
2. When you are done entering items, enter <done>
```""")
            try:
                while True:
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=30)
                    response = msg.content.replace("<", "").replace(">", "")

                    if "done" in response.lower():
                        break

                    if "cancel" in response.lower():
                        return None

                    parts = response.split()
                    if len(parts) < 3:
                        await ctx.send(f'The following response `{msg.content}` was not valid.  Please try again.')
                        continue

                    character_part = parts[0]
                    item_value_part = parts[1]
                    item_name_part = parts[2:]

                    # Validate the character
                    character = [c for c in self.characters if c.name.lower() == character_part.lower()]
                    if not character:
                        await ctx.send(f'The following character `{character_part}` was not valid.  Please try again.')
                        continue
                    character = character[0]

                    # Validate the item value
                    if not item_value_part.isnumeric():
                        await ctx.send(f'The following dkp of `{item_value_part}` is not a number.  Please try again.')
                        continue
                    item_value = int(item_value_part)

                    # TODO validate item_name
                    item_name = ' '.join(item_name_part).capitalize()

                    raid_item = eqdkp.create_raid_item(item_date=raid.date,
                                                       item_name=item_name,
                                                       item_raid_id=raid.id,
                                                       item_value=item_value,
                                                       item_buyers=[character.id])
                    if raid_item:
                        await ctx.send(
                            f"`{item_name} was successfully charged to {character.name} for {item_value} dkp.  "
                            f"Continue with the next item, or type done.`")
                    else:
                        await ctx.send(f"`ERROR: {item_name} failed to get entered.  Please try again`")

            except Exception:
                pass

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
    @addcharacter.before_invoke
    @additem.before_invoke
    async def get_data(self, ctx):
        self.characters = eqdkp.get_characters()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'`Error: Missing Required Argument.  Please refer to !help {ctx.command.name}`')


def setup(bot: commands.Bot):
    bot.add_cog(EverQuest(bot))
