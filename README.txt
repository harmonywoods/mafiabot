A simple bot for helping manage mafia games on discord.

Configuration information:
The dependencies for this are python 3.12+ (it may work with older versions, not sure) and the python library discord.py (information at https://discordpy.readthedocs.io) which wraps the discord API
To set up, go to your developer portal, set up a new application, get your token and mod role name for config.py.
Put your API token and mod_role_name values in config.py - for instance:
token = 'token here'
mod_role_name = 'mod role name here'
Alternatively, you can set environment variables (if you're using something like Docker). In this case, set the environment variables TOKEN and MODROLENAME to the appropriate values
Generate an invite link by going OAuth2 -> URL Generator, select bot and then select:
Send messages
Manage channels
Manage roles
View channels
Use Slash Commands
and copy the link @ the bottom
Invite the bot to the server you want it to run games on, and then run the script. 
Commands:
Anyone can trigger (inside OR outside the game channel):
/votecount triggers a votecount
/debug prints some useful debugging information to the console
Only people with a role who's name matches the mod role name can trigger:
/startday [player role name],[time]
Time is provided in hours (decimal amounts are supported)
Player role name is the name of the role you wish to use
e.g. 
/startday mafia player,24
Only people with the mafia player role can trigger:
/vote [player]
Player must have the mafia role name. Will record the vote if so
/help 
Gives this list of commands 

For further questions contact the administrator of the instance, should be listed in the bot's about me

