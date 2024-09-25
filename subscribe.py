from intents import *
# retrieve token and api
from botInformation import WEATHER_API, BOT_CITY, DISCORD_TOKEN
# Used to sort the alert times to find the minimumCheckTime
from algorithm import MergeSort
# used for parsing
import json
# used for rounding down for time conversion to utc
import math
# Required to not send an alert till the current time is equal
# to the alertTimeUtc
import asyncio
# an asynchronous http library to retrieve weather information
# from 'OpenWeatherMap'
import aiohttp
# used to get the current time
import datetime


@bot.command()
# allows user to get weather updates daily at a set time
async def subscribe(context, city: str = None,  alertTime: str = None):
    # NOTE: 'alertTime' is based on their local time zone

    if city is None and alertTime is None:
        await context.send(":x: You did not enter a city or alert time! :x:\n"
                           "refer to **/subscribeHelp** for further information")
    # There is no need to add a condition for no city value since the user is either
    # going to input none of the required arguments or he is going to put one, the
    # 'city' value. Thus, both scenarios have been accounted for.
    elif alertTime is None:
        await context.send(":x: You did not enter an alert time! :x:\n"
                           "refer to **/subscribeHelp** for further information")
    else:

        # the storage json file has a key called 'firstTime' since the storage is
        # persistent and the bot is not (it will lose information once it restarts e.g.),
        # this is important, so we can set the value of minimumCheck to None when the
        # storage has not been updated before

        # the time zone offset from local time to utc, required for time conversion
        timeZoneOffset = await getTimeZone(city)

        # escaping function if we cannot determine
        # timezone value
        if not timeZoneOffset:
            await context.send(":x: Unable to find city timezone!")
            return

        userId = getMemberId(context)

        username = getMemberName(context)

        alertTimeUtc = getUtcTime(alertTime, timeZoneOffset)

        # creating dictionary to add to the storage.json
        userInformation = {
            'userId': userId,
            'username': username,
            'city': city,
            'alertTimeUtc': alertTimeUtc,
            'timeZoneOffset': timeZoneOffset
        }

        # check to see if the alert exists already, do not want any duplicate alerts
        exists = checkAlertExists(userId, city, alertTimeUtc)

        if exists:
            await context.send(':x: You cannot duplicate alerts! :x:')
            return

        addUserInformation(userInformation)

        currentTime = await getCurrentTimeUTC()

        updateMinimumCheckTime(currentTime)


# returning value required to convert local time to UTC time for local storage
async def getTimeZone(city):

    weatherCall = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}'

    # making an HTTP call to 'OpenWeatherMap'
    async with aiohttp.ClientSession() as session:
        async with session.get(weatherCall) as resp:
            # receive the response as a json
            data = await resp.text()
            data = json.loads(data)

            try:
                # returning timezone value used to convert local time to UTC
                return data["timezone"]

            except KeyError:
                # we can use the None value to stop the subscription process if the
                # timezone value cannot be found
                return False


# finding the Member ID and name to store in the json file
def getMemberId(context):
    return context.message.author.id


def getMemberName(context):
    return context.message.author.name


# converts local time to utc so that the storage.json stores time in one
# universal time zone
def getUtcTime(localTime, timeZoneOffset):
    # 'localTimeAhead' determines the operation sign
    localTimeAhead = True
    if str(timeZoneOffset)[0] == '-':
        localTimeAhead = False
        timeZoneOffset = int(str(timeZoneOffset)[1:])

    # 'timeZoneOffset' is measured in seconds, thus we can convert it to minutes and hours
    timeZoneOffsetHours = math.floor(timeZoneOffset / 3600)
    timeZoneOffsetMinutes = int((timeZoneOffset - (timeZoneOffsetHours*3600)) / 60)

    # slice the 'localTime' to extract the hours
    localTimeHours = localTime[0:2]
    localTimeMinutes = localTime[3:6]

    # if the local time is ahead, you have to subtract the time zone conversion
    # to make it equal to utc
    if localTimeAhead:
        newHours = (int(localTimeHours) - int(timeZoneOffsetHours)) % 24
        newMinutes = (int(localTimeMinutes) - int(timeZoneOffsetMinutes)) % 60
    else:
        newHours = (int(localTimeHours) + int(timeZoneOffsetHours)) % 24
        newMinutes = (int(localTimeMinutes) + int(timeZoneOffsetMinutes)) % 60

    # ensuring that if hours or minutes is a single digit there is a 0 as a prefix
    # to maintain the military format
    if newHours < 10:
        newHours = '0' + str(newHours)

    if newMinutes < 10:
        newMinutes = '0' + str(newMinutes)

    utcTime = f'{newHours}:{newMinutes}'
    return utcTime


