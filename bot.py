import os
import traceback
from os import listdir
from os.path import isfile, join

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),
                   description='Amtrak EQ Discord Bot.')


# bot.remove_command('help')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('----------')
    bot.guild_id = int(os.getenv('DISCORD_GUILD_ID', 0))
    bot.batphone_id = int(os.getenv('DISCORD_BATPHONE_CHANNEL_ID', 0))
    bot.dkp_log_id = int(os.getenv('DISCORD_DKP_ENTRY_LOG_CHANNEL_ID', 0))
    await bot.change_presence(activity=discord.Game(name='with myself'))

# Here we load our extensions(cogs) that are located in the cogs directory. Any file in here attempts to load.
cogs_dir = 'cogs'
if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()


# Run the bot
bot.run(os.environ['DISCORD_BOT_TOKEN'])
