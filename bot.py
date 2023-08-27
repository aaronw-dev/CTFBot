import requests
import json
from datetime import datetime
import calendar
import discord
from discord import app_commands
import pytz
from dateutil.relativedelta import relativedelta
from math import *

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

with open("webhookurl.token", "r") as file:
    webhookurl = file.read()

@tree.command(name="getctf", description="Find upcoming CTFs")
#variable structure: VARIABLENAME: TYPE = DEFAULTVALUE
async def getctf(interaction, amount: app_commands.Range[int, 5, 20] = 10):
    maxresults = amount + 1
    timemin = datetime.now().strftime("%Y-%m-%d")
    timemax = (datetime.now() + relativedelta(years=1)).strftime("%Y-%m-%d")
    rssurl = f"https://clients6.google.com/calendar/v3/calendars/ctftime@gmail.com/events?calendarId=ctftime%40gmail.com&singleEvents=true&timeZone=Africa%2FAbidjan&maxAttendees=1&maxResults={maxresults}&sanitizeHtml=true&timeMin={timemin}T00%3A00%3A00Z&timeMax={timemax}T00%3A00%3A00Z&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
    res = requests.get(rssurl)
    
    rescontent = res.content.decode('utf8')  # .replace("'", '"')

    responsejson = json.loads(rescontent)
    with open("output.json", "w") as file:
        json.dump(responsejson, file, indent=4)
    finalmessage = '''
    > ## Here are some upcoming CTFs:
    '''
    upcomingevents = responsejson["items"]
    upcomingevents = sorted(upcomingevents, key=lambda x: x["start"]["dateTime"])
    names = []
    messagewidth = 60
    for item in upcomingevents:
        eventName = item["summary"]
        eventTime = datetime.fromisoformat(item["start"]["dateTime"])
        eventTimezone = item["start"]["timeZone"] #Format: UTC
        eventDuration = datetime.fromisoformat(item["end"]["dateTime"]) - datetime.fromisoformat(item["start"]["dateTime"])
        durationDays = eventDuration.days
        durationHours = floor(eventDuration.seconds / 3600)
        durationMinutes = floor(((eventDuration.seconds / 3600) - durationHours) * 60)
        durationSeconds = floor((((eventDuration.seconds / 3600) - durationHours) * 60 - durationMinutes) * 60)
        now = datetime.now()
        now = pytz.UTC.localize(now) 
        if(eventTime < now):
            continue
        eventLink = item["description"][-32:-2]
        names.append(item)
        finalmessage += "> " + "[" + item["summary"] + "](<" + eventLink + ">)" + " on " + "<t:" + str(calendar.timegm(eventTime.timetuple())) + ":D>"
        finalmessage += (" duration: " + str(durationHours) + " hour" + ("s" if durationHours != 1 else "") + " " + ((str(durationMinutes) + " minute" + ("s" if durationHours != 1 else "")) if durationMinutes != 0 else "")) if durationHours != 0 else "" 
        finalmessage += "\n"
    finalmessage += "\n"
    body = {
        "content": finalmessage
    }
    
    await interaction.response.send_message(body["content"], ephemeral=False)
'''
Code to post a webhook
requests.post(
    webhookurl,
    json=body)
'''
@client.event
async def on_message(message):
    if message.author.bot:
        return
    print(message.author.display_name + ": " + message.content)
    #await message.channel.send("balls")

@client.event
async def on_ready():
  await tree.sync()
  print("yes mom i'm awake")

with open("token.token", "r") as file:
    token = file.read()
client.run(token)