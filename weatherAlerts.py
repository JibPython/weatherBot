from subscribe import *
from botInformation import WEATHER_CHANNEL_ID


# prints message to terminal to show it's running
@bot.event
async def on_ready():
    # need to handle retrieving the minimumCheckTime and update it
    # in case the bot has come online later and missed an alert time
    print('logged in successfully')
    print(getMinimumCheckTime())
    if getMinimumCheckTime() is not None:
        await waitTillNextAlert()


# returns the difference between two times in seconds,
# required for the 'waitTillNextAlert' function
def differenceBetweenTimes(time1, time2):
    # time2 will always be greater than time1 since the next
    # minimumCheckTime will always be greater than the current time
    timeOneHour = int(time1[0:2])
    timeOneMinutes = int(time1[3:])
    timeTwoHour = int(time2[0:2])
    timeTwoMinutes = int(time2[3:])

    hourDifference = timeTwoHour - timeOneHour
    minuteDifference = timeTwoMinutes - timeOneMinutes

    hoursToSeconds = hourDifference * 3600
    minutesToSeconds = minuteDifference * 60

    totalSeconds = hoursToSeconds + minutesToSeconds

    return totalSeconds


async def waitTillNextAlert():
    while True:
        currentTime = await getCurrentTimeUTC()
        updateMinimumCheckTime(currentTime)

        # need to find a difference between the current time and the
        # minimumCheckTime and convert it to seconds to synchronize the
        # weather alert with the alertTimeUtc
        minimumCheckTime = getMinimumCheckTime()

        if comparingTimes(currentTime, minimumCheckTime) == "draw":
            # the program does not need to wait to send an alert notification
            print("it is the same time2")
            await sendAlerts(minimumCheckTime)
            await asyncio.sleep(60)
        else:
            waitSeconds = differenceBetweenTimes(currentTime, minimumCheckTime)
            # possible for the waitSeconds to be negative since the current time
            # could be greater than the next alert time, if the alert is the next
            # morning for example
            if waitSeconds > 0:
                print(f'{waitSeconds} seconds till next alert')
                # wait till the currentTime is equal to the minimumCheckTime
                await asyncio.sleep(waitSeconds)
                await sendAlerts(minimumCheckTime)
                print("it is the same time")
            await asyncio.sleep(60)


# This function handles when a user needs to be notified about their weather information
async def sendAlerts(minimumCheckTime):

    # create a list of people who need to be sent a weather alert now

    with open('storage.json', 'r') as file:
        storage = json.load(file)

    allAlerts = storage["users"]

    # there could be multiple people who need to be alerted
    notifyNow = []

    for alert in allAlerts:
        if comparingTimes(alert["alertTimeUtc"], minimumCheckTime) == "draw":
            notifyNow.append(alert)

    for alert in notifyNow:
        city, userId = alert["city"], alert["userId"]

        await dmAlerts(city, userId)


# now that we have the list of cities and userId's we can now dm the user the weather information
async def dmAlerts(city, userId):
    # Creating a User instance of the member who is going to receive the weather information
    channel = bot.get_channel(WEATHER_CHANNEL_ID)
    # await channel.send(f"<@{userId}>")

    print(type(channel))

    await weatherNowAt(channel, city, userId)


@bot.command()
# displays the current weather of any city around the world
async def weatherNowAt(context, city: str = None, userId: int = None):
    print(context)
    # 'city' will have a default type of None, so we can send a message back to the user to tell
    # them to enter a city name which will make the type a String
    if isinstance(context, discord.channel.TextChannel):
        weatherCall = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'

        await formatResponse(context, weatherCall, userId)
    else:
        if city is None:
            await context.send(':x: Did not enter a city name!')
        else:
            weatherCall = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'

            # calling the function to format the JSON response
            await formatResponse(context, weatherCall)


async def formatResponse(context, weatherCall, userId: int = None):
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
                if isinstance(context, discord.channel.TextChannel):
                    output = f'<@{userId}> this is the weather information for {str(datetime.datetime.now())[11:16]}:\n'
                else:
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