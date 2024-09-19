# Used to interact with Discord api
import discord
from discord.ext import commands
from discord_token import DISCORD_TOKEN

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

# prints message to terminal to show it's running
@bot.event
async def on_ready():
    # may need to handle connection to weather api
    print('logged in successfully')


# processing every message
@bot.event
async def on_message(message):
    # ignore messages received by the bot
    if message.author == bot.user:
        return

    if message.content.startswith('hi'):
        await message.channel.send('Hello!')

    # check to see if a command was called
    await bot.process_commands(message)


@bot.command()
# displays the current weather in Southampton
async def weatherNow(context):
    await context.send('Currently being worked on!')

# Giving the bot access to the token
bot.run(DISCORD_TOKEN)