# come back to later
def checkAlertExists(userId, city, alertTimeUtc):
    with open('storage.json', 'r') as file:
        storage = json.load(file)

    # getting 'users' values
    userAlerts = storage["users"]

    # returning True if the alert with the same userId, city and alertTimeUtc exists already
    for dict in userAlerts:
        if dict["userId"] == userId and dict["city"] == city and dict["alertTimeUtc"] == alertTimeUtc:
            return True
    else:
        return False


# adding user alert details to storage.json
def addUserInformation(userInformation):
    # reading storage.json
    with open('storage.json', 'r') as file:
        storage = json.load(file)

    # adding the new user alert details to the previous
    # stored values in the storage.json file
    values = storage["users"]
    values.append(userInformation)
    storage["users"] = values

    # updating 'minimumCheckTime' if this is the first
    # alert added
    if storage["minimumCheckTime"] is None:
        storage["minimumCheckTime"] = userInformation["alertTimeUtc"]

    # updating the storage.json file
    with open('storage.json', 'w') as file:
        json.dump(storage, file, indent=4)


# used to retrieve minimumCheckTime value
def getMinimumCheckTime():
    with open('storage.json', 'r') as file:
        storage = json.load(file)

    return storage["minimumCheckTime"]


# required to get the current time to calculate 'minimumCheckTime' value
# so the bot knows what time the next upcoming alert is
async def getCurrentTimeUTC():
    # this is the current time in the local time zone
    # this value needs to be converted to utc
    currentTimeLocal = str(datetime.datetime.now())

    # 'BOT_CITY' is a string literal where it is equal to the city name
    # where the bot is being run from
    botTimeZoneOffset = await getTimeZone(BOT_CITY)

    # had to get the substring of 'currentTimeLocal' to remove the current date along
    # with the seconds and milliseconds
    currentTimeUtc = getUtcTime(currentTimeLocal[11:16], botTimeZoneOffset)

    return currentTimeUtc


# used to calculate the minimumCheckTime and update the storage.json file
def updateMinimumCheckTime(currentTime):
    with open('storage.json', 'r') as file:
        storage = json.load(file)

    times = []
    users = storage["users"]

    # making an unsorted list of alert times
    for user in users:
        times.append(user["alertTimeUtc"])

    minimumCheckTime = None
    # the minimumCheckTime is set to None in case there is no
    # alerts saved in storage.json
    if times:

        # sort times in sequential order
        timesSorted = MergeSort(times).sort()
        # for debugging purposes
        print(timesSorted)
        for index in range(len(timesSorted)):
            # if the first alertTime is greater than the current time then that
            # will be the minimumCheckTime
            if index == 0:
               if comparingTimes(timesSorted[index], currentTime) == "time1":
                    minimumCheckTime = timesSorted[0]
                    break
            # if the current time is equal to one of the alert times then an alert
            # needs to be made straight away
            if comparingTimes(timesSorted[index], currentTime) == "draw":
                minimumCheckTime = currentTime
                break
            # if it is the last element in the sorted time alerts and it is not
            if index == len(timesSorted) - 1:
                # if the current time is later than the last alert, then the next
                # alert will be the first alert on the following day
                if comparingTimes(timesSorted[index], currentTime) == "time2":
                    minimumCheckTime = timesSorted[0]
                    break
                else:
                    # if the last alert time is later than the current time then that
                    # will be the next alert time
                    minimumCheckTime = timesSorted[index]
                    break
            # if the current time is greater than the previous alert time, but it is not greater than
            # the upcoming alert, then the minimumCheckTime will be the upcoming alert time
            if comparingTimes(timesSorted[index], currentTime) == "time2" and comparingTimes(timesSorted[index+1], currentTime) == "time1":
                minimumCheckTime = timesSorted[index + 1]
                break

    # need to update the minimumCheckTime in storage.json
    storage["minimumCheckTime"] = minimumCheckTime

    with open('storage.json', 'w') as file:
        json.dump(storage, file, indent=4)

    # to make sure that the feature is working as expected
    print(f'the current time is: {currentTime}')
    print(f'the minimum check time is {minimumCheckTime}')


# used to compare the times stored in storage.json and the current time
# to determine which time is greater than the other
def comparingTimes(time1, time2):
    timeOneHour = int(time1[0:2])
    timeOneMinutes = int(time1[3:])
    timeTwoHour = int(time2[0:2])
    timeTwoMinutes = int(time2[3:])
    # Compare hour to see if there is an immediate difference
    if timeOneHour > timeTwoHour:
        return "time1"
    elif timeTwoHour > timeOneHour:
        return "time2"
    elif timeOneHour == timeTwoHour:
        # Compare minutes to see deduce which one is greater
        if timeTwoMinutes > timeOneMinutes:
            return "time2"
        elif timeOneMinutes > timeTwoMinutes:
            return "time1"
        else:
            return "draw"