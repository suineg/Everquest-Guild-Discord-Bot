import os
from datetime import datetime, timedelta

import pandas as pd
from discord.ext import commands

from cogs import dkp
from helpers import config, twapi

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


# TODO Learn how to separate commands into separate categories.
@bot.command()
@commands.has_any_role('Admin', 'Raid Leader')
async def tweet(ctx, *, message):
    """Send a tweet to the AmtrakEQ Twitter account. Required role: @Admin or @Raid Leader"""

    status = twapi.post_tweet(message)
    await ctx.send(f"""```
Here comes the train bitches!
Status Update: {message}
```""")
    discord_server = bot.get_guild(os.environ['DISCORD_GUILD_ID'])
    batphone_channel = discord_server.get_channel(os.environ['DISCORD_BATPHONE_CHANNEL_ID'])

    await batphone_channel.send(f"@everyone {message}")


bot.add_cog(dkp.DKP(bot))


# Run the bot
bot.run(os.environ['DISCORD_BOT_TOKEN'])
