import configparser
import time
import sys
import traceback

from .vbot_commands import setup as main_commands_setup
from discord.utils import get

import helpers
import discord
from discord.ext import commands
#from .vbot_commands import ValorantBotCommands

config = configparser.ConfigParser()
config.read('config.ini')
fauxner = config['config']['OWNER_ROLE']


class AdminCommands(commands.Cog):
  def __init__(self, bot: commands.Bot, ):
    self.bot = bot
    self.conn = helpers.sqlite_create_connection('vbot.db')

  @commands.command(pass_context=True)
  @commands.has_role(fauxner)
  async def enablebot(self, client):
    epoch_time = str(int(time.time()))
    queue_id = helpers.sqlite_insert(self.conn, 'queues', str(epoch_time))
    print('hi hi hi hi hi hi!!!!!!!!!!!!!!!!!!')
    print(queue_id)
    print(helpers.sqlite_select(self.conn, 'queues', 'id', ' ORDER BY id DESC LIMIT 1'))
    main_commands_setup(self.bot)
    #self.bot.add_cog(ValorantBotCommands(self.bot))


    #previous_queue_id = helpers.sqlite_select(self.conn, 'queues', 'id', 'ORDER BY ID DESC LIMIT 1')


  @commands.command(pass_context=True)
  @commands.has_role(fauxner)
  async def disablebot(self, client):
    self.bot.remove_cog('ValorantBotCommands')

def setup(bot):
    bot.add_cog(AdminCommands(bot))
