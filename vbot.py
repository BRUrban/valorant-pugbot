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

@client.event
async def on_message(message):
    player_list = []
    if message.author == client.user:
        return

    if get(message.author.roles, name=owner) and message.content.startswith('!captain'):
        print(message)
        target = (message.mentions[0])
        print(target)
        captain_role = get(message.guild.roles, name=captain_role_name)
        await target.add_roles(captain_role)
        await target.edit(voice_channel=(client.get_channel(int(vct1))))
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)

    if get(message.author.roles, name=owner) and message.content.startswith('!reset'):
      client.data = {}
      client.data['queued_users'] = []
      client.queue_count = 0
      in_channel = client.get_channel(int(vct1)).members + client.get_channel(int(vct2)).members
      for user in in_channel:
        await user.edit(voice_channel=None)

    if get(message.author.roles, name=captain_role_name) and message.content.startswith('!pick'):
      target = (message.mentions[0])
      await target.edit(voice_channel=(message.author.voice.channel))
      print(message.author.voice.channel)
      msg = f'{target} has been picked by {message.author}'
      await message.channel.send(msg)

    if message.content.startswith('!queue') or message.content.startswith('!join'):
      if client.queue_count < 10:
        client.data['queued_users'].append({'username':
        message.author.display_name, 'user_id': message.author.id})
        client.queue_count +=1
        msg = client.data['queued_users'][0]['username']
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
      embed = discord.Embed(title="Valorant Queue", description="Players in Queue:",
      color=3447003)
      embed.add_field(name="Players", value=player_list, inline=False)
      await message.channel.send(embed=embed)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(token)

