import configparser
import discord
from discord.utils import get

config = configparser.ConfigParser()
config.read('config.ini')
token = config['config']['TOKEN']
owner = config['config']['OWNER_ROLE']
vct1 = config['config']['T1_VOICE_CHANNEL_ID']
print(vct1)
vct2 = config['config']['T2_VOICE_CHANNEL_ID']
captain_role_name = config['config']['CAPTAIN_ROLE_NAME']

client = discord.Client()
client.data = {}
client.data['queued_users'] = []
client.queue_count = 0
client.t1_count = 0
client.t2_count = 0
client.which_pick = '1'

@client.event
#TODO: Add logic to alternate picks between captains.
async def on_message(message):
    player_list = []
    t1_captain = None
    t2_captain = None
    if message.author == client.user:
        return

    if get(message.author.roles, name=owner) and message.content.startswith('!captain'):
        print(message)
        target = (message.mentions[0])
        print(target)
        print(target.display_name)
        if any(player['username'] == str(target.display_name) for player in client.data['queued_users']):
          captain_role = get(message.guild.roles, name=captain_role_name)
          await target.add_roles(captain_role)
          if client.t1_count == 0:
            await target.edit(voice_channel=(client.get_channel(int(vct1))))
            for user in client.data['queued_users']:
              print('hihihi')
              print(user['username'])
              print(target.display_name)
              if user['username'] == str(target.display_name):
                user['team'] = '1'
                t1_captain = user['username']
                print('hi!')
                print(user['username'])
                print(user['team'])
                client.t1_count +=1
            msg = f'{target.display_name} chosen as Team 1 Captain! HF, you beautiful gamer. :)'
          else:
            await target.edit(voice_channel=(client.get_channel(int(vct2))))
            for user in client.data['queued_users']:
              print('hihihi')
              print(user['username'])
              print(target.display_name)
              if user['username'] == str(target.display_name):
                user['team'] = '2'
                t2_captain = user['username']
                print('hi!')
                print(user['username'])
                print(user['team'])
                client.t2_count +=1
            msg = f'{target.display_name} chosen as Team 2 Captain! GL, you need it.'
        else:
          msg = 'Invalid captain. Captain must be picked from Queued players.'
        await message.channel.send(msg)

    if get(message.author.roles, name=owner) and message.content.startswith('!reset'):
      client.data = {}
      client.data['queued_users'] = []
      client.queue_count = 0
      client.t1_count = 0
      client.which_pick = '1'
      in_channel = client.get_channel(int(vct1)).members + client.get_channel(int(vct2)).members
      for user in in_channel:
        await user.edit(voice_channel=None)

    if get(message.author.roles, name=captain_role_name) and message.content.startswith('!pick'):
      captain_data = list(filter(lambda captain: captain['username'] == message.author.display_name, client.data['queued_users']))
      if captain_data[0]['team'] == client.which_pick:
        team = None
        unpicked_users = list(filter(lambda player: player['team'] == '0', client.data['queued_users']))
        unpicked_usernames = []
        for user in unpicked_users:
          unpicked_usernames.append(user['username'])
        unpicked_formatted = """
  {}
  """.format("\n".join(unpicked_usernames[0:]))
        t1_users = list(filter(lambda player: player['team'] == '1', client.data['queued_users']))
        t1_usernames = []
        for user in t1_users:
          t1_usernames.append(user['username'])
        t1_users_formatted = """
  {}
  """.format("\n".join(t1_usernames[0:]))
        t2_users = list(filter(lambda player: player['team'] == '2', client.data['queued_users']))
        t2_usernames = []
        for user in t2_users:
          t2_usernames.append(user['username'])
        t2_users_formatted = """
  {}
  """.format("\n".join(t2_usernames[0:]))
        target = (message.mentions[0])
        if message.author.display_name == t1_captain:
          team = '1' 
        if message.author.display_name == t2_captain:
          team = '2'
            #captain_team_index = next((i for i, item in
            #enumerate(client.data['queued_users']) if item["team"] == "Pam"), None)

        if any(player['username'] == target.display_name for player in unpicked_users):
          await target.edit(voice_channel=(message.author.voice.channel))
          for user in client.data['queued_users']:
            if user['username'] == str(target.display_name):
              user['team'] = team
              if team == '1':
                t1_users.append(user)
                t1_usernames.append(user['username'])
                t1_users_formatted = """
  {}
  """.format("\n".join(t1_usernames[0:]))
              if team == '2':
                t2_users.append(user)
                t2_usernames.append(user['username'])
                t2_users_formatted = """
  {}
  """.format("\n".join(t2_usernames[0:]))
              unpicked_users.remove(user)
              unpicked_usernames.remove(user['username'])
              unpicked_formatted = """
  {}
  """.format("\n".join(unpicked_usernames[0:]))
          print(message.author.voice.channel)
          msg = f'{target.display_name} has been picked by {message.author}'
          if client.which_pick == '1':
            client.which_pick = '2'
          else:
            client.which_pick = '1'
        elif any(player['username'] == target.display_name for player in t1_users) or any(player['username'] == target.display_name for player in t2_users):
          msg = 'Invalid pick. Player is already on another team.'
        else:
          msg = 'Invalid pick. Player is not in queue.'
      else:
        msg = 'NO. Not your turn >:|'
      await message.channel.send(msg)
      pickembed = discord.Embed(title='Players:') 
      if unpicked_formatted.strip():
        pickembed.add_field(name='Unpicked:', value=str(unpicked_formatted), inline=False)
      if t1_users_formatted.strip():
        pickembed.add_field(name='Team 1:', value=t1_users_formatted, inline=True)
      if t2_users_formatted.strip():
        pickembed.add_field(name='Team 2:', value=t2_users_formatted, inline=True)
      await message.channel.send(embed=pickembed)
      captain_pick_msg = f'Captain {client.which_pick}s turn.'
      await message.channel.send(captain_pick_msg)

    if message.content.startswith('!queue') or message.content.startswith('!join'):
      if client.queue_count < 10:
        client.data['queued_users'].append({'username':
        message.author.display_name, 'user_id': message.author.id, 'team': '0'})
        client.queue_count +=1
        msg = 'You have joined the queue! Please enter a voice channel.'
        print(message.author.display_name)
        print(message.author.roles)
        await message.channel.send(msg)

    if message.content.startswith('!leave') and get(message.author.display_name) in client.data['queued_users']:
      client.queue_count -=1
      client.data['queued_users'].remove(get(message.author.display_name))
      msg = client.data['queued_users']
      await message.channel.send(msg)

    if message.content.startswith('!info') or message.content.startswith('!players'):
      for player in client.data['queued_users']:
        player_list.append(player['username'])
      unpicked_users = list(filter(lambda player: player['team'] == '0', client.data['queued_users']))
      unpicked_usernames = []
      for user in unpicked_users:
        unpicked_usernames.append(user['username'])
      unpicked_formatted = """
{}
""".format("\n".join(unpicked_usernames[0:]))
      t1_users = list(filter(lambda player: player['team'] == '1', client.data['queued_users']))
      t1_usernames = []
      for user in t1_users:
        t1_usernames.append(user['username'])
      t1_users_formatted = """
{}
""".format("\n".join(t1_usernames[0:]))
      t2_users = list(filter(lambda player: player['team'] == '2', client.data['queued_users']))
      t2_usernames = []
      for user in t2_users:
        t2_usernames.append(user['username'])
      t2_users_formatted = """
{}
""".format("\n".join(t2_usernames[0:]))
      embed = discord.Embed(title="Valorant Queue", description="Players in Queue:",
      color=3447003)
      print(t1_users)
      print(t1_usernames)
      print(t1_users_formatted)
      print(t2_users)
      print(t2_users_formatted)
      if client.data['queued_users']:
        if (unpicked_formatted.strip()):
          print(unpicked_users[0])
          embed.add_field(name="Waiting in Queue:", value=str(unpicked_formatted), inline=False)
        #if t1_users or t2_users:
        if (t1_users_formatted.strip()):
          print(t1_users)
          embed.add_field(name="Team 1:", value=str(t1_users_formatted), inline=True)
        if (t2_users_formatted.strip()):
          print(t2_users)
          embed.add_field(name="Team 2:", value=(t2_users_formatted), inline=True)
      else:
        embed.add_field(name='\u200b', value='Queue is currently empty', inline=True)
      await message.channel.send(embed=embed)



    if message.content.startswith('!help'):
      embed = discord.Embed(title='Valorant PUGbot Help', color=3447003)
      embed.add_field(name='Commands', value='''Join the queue: !queue/!join
      Leave the queue: !leave
      Display users queued: !players/!info
      Set Team captains (Owner only): !captains @user
      Reset pug queue and kick users from team voice (Owner only): !reset
      Pick player (Captains only): !Pick @user
      Display this message: !help''')
      await message.channel.send(embed=embed)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)

