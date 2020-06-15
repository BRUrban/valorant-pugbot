import configparser
import sys
import traceback

import discord
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
token = config['config']['TOKEN']

bot = commands.Bot(command_prefix='!')
description = '''
    For Valorant pugs!
    Join the queue: !queue/!join
    Leave the queue: !leave
    Display users queued: !players/!info
    Set Team captains (Owner only): !captains @user
    Reset pug queue and kick users from team voice (Owner only): !reset
    Pick player (Captains only): !Pick @user
    Display this message: !help
    '''


def get_prefix(bot, message):
    prefixes = ['!']
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_cogs = ['cogs.admin_commands']
bot = commands.Bot(command_prefix=get_prefix, description=description)

if __name__ == '__main__':
    for cog in initial_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print(f'Failed to load {cog}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    if not hasattr(bot, 'appinfo'):
        bot.AppInfo = await bot.application_info()
    print(
        f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\nOwner: {bot.AppInfo.owner}')
    print(f'Successfully logged in and booted...!')


bot.run(token, bot=True, reconnect=True)