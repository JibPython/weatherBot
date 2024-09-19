# Used to interact with Discord api
import discord
from discord_token import DISCORD_TOKEN

# AN INTENT ALLOWS THE BOT TO LISTEN TO
# SPECIFIC TYPE OF EVENTS

# giving the bot non-privileged intents
intents = discord.Intents.default()

# allowing it to read message contents
intents.message_content = True

# Creating a client with the specified intents
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # may need to handle connection to weather api
    print('logged in successfully')


@client.event
async def on_message(message):
    # ignore messages received by the bot
    if message.author == client.user:
        return

    if message.content.startswith('1'):
        await message.channel.send('Hello!')

# Giving the client access to the token
client.run(DISCORD_TOKEN)