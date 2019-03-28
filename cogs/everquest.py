import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from helpers.errors import *
from helpers.msgtemplates import *
from helpers.utils import *
from interface import eqdkp, twitterapi, gifs, allakhazam
from models.raid import Raid
from models.raidevent import RaidEvent


class EverQuest(commands.Cog, name='everquest'):

    def __init__(self, bot):
        self.bot = bot
        self.characters = []

    def has_any_channel(*channels):
        async def predicate(ctx):
            return ctx.channel.name in channels or ctx.channel.id in channels

        return commands.check(predicate)

    @commands.command(aliases=['item', 'quest', 'mob', 'spell', 'recipe'])
    async def alla(self, ctx, *, query: str):
        """Find Eq Item on Allakhazam"""

        description = allakhazam.search_alla(query)
        embed = discord.Embed(title='Allakhazam Matches',
                              description=description,
                              colour=discord.Colour.red())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=['standings'])
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
            await ctx.author.send(f"""```\n{chunk}```""")

    @commands.command(aliases=['tweet', 'letsgo', 'wakeup'])
    @commands.has_any_role('Admin', 'Raid Leader')
    async def batphone(self, ctx, *, message: add_est_timestamp = None):
        """Send a tweet to the AmtrakEQ Twitter account."""

        if not message:
            return ctx.send(f"""{ctx.author.mention} I'm already doing 90% of the work.  
    Do you want me to come up with the message too?""")

        status = twitterapi.post_tweet(message)

        embed = discord.Embed(title='Batphone',
                              url=f'https://twitter.com/AmtrakEq/status/{status.id}',
                              description=message,
                              colour=discord.Colour.red())
        embed.set_image(url=gifs.get_one_gif("thomas the train"))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        await ctx.send(f'`Batphone sent: {status.text}`')
        await ctx.bot.batphone_channel.send(f'@everyone {status.text}', embed=embed)

    @commands.group()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.guild)
    @commands.has_role('DKP')
    @has_any_channel('dkp-entry')
    async def add(self, ctx):
        pass

    @add.command()
    async def raid(self, ctx, *, event: RaidEvent):
        """
        Add a raid to the eqdkp site

         1. You need to attach a RaidRoster file along with this command.
         2. You can enter a part of an event name, or the event id in order to select it

            Please note: Because of this, make sure what you're entering is enough of a partial
            to match the correct event you're looking for.
        """

        def check_author(m):
            return m.author == ctx.author

        if not event:
            return await ctx.send("`Error: A valid raid event is required.`")

        # Check for RaidRoster file
        attachments = ctx.message.attachments
        while not attachments:
            await ctx.send("`It appears you forgot to attach a RaidRoster file.  Please do that now.`")
            msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
            attachments = msg.attachments

        if 'RaidRoster' not in attachments[0].filename:
            raise InvalidRaidRosterFile

        raid_files = [file for file in attachments]

        async with ctx.typing():
            for file in raid_files:

                # Download and parse the RaidRoster File for attendees
                await download_attachment(file.url)
                with open(file.filename, 'r') as f:
                    content = f.readlines()
                os.remove(file.filename)
                datetime_str = ' '.join(file.filename.replace('.txt', '').split('-')[1:])
                raid_datetime = datetime.datetime.strptime(datetime_str, '%Y%m%d %H%M%S')
                raiders = [x.split('\t')[1] for x in content]

                # Manually add attendees to the dump from "creditt" tells
                await ctx.send(ADD_RAID_CREDITT)
                msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                creditt = False if "no" in msg.content.lower() else True

                if creditt:
                    await ctx.send(ADD_RAID_CREDITT_MEMBERS)
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                    raiders_to_add = [add.capitalize()
                                      for add in msg.content.replace(' ', '').split(',')
                                      if add.capitalize() not in raiders]
                    raiders = raiders + raiders_to_add

                # Check for attendees not in eqdkp
                raiders_missing = [raider
                                   for raider in raiders
                                   if raider not in [character.name
                                                     for character in self.characters]]
                if raiders_missing:
                    await ctx.send(ADD_RAID_MISSING_MEMBERS.format(count=len(raiders_missing),
                                                                   member_list=', '.join(raiders_missing)))
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                    add_raiders = False if "no" in msg.content.lower() else True

                    if add_raiders:
                        for raider in raiders_missing[:]:
                            new_character = eqdkp.create_character(raider)
                            if new_character:
                                self.characters.append(new_character)
                                raiders_missing.remove(raider)
                            else:
                                await ctx.send(f"Failed to create `{raider}`.  Please create manually and add to raid")

                # Add a raid note
                await ctx.send(ADD_RAID_NOTE.format(event_name=event.name))
                try:
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=20)
                    note = msg.content.upper()
                except Exception:
                    note = event.name

                # Create Raid Attendees List
                raid_attendees = {c.id: c.name
                                  for c in self.characters
                                  if c.name in raiders
                                  and c.name not in raiders_missing}

                # Create the raid
                raid = eqdkp.create_raid(raid_datetime.strftime('%Y-%m-%d %H:%M'),
                                         [cid for cid, cname in raid_attendees.items()],
                                         event.value,
                                         event.id,
                                         note)

                if raid:
                    raid_url = f"index.php/Raids/{event.name.replace(' ', '-')}-r{raid['raid_id']}.html?s="
                    url = os.getenv('EQDKP_URL') + raid_url

                    attendees_by_name = [cname for cid, cname in raid_attendees.items()]
                    attendees_by_name.sort()
                    msg = LOG_ENTRY_FOR_RAID.format(url=url,
                                                    raid_id=raid['raid_id'],
                                                    dkp=str(event.value).center(7),
                                                    event=event.name.center(37),
                                                    date=raid_datetime.strftime('%m/%d/%Y').center(14),
                                                    attendees=', '.join(attendees_by_name))

                    await ctx.bot.dkp_entry_log_channel.send(msg)
                    await ctx.send(f'Raid `ID: {raid["raid_id"]} EVENT: {event.name}` was successfully created')
                else:
                    await ctx.send('Raid failed to create.  Please upload manually')

    @add.command()
    async def item(self, ctx, raid: Raid):
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
            # Raid Found, ask user to start entering items
            await ctx.send(RAID_FOUND.format(raid_id=raid.id,
                                             raid_event_name=raid.event_name,
                                             raid_date=raid.date))
            item_log = ''
            while True:
                # Wait for item entry: <Character> <DKP> <Item Name>
                try:
                    msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
                except asyncio.TimeoutError:
                    break

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
                    item_log += f"> {item_name.ljust(30)}{character.name.ljust(20)}{str(item_value).rjust(5)} DKP\n"

                else:
                    await ctx.send(f"`ERROR: {item_name} failed to get entered.  Please try again`")

            # Find and edit the raid log in #dkp-entry-log channel
            if len(item_log) > 0:
                async with ctx.typing():
                    channel = ctx.bot.dkp_entry_log_channel
                    messages = await channel.history(limit=50).flatten()
                    messages = [m for m in messages if f"Raid Entry Log [{raid.id}]" in m.content]
                    if messages:
                        message = messages[0]
                        items_purchased = f"""\n\n* Items Purchased\n{item_log}```"""
                        content = message.content[:-3] + items_purchased
                        await message.edit(content=content)
                        return await ctx.send(f'All done!  #{channel.name} has been edited.')
                    else:
                        return await ctx.send(
                            f"`ERROR: I wasn't able to edit #{channel.name}.  Please do so manually.`")

    @add.command(aliases=['adj'])
    async def adjustment(self, ctx, *, adjustment_reason: str):
        """Add an adjustment to the  DKP site"""

        est = pytz.timezone('US/Eastern')
        now = datetime.datetime.now(est)

        def check_author(m):
            return m.author == ctx.author

        # Get value of the adjustment
        await ctx.send(ADJUSTMENT_VALUE.format(reason=adjustment_reason))
        msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
        try:
            adjustment_value = float(msg.content)
        except ValueError:
            return await ctx.send(f"`ERROR: ValueError. {msg.content} is not a valid adjustment value.`")

        # Request a member or a comma separated list of characters
        await ctx.send(ADJUSTMENT_MEMBERS)
        msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
        members = msg.content.replace(' ', '').lower().split(',')
        members = [c for c in self.characters if c.name.lower() in members]

        # Ask if the adjustment should be applied to a raid
        await ctx.send(ADJUSTMENT_RAID)
        msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
        is_raid = True if "yes" in msg.content.lower() else False

        # Get the raid data if a Yes was answered above
        raid = None
        if is_raid:
            await ctx.send(ADJUSTMENT_RAID_ID)
            msg = await ctx.bot.wait_for('message', check=check_author, timeout=60)
            raid = await Raid.convert(ctx, int(msg.content))

        # Create the adjustment
        adjustment = eqdkp.create_adjustment(adjustment_date=raid.date if is_raid else now.strftime('%Y-%m-%d %H:%M'),
                                             adjustment_reason=adjustment_reason,
                                             adjustment_members=[m.id for m in members],
                                             adjustment_value=adjustment_value,
                                             adjustment_raid_id=raid.id if is_raid else None,
                                             adjustment_event_id=raid.event_id if is_raid else 25)

        # Confirmations
        if adjustment:
            msg = LOG_ENTRY_FOR_ADJUSTMENT.format(reason=adjustment_reason,
                                                  value=adjustment_value,
                                                  members=', '.join([m.name for m in members]))
            await ctx.bot.dkp_entry_log_channel.send(msg)
            await ctx.send(f'Adjustment was successfully created')
        else:
            await ctx.send('Adjustment failed to create.  Please upload manually')

    @add.command(aliases=['char'])
    async def character(self, ctx, character=None):
        """Add a character to the eqdkp site"""

        if character.lower() in [c.lower() for c in self.characters]:
            return await ctx.send(f"`ERROR: Duplicate Character` {character} is already added.")

        created_char = eqdkp.create_character(character.capitalize())
        if created_char:
            self.characters.append(created_char)
            await ctx.send(f"{created_char.name} was created!")
        else:
            await ctx.send(f"Failed to create {character}.  Please try again later, or create them manually.")

    @add.before_invoke
    async def get_data(self, ctx):
        self.characters = eqdkp.get_characters()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'`Error: Missing Required Argument.`  Please refer to `!help {ctx.command.name}`')
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send(f'`Error: Timeout.`  You did not respond in time.')
        if isinstance(error, InvalidRaidRosterFile):
            return await ctx.send(f'`Error: InvalidFile.`  You did not upload a valid RaidRoster file.')


def setup(bot: commands.Bot):
    bot.add_cog(EverQuest(bot))
