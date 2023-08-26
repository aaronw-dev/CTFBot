import requests
import json
from datetime import datetime
import calendar
import discord
from discord import app_commands

intents = discord.Intents().all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

rssurl = "https://clients6.google.com/calendar/v3/calendars/ctftime@gmail.com/events?calendarId=ctftime%40gmail.com&singleEvents=true&timeZone=Africa%2FAbidjan&maxAttendees=1&maxResults=250&sanitizeHtml=true&timeMin=2023-07-31T00%3A00%3A00Z&timeMax=2023-09-04T00%3A00%3A00Z&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"
webhookurl = "https://discord.com/api/webhooks/1145053865599828000/qx5snul2GwFrSNz3-qvEupR-mGgKmrCr2L2U9rfstXarp_x2QaaioR1olmbuUqjkst9w"

@tree.command(name="getctf", description="Find upcoming CTFs")
#variable structure: VARIABLENAME: TYPE = DEFAULTVALUE
async def getctf(interaction):
    res = requests.get(rssurl)
    rescontent = res.content.decode('utf8')  # .replace("'", '"')

    responsejson = json.loads(rescontent)
    names = []
    finalmessage = '''
    > ## Here are some upcoming CTFs:
    '''
    for item in responsejson["items"]:
        names.append(item)
        eventTime = datetime.fromisoformat(item["start"]["dateTime"])
        finalmessage += "> *" + item["summary"] + "* on " + str(
            eventTime.day) + " " + calendar.month_name[eventTime.month] + " " + str(eventTime.year) + "\n"
    finalmessage += "\n"
    body = {
        "content": finalmessage
    }
    await interaction.response.send_message(body["content"], ephemeral=False)

@client.event
async def on_ready():
  await tree.sync()
  print("yes mom i'm awake")

with open("token.token", "r") as file:
    token = file.read()
client.run(token)