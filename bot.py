import requests #so we can get google calendar info
import json #provides functions to go from plain text to dicts and for logging
from datetime import datetime #stuff to find certain CTF events
import calendar #functions to find date names
import discord #stuff for discord bot
from discord import app_commands #allows discord commands
import pytz # for date localization
from dateutil.relativedelta import relativedelta #utility to get one full year forward of CTF events
from math import * #all math functions
from bs4 import BeautifulSoup

intents = discord.Intents().all() #we need all discord intents
client = discord.Client(intents=intents) #init a client with given intents
tree = app_commands.CommandTree(client) #for discord commands

with open("webhookurl.token", "r") as file:
    webhookurl = file.read() #get the webhook url from file

@tree.command(name="ctfinfo", description="Get more information about a CTF event")
async def ctfinfo(interaction, eventid: int):
    await interaction.response.send_message('Finding information about event with ID: ' + str(eventid) + "...", ephemeral=True)

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    websiteresponse = requests.get("https://ctftime.org/event/2003", headers=headers)
    websitehtml = websiteresponse.text
    soup = BeautifulSoup(websitehtml, "html.parser")
    pageheader = soup.find("div", {"class" : "page-header"}).find("h2")
    eventname = pageheader.get_text()
    teamamount = soup.find(lambda tag:tag.name=="p" and "teams total" in tag.text)
    teamamount = teamamount.get_text().split(" ")[0]
    teams = soup.find_all("tr")
    message = "# " + eventname + "\n"
    message += "## Teams (1-10 of " + teamamount + ")\n"
    for div in teams[1:11]:
        message += "`" + div.get_text().strip() + "`\n"
    await interaction.followup.send(message, ephemeral=False)


@tree.command(name="getctf", description="Find upcoming CTFs") #register a command into discord
#variable structure: VARIABLENAME: TYPE = DEFAULTVALUE
async def getctf(interaction, amount: app_commands.Range[int, 5, 20] = 10):
    maxresults = amount + 1 #maxresults needs value + 1 for some reason
    timemin = datetime.now().strftime("%Y-%m-%d") #timemin is the current datetime
    timemax = (datetime.now() + relativedelta(years=1)).strftime("%Y-%m-%d") #timemax is the current datetime + 1 year
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