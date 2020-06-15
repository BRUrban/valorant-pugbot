import configparser

from discord.utils import get

import helpers
import discord
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')
fauxner = config['config']['OWNER_ROLE']
captain_role_name = config['config']['CAPTAIN_ROLE_NAME']
vct1 = config['config']['T1_VOICE_CHANNEL_ID']
vct2 = config['config']['T2_VOICE_CHANNEL_ID']

###TODO: Clean up code more, test with larger number of users.
class ValorantBotCommands(commands.Cog, ):
  def __init__(self, bot: commands.Bot):
    self.conn = helpers.sqlite_create_connection('vbot.db')
    self.current_queue_id = helpers.sqlite_select(self.conn, 'queues', 'id', ' ORDER BY id DESC LIMIT 1')
    self.bot = bot
    self.which_pick = '1'
    self.t1_captain = None
    self.t2_captain = None

  # def is_queued(self):
  #   async def predicate(client):
  #     return client.author.display_name in self.data['queued_users']
  #   return commands.check(predicate)


  @commands.command(pass_context=True)
  @commands.has_role(fauxner)
  async def captain(self, client):
    target = (client.message.mentions[0])
    players_conditional = f' WHERE queue_id={self.current_queue_id[0]}'
    cc_conditional = f' WHERE queue_id={self.current_queue_id[0]} AND NOT is_captain=0'

    queued_users = helpers.sqlite_select(self.conn, 'queued_players', 'username', players_conditional)
    captain_count = helpers.sqlite_select(self.conn, 'queued_players', 'COUNT(*)', cc_conditional)
    print(captain_count[0])
    print('that was captain count!')

    if any(player == str(target.display_name) for player in queued_users):
      captain_role = get(client.guild.roles, name=captain_role_name)
      await target.add_roles(captain_role)

      if captain_count[0] == 0:
        await target.edit(voice_channel=(self.bot.get_channel(int(vct1))))
        for user in queued_users:
          if user == str(target.display_name):
            captain_1_conditional = f' WHERE queue_id={self.current_queue_id[0]} AND username="{target.display_name}"'
            helpers.sqlite_update(self.conn, 'queued_players', 'team_id =1, is_captain =1', captain_1_conditional)
        msg = f'{target.display_name} chosen as Team 1 Captain! HF, you beautiful gamer. :)'

      elif captain_count[0] == 1:
        await target.edit(voice_channel=(self.bot.get_channel(int(vct2))))
        for user in queued_users:
          if user == str(target.display_name):
            captain_2_conditional = f' WHERE queue_id={self.current_queue_id[0]} AND username="{target.display_name}"'
            helpers.sqlite_update(self.conn, 'queued_players', 'team_id = 2, is_captain = 1', captain_2_conditional)
        msg = f'{target.display_name} chosen as Team 2 Captain! GL, you need it.'

      else:
        msg = 'Too many captains, please reset or let your captains pick! monkaS'

    else:
      msg = 'Invalid captain. Captain must be picked from Queued players.'
    await client.send(msg)


  @commands.command()
  @commands.has_role(fauxner)
  async def reset(self, client):
    queued_players_conditional = f' WHERE queue_id={self.current_queue_id[0]}'
    self.which_pick = '1'
    in_channel = self.bot.get_channel(int(vct1)).members + self.bot.get_channel(int(vct2)).members

    helpers.sqlite_update(self.conn, 'queued_players', 'team_id = 0, is_captain = 0', queued_players_conditional)
    for user in in_channel:
      await user.edit(voice_channel=None)


  @commands.command()
  @commands.has_role(captain_role_name)
  async def pick(self, client):
    captains_conditionals = f' WHERE is_captain=1 AND queue_id={self.current_queue_id[0]}'
    unpicked_conditional = f' WHERE (queue_id={self.current_queue_id[0]} AND team_id=0)'
    t1_conditional = f' WHERE (queue_id={self.current_queue_id[0]} AND team_id=1)'
    t2_conditional = f' WHERE (queue_id={self.current_queue_id[0]} AND team_id=2)'

    captain_names = helpers.sqlite_select(self.conn, 'queued_players', 'username', captains_conditionals)
    captain_teams = helpers.sqlite_select(self.conn, 'queued_players', 'team_id', captains_conditionals)
    sql_unpicked_users = helpers.sqlite_select(self.conn, 'queued_players', 'username', unpicked_conditional)
    sql_t1_users = helpers.sqlite_select(self.conn, 'queued_players', 'username', t1_conditional)
    sql_t2_users = helpers.sqlite_select(self.conn, 'queued_players', 'username', t2_conditional)

    unpicked_users = helpers.filter_and_format_players('0', sql_unpicked_users)
    t1_users = helpers.filter_and_format_players('1', sql_t1_users)
    t2_users = helpers.filter_and_format_players('2', sql_t2_users)
    target = (client.message.mentions[0])
    if captain_teams:
      team = [captain_teams[cteam] for cteam in range(len(captain_teams)) if str(captain_teams[cteam]) == self.which_pick and client.message.author.display_name == captain_names[cteam]]

      if any(player['username'] == target.display_name for player in unpicked_users[1]):
        await target.edit(voice_channel=client.author.voice.channel)
        team_conditional = f' WHERE (queue_id={self.current_queue_id[0]} AND username={target.display_name} AND is_captain=0)'
        team_update = f'team_id={team}'
        helpers.sqlite_update(self.conn, 'queued_players', team_update, team_conditional)
        pick_msg = f'{target.display_name} has been picked by {client.message.author}'
        await client.channel.send(pick_msg)
        if self.which_pick == '1':
          self.which_pick = '2'
        else:
          self.which_pick = '1'
      elif any(player == target.display_name for player in t1_users[1]) or any(player == target.display_name for player in t2_users[1]):
        on_team_msg = 'Invalid pick. Player is already on another team.'
        await client.channel.send(on_team_msg)
      elif team == None:
        not_turn_msg = 'NO. Not your turn >:|'
        await client.channel.send(not_turn_msg)
      else:
        unqueued_err_msg = 'Invalid pick. Player is not in queue.'
        await client.channel.send(unqueued_err_msg)
      captain_pick_msg = f'Captain {self.which_pick}s turn.'
      await client.channel.send(captain_pick_msg)
    else:
      no_capt_msg = 'No captains in list. Captains must be assigned before picks can be made.'
      await client.channel.send(no_capt_msg)

    pick_embed = helpers.players_embed(self.conn)
    await client.channel.send(embed=pick_embed)



  @commands.command(aliases=['queue'])
  async def join(self, client):
    conditional = f' WHERE queue_id={self.current_queue_id[0]}'
    queue_count = helpers.sqlite_select(self.conn, 'queued_players', 'COUNT(id)', conditional)
    print('queue count!')
    print(queue_count)

    if helpers.sqlite_select(self.conn, 'queued_players', 'COUNT(id)', conditional)[0] < 10:
      helpers.sqlite_insert(self.conn, 'queued_players', f'{self.current_queue_id[0]}, "{client.message.author.display_name}", "0", 0')
      msg = 'You have joined the queue! Please enter a voice channel.'
      await client.send(msg)


  @commands.command()
  #@is_queued()
  async def leave(self, client):
    current_user_conditional = f' WHERE username="{client.message.author.display_name}"'

    helpers.sqlite_delete(self.conn, 'queued_players', current_user_conditional)
    msg = f'{client.message.author.display_name} has left the queue. :('
    await client.channel.send(msg)


  @commands.command(aliases=['valorant'])
  async def players(self, client):
    players_embed = helpers.players_embed(self.conn)
    await client.send(embed=players_embed)


  @commands.command()
  async def info(self, client):
    embed = discord.Embed(title='Valorant PUGbot Help', color=3447003)
    embed.add_field(name='Commands', value='''Join the queue: !queue/!join
    Leave the queue: !leave
    Display users queued: !players/!info
    Set Team captains (Owner only): !captains @user
    Reset pug queue and kick users from team voice (Owner only): !reset
    Pick player (Captains only): !Pick @user
    Display this message: !help''')
    await client.send(embed=embed)


def setup(bot):
    bot.add_cog(ValorantBotCommands(bot))