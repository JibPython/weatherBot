# Used to interact with Discord api
import discord
from discord.ext import commands
# retrieve token and api
from discord_token import DISCORD_TOKEN, WEATHER_API
# an asynchronous http library to retrieve weather information
# from 'OpenWeatherMap'
import aiohttp
# used for parsing
import json

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

    # Southampton Longitude cords
    soLon = -1.4043

    # Southampton Latitude cords
    soLat = 50.904

    weatherCall = f'https://api.openweathermap.org/data/2.5/weather?lat={soLat}&lon={soLon}&appid={WEATHER_API}'

    # making an HTTP call to 'OpenWeatherMap'
    async with aiohttp.ClientSession() as session:
        async with session.get(weatherCall) as resp:
            # receive the response as a json
            data = await resp.text()
            data = json.loads(data)

            # Creating dictionary from json
            weather_details = {
                'city': data["name"],
                'country': data["sys"]["country"],
                'description': data["weather"][0]["description"],
                'temperature': data["main"]["temp"],
                'wind speed': data["wind"]["speed"]
            }

            # Convert and format the temperature from Kelvin to Celsius
            weather_details['temperature'] = str(round(weather_details['temperature'] - 273.15, 2)) + '°C'

            weather_details['wind speed'] = str(weather_details['wind speed']) + 'm/s'

            # formatting an output message to discord
            output = ''
            for key in weather_details:
                if key == 'city':
                    output += ':cityscape:'
                elif key == 'country':
                    output += ':map:'
                elif key == 'description':
                    output += ':bookmark_tabs:'
                elif key == 'wind speed':
                    output += ':leaves:'
                else:
                    output += ':thermometer:'
                output += f' {key} : {weather_details[key]} \n'

            await context.send(output)

# Giving the bot access to the token
bot.run(DISCORD_TOKEN)