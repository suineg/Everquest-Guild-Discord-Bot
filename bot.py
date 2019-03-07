import os
import random
import re
from datetime import datetime, timedelta

import pandas as pd
from discord.ext import commands

from helpers import config, eqdkp, twapi

# Configuring Pandas default options
pd.set_option('display.max_rows', 25)
pd.set_option('display.max_columns', 6)
pd.set_option('display.width', 1000)
pd.set_option('display.column_space', 25)

# Setting initial last_run to 2 minutes ago to not trigger immediate delay warning
config.LAST_RUN = datetime.now() - timedelta(minutes=2)

# Defining the bots criteria
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),
                   description='Amtrak EQ Discord Bot.')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('----------')


@bot.command()
@commands.has_any_role('Admin', 'Raid Leader')
async def tweet(ctx, *, message):
    """
    This command is only @Admin usable and it will create a Tweet to the batphone Twitter account
    """
    status = twapi.post_tweet(message)
    await ctx.send(f"""```
I just fucking tweeted!
Status Update: {message}
```""")


@bot.command()
async def dkp(ctx, *filters):
    """
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
    seconds_remaining = config.SPAM_DELAY_IN_SECONDS - (datetime.now() - config.LAST_RUN).seconds
    if seconds_remaining > 0:
        await ctx.send(f"{random.choice(config.INSULTS)} [{seconds_remaining} seconds remaining...]")
    else:
        config.LAST_RUN = datetime.now()
        filters = parse_args(*filters)
        points = eqdkp.get_points(filters)
        chunks = [points[i:i + 10] for i in range(0, len(points), 10)]
        for chunk in chunks:
            await ctx.send(f"""```
{chunk}
```""")


def parse_args(*s):
    if s is None:
        return None
    filters = {}
    operators = ['=', ':', ';']
    comparisons = ['>', '<', '>=', '<=']
    value_splits = [',', '/']
    arg_pairs = [re.split(r'(\W)', arg_pair, maxsplit=1) for arg_pair in s]
    try:
        for arg_pair in arg_pairs:
            column = arg_pair[0].upper()
            if column not in (config.EQDKP_COLUMNS + config.ADDITIONAL_FILTERS):
                continue
            if arg_pair[1] not in operators and arg_pair[1] not in comparisons:
                raise SyntaxError(''.join(arg_pair))
            if arg_pair[1] in operators:
                value = re.split('|'.join(value_splits), arg_pair[2])
            else:
                value = ' '.join(arg_pair[1:])
            filters[column] = value
    except SyntaxError:
        pass
    finally:
        return filters


# Run the bot
bot.run(os.environ['BOT_TOKEN'])
