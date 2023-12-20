import discord
from discord.ext import tasks
import re
import time
import asyncio
import os
#handle getting token & mod_role_name environment variables
if 'TOKEN' in os.environ and 'MODROLENAME' in os.environ:
    token = os.environ['TOKEN']
    mod_role_name = os.environ['MODROLENAME']
else:
    from config import token, mod_role_name
def votecount_str():
    output = 'Votecount: \n'
    if ourGame.possible_votes == []:
        return "Votecount requested without game start"
    for player in ourGame.possible_votes + ['no vote']:
        if isinstance(player, discord.Member):
            output += player.nick + " " + str(len(ourGame.votes[player])) + ": " + ', '.join([voter.nick for voter in ourGame.votes[player]]) + "\n"
        else:
            output += player + " " + str(len(ourGame.votes[player])) + ": " + ', '.join([voter.nick for voter in ourGame.votes[player]]) + "\n"
    return output
help_message = help_message = '''Commands:
These are all slash commands except /debug
Anyone can trigger (inside OR outside the game channel):
/votecount 
triggers a votecount
/debug 
prints some useful debugging information to the console
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
Player must have the mafia role name. Will record the vote if so. Can either use the player's nickname or their username
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
        await tree.sync()
        print(f'Mafia bot online as {self.user} (ID: {self.user.id})')
    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()
    async def on_message(self, message):
        if message.content == '/debug':
            print(ourGame)
            return
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
        await ourGame.game_channel.send(votecount_str())
ourGame = Game()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = MyClient(intents=intents)
tree = discord.app_commands.CommandTree(client)
@discord.app_commands.command()
async def vote(interaction: discord.Interaction, vote: str):
    #TODO: clean this part up
    if interaction.user in ourGame.player_list:
        if vote == 'no elimination' or vote in [i.name for i in ourGame.player_list]:
            for possible_vote in ourGame.possible_votes:
                if interaction.user in ourGame.votes[possible_vote]:
                    ourGame.votes.remove(interaction.user)
            user_voted_for = [i for i in ourGame.player_list if i.name == vote][0]
            await interaction.response.send_message('vote for ' + user_voted_for.nick + ' recorded')
            ourGame.votes[user_voted_for].append(interaction.user)
            if len(ourGame.votes[user_voted_for]) > len(ourGame.player_list)/2:
                await ourGame.game_channel.send("HAMMER")
                await client.end_day()
        elif vote in [i.nick for i in ourGame.player_list]:
            user_voted_for = [i for i in ourGame.player_list if i.nick == vote][0]
            await interaction.response.send_message('vote for ' + user_voted_for.nick + ' recorded')
            ourGame.votes[user_voted_for].append(interaction.user)
            if len(ourGame.votes[user_voted_for]) > len(ourGame.player_list)/2:
                await ourGame.game_channel.send("HAMMER")
                await client.end_day()
        elif int(vote[2:-1]) in [i.id for i in ourGame.player_list]:
            user_voted_for = [i for i in ourGame.player_list if i.id == int(vote[2:-1])][0]
            await interaction.response.send_message('vote for ' + user_voted_for.nick + ' recorded')
            ourGame.votes[user_voted_for].append(interaction.user)
            if len(ourGame.votes[user_voted_for]) > len(ourGame.player_list)/2:
                await ourGame.game_channel.send("HAMMER")
                await client.end_day()
        else:
            await interaction.response.send_message('invalid command')
    else:
        await interaction.response.send_message('invalid command')
tree.add_command(vote)
@discord.app_commands.command()
async def votecount(interaction: discord.Interaction):
    await interaction.response.send_message(votecount_str())
tree.add_command(votecount)
@discord.app_commands.command()
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(help_message)
tree.add_command(help)
@discord.app_commands.command()
async def daystart(interaction: discord.Interaction, player_role_name: str, length:float):
    #TODO: support pinging player role
    try:
        if mod_role_name in [role.name for role in interaction.user.roles]:
            roles = [role for role in interaction.guild.roles]
            player_role = [role for role in roles if role.name == player_role_name.strip()][0]
            members = await interaction.guild.chunk()
            player_list = [user for user in members if player_role.name in [role.name for role in user.roles]]
            #reset game
            ourGame.player_list = player_list
            ourGame.possible_votes = player_list + ['no elimination']
            ourGame.votes = {i : [] for i in ourGame.possible_votes}
            ourGame.votes['no vote'] = player_list
            ourGame.player_role = player_role
            ourGame.game_channel = interaction.channel
            ourGame.day_length = 60 * 60 * float(length)
            await interaction.channel.edit(overwrites = {player_role:discord.PermissionOverwrite(send_messages=True)})
            ourGame.day_start = time.time()
            await interaction.response.send_message("successfully started")
        else: 
            await interaction.response.send_message("not a mod")
    except:
        await interaction.response.send_message("error - probably incorrect command")
# Can also specify a guild here, but this example chooses not to.

tree.add_command(daystart)
client.run(token)
print('haha')