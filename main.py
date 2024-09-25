from weatherAlerts import *


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
# informs the user how to use the /subscribe command
async def subscribeHelp(context):
    await context.send("enter the /subscribe command in this format for daily updates:\n"
                       "```/subscribe {CityName} {timeYouWantToBeAlerted}```")


# Giving the bot access to the token
bot.run(DISCORD_TOKEN)