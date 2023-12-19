#TODO: test, write up, let deadline be set in daystart
import discord
from discord.ext import tasks
import re
from config import token, mod_role_name
import time
def votecount():
    output = 'Votecount: \n'
    if ourGame.possible_votes == []:
        raise Exception("Votecount requested without game start")
    for player in ourGame.possible_votes:
        output += player + " " + str(len(ourGame.votes[player])) + ": " + ', '.join(ourGame.votes[player]) + "\n"
    return output
help_message = help_message = '''Commands:
Anyone can trigger (inside OR outside the game channel):
/votecount triggers a votecount
/debug prints some useful debugging information to the console
/help 
Gives this list of commands 
Only people with a role who's name matches the mod role name can trigger:
/startday [player role name],[time]
Time is provided in hours (decimal amounts are supported)
Player role name is the name of the role you wish to use
e.g. 
/startday mafia player,24
Only people with the mafia player role (assigned by a moderator) can trigger:
/vote [player]
Player must have the mafia role name. Will record the vote if so
e.g.
/vote harmony
For further questions contact the administrator of the instance, should be listed in the bot's about me'''

class Game:
    def __init__(self):
        self.player_list = []
        self.possible_votes = []
        self.votes = {}
        self.player_role = None
        self.day_start = None
        self.game_channel = None
        self.day_length = None
    def __repr__(self):
        return ','.join(self.player_list) + '|' + ','.join(self.possible_votes) + ','.join(self.votes)
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Mafia bot online as {self.user} (ID: {self.user.id})')
    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()
    async def on_message(self, message):
        # don't respond to ourselves
        try:
            if message.author == self.user:
                return; # dont think this is necessary
            if message.content == '/debug':
                print(ourGame)
                return
            if message.content == '/help':
                await message.reply(help_message, mention_author=True)
            if message.content == '/votecount':
                await message.reply(votecount(), mention_author=True)
                return
            if message.content[:5] == '/vote':
                vote = message.content[6:]
                if vote in ourGame.possible_votes and message.author.nick in ourGame.player_list:
                    await message.reply('vote for ' + vote + ' recorded', mention_author = True)
                    ourGame.votes[vote].append(message.author.nick)
                    if len(ourGame.votes[vote]) > len(ourGame.player_list)/2:
                        #HAMMER
                        await message.reply('HAMMER')
                        await self.end_day()
                else:
                    await message.reply('invalid vote', mention_author = True)
                return
            if message.content[:9] == '/startday':
                if mod_role_name in [role.name for role in message.author.roles]:
                    setup = message.content[10:].split(',')
                    player_role = [role for role in message.guild.roles if role.name == setup[0]][0]
                    members = await message.guild.chunk()
                    player_list = [user.nick for user in members if player_role.name in [role.name for role in user.roles]]
                    #reset game
                    ourGame.player_list = player_list
                    ourGame.possible_votes = player_list + ['no elimination']
                    ourGame.votes = {i : [] for i in ourGame.possible_votes}
                    ourGame.votes['no vote'] = player_list
                    ourGame.player_role = player_role
                    ourGame.game_channel = message.channel
                    ourGame.day_length = 60 * 60 * float(setup[1])
                    print(ourGame.day_length)
                    await message.channel.edit(overwrites = {player_role:discord.PermissionOverwrite(send_messages=True)})
                    ourGame.day_start = time.time()
                    await message.reply("successfully started", mention_author = True)
                else: 
                    await message.reply("not a mod", mention_author = True)
        except Exception as e:
            await message.reply("error - probably incorrect command")
            print(e)
    @tasks.loop(seconds=30)  # task runs every 30 seconds
    async def my_background_task(self):
        if ourGame.day_start:
            if time.time() - ourGame.day_start > ourGame.day_length:
                await self.end_day()
    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in
    async def end_day(self):
        await ourGame.game_channel.send("EOD")
        ourGame.day_start = None
        await ourGame.game_channel.edit(overwrites = {ourGame.player_role:discord.PermissionOverwrite(send_messages=False)})
        await ourGame.game_channel.send(votecount())
ourGame = Game()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = MyClient(intents=intents)
client.run(token)
print('haha')