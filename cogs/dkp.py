from discord.ext import commands

import helpers.eqdkp as eqdkp


class DKP(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(rate=3, per=10.0, type=commands.BucketType.user)
    async def standings(self, ctx, *, filters=None):
        """
        Get DKP standings

        Filters:
            1.) Each filter is designed as a key=value pairing.
            2.) Text filters will be set with = and can include a comma separated list for value
            3.) Numeric filters can be set with >, <, >=, <= and must include an integer for value
            4.) Additional filters will be separated by a space.  No spaces must exist in a key=value pairing

        Output Columns:
            Filters can be built around the following 6 columns (orderby defaults)
            1.) Character (Asc)
            2.) Class (Asc)
            3.) DKP (Desc)
            4.) 30Day (Desc)
            5.) 60Day (Desc)
            6.) 90Day (Desc)

        Additional Filters:
            In addition to be able to filter on each column, can you can provide these extras:
            1.) orderby=(comma separated list of columns)
            2.) top=#.  (Bot will not ever give more than 50)

        Examples:
            Top 5 warriors by 30 day:       !dkp class=war orderby=30day top=5
            Top 10 tanks over 2k DKP:       !dkp class=war,pal,sk dkp>2000 top=10
            [WRONG] No spaces in filter:    !dkp class=shadow knight
            Top 20 players by DKP, 30day:   !dkp top=20                              (Default sort)
        """

        filters = eqdkp.parse_args(*filters)
        points = eqdkp.get_points(filters)
        chunks = [points[i:i + 10] for i in range(0, len(points), 10)]
        for chunk in chunks:
            await ctx.send(f"""```
{chunk}```""")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addraid(self, ctx, *, message=None):
        """Add a raid to the EQDKP site"""

        # TODO Implement
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def additem(self, ctx, *, message=None):
        """Add a character to the EQDKP site"""

        # TODO Implement
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addadjustment(self, ctx, *, message=None):
        """Add a raid adjustment to the EQDKP site"""

        # TODO Implement
        await ctx.send("This feature isn't enabled yet.")

    @commands.command()
    @commands.has_any_role('Admin', 'Raid Leader')
    async def addcharacter(self, ctx, character=None):
        """Add a character to the EQDKP site"""

        if not character:
            return ctx.send('`Please provide a character name to create.`')

        json = eqdkp.create_character(character)
        if json:
            if json['status'] == 0:
                return await ctx.send('`Error processing request: {}`'.format(json['error']))
            else:
                character_id = json['character_id']
                await ctx.send(f'`{character} was successfully added. (Id: {character_id})`')
