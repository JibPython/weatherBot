import discord
from discord.ext import commands

# AN INTENT ALLOWS THE BOT TO LISTEN TO
# SPECIFIC TYPE OF EVENTS

# giving the bot non-privileged intents
intents = discord.Intents.default()

# allowing it to read message contents
intents.message_content = True

# A 'commands.Bot' IS A SUBCLASS OF 'discord.client'
# WHICH ALLOWS YOU TO MANAGE COMMANDS AND IT INHERITS
# ALL OF ITS FUNCTIONALITIES

# Creating a bot with the specified intents
bot = commands.Bot(command_prefix='/', intents=intents)
