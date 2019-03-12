import os

from discord.ext import commands

from cogs import dkp, raids, misc

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'),
                   description='Amtrak EQ Discord Bot.')


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('----------')

bot.add_cog(dkp.DKP(bot))
bot.add_cog(raids.Raids(bot))
bot.add_cog(misc.Misc(bot))

# Run the bot
bot.run(os.environ['DISCORD_BOT_TOKEN'])
