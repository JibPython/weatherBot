# Used to interact with Discord api
import discord
from discord.ext import commands
# retrieve token and api
from bot_information import DISCORD_TOKEN, WEATHER_API
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

    city = 'southampton'

    weatherCall = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'

    # calling the function to format the JSON response
    await formatResponse(context, weatherCall)


@bot.command()
# displays the current weather of any city around the world
async def weatherNowAt(context, city: str = None):

    # 'city' will have a default type of None, so we can send a message back to the user to tell
    # them to enter a city name which will make the type a String
    if city is None:
        await context.send(':x: Did not enter a city name!')
    else:
        weatherCall = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'

        # calling the function to format the JSON response
        await formatResponse(context, weatherCall)


async def formatResponse(context, weatherCall):
    # making an HTTP call to 'OpenWeatherMap'
    async with aiohttp.ClientSession() as session:
        async with session.get(weatherCall) as resp:
            # receive the response as a json
            data = await resp.text()
            data = json.loads(data)

            # Creating dictionary from json
            try:
                weatherDetails = {
                    'city': data["name"],
                    'country': data["sys"]["country"],
                    'description': data["weather"][0]["description"],
                    'temperature': data["main"]["temp"],
                    'wind speed': data["wind"]["speed"]
                }

                # Convert and format the temperature from Kelvin to Celsius
                weatherDetails['temperature'] = str(round(weatherDetails['temperature'] - 273.15, 2)) + '°C'

                weatherDetails['wind speed'] = str(weatherDetails['wind speed']) + 'm/s'

                # formatting an output message to discord
                output = ''
                for key in weatherDetails:
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
                    output += f' {key} : {weatherDetails[key]} \n'

                # sends the output to discord chat
                await context.send(output)

            # missing keys in dictionary from incorrect city name or website is unable to send a
            # successful response
            except KeyError:
                await context.send(":x: Unable to find city weather details!")




# Giving the bot access to the token
bot.run(DISCORD_TOKEN)