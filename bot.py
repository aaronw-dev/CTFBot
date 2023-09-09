import requests  # so we can get google calendar info
import json  # provides functions to go from plain text to dicts and for logging
from datetime import datetime  # stuff to find certain CTF events
import calendar  # functions to find date names
import discord  # stuff for discord bot
from discord import app_commands  # allows discord commands
import pytz  # for date localization

# utility to get one full year forward of CTF events
from dateutil.relativedelta import relativedelta
from math import *  # all math functions
from bs4 import BeautifulSoup

intents = discord.Intents().all()  # we need all discord intents
client = discord.Client(intents=intents)  # init a client with given intents
tree = app_commands.CommandTree(client)  # for discord commands

whitelist = [937168534830719008, 719678705613537361]


"""@tree.command(name="ctfinfo", description="Get more information about a CTF event")
async def ctfinfo(interaction, eventid: int):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    websiteresponse = requests.get(
        "https://ctftime.org/event/" + str(eventid), headers=headers
    )
    websitehtml = websiteresponse.text

    websitehtml = websitehtml.replace("<br />", "\n").replace("<b>", "### ")

    soup = BeautifulSoup(websitehtml, "html5lib")
    pageheader = soup.find("div", {"class": "page-header"}).find("h2")
    eventname = pageheader.get_text()
    teamamount = soup.find(lambda tag: tag.name == "p" and "teams total" in tag.text)
    teamamount = teamamount.get_text().split(" ")[0]

    teams = []
    for div in soup.find_all("tr")[1:11]:
        linkdiv = div.find("a", href=True)
        teams.append(
            {
                "name": linkdiv.get_text().strip(),
                "link": "https://ctftime.org" + linkdiv["href"],
            }
        )
    informationbox = soup.find("div", {"class": "span10"})
    informationboxes = informationbox.findChildren("p", recursive=False)
    eventformat = informationboxes[4].get_text().replace("Format: ", "")
    eventurl = informationboxes[5].get_text().replace("Official URL: ", "")
    eventlocation = informationboxes[1].get_text().replace("### ", "")
    message = "> # [" + eventname + "](<" + eventurl + ">)" + "\n"
    message += "> ## Event ID: `" + str(eventid) + "`\n"
    message += "> ## Format: " + eventformat + "\n"
    message += "> ## Location: " + eventlocation.replace("On-line", "Online") + "\n"
    message += "> ## Teams: " + teamamount + "\n"
    message += "> ## Description \n> "
    message += (
        soup.find("div", {"id": "id_description"})
        .get_text()
        .strip()
        .replace("\n", "\n> ")
        + "\n"
    )
    # for div in teams[1:11]:
    # linkdiv = div.find("a", href=True)
    # message += "> 🔹 [" + linkdiv.get_text().strip() + "](<https://ctftime.org" + linkdiv["href"] + ">)" + "\n"

    await interaction.response.send_message(message, ephemeral=False)

"""


@tree.command(name="upcoming", description="Get the next 7 days of CTF events")
async def upcoming(interaction):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36"
        "(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }

    # get the utc time now in unix epoch time
    now = datetime.utcnow().timestamp()

    # get the utc time + 5 days in unix epoch time
    seven_days = datetime.utcnow() + relativedelta(days=+7)
    seven_days = seven_days.timestamp()

    r = requests.get(
        "https://ctftime.org/api/v1/events/?limit=100"
        + "&start="
        + str(int(now))
        + "&finish="
        + str(int(seven_days)),
        headers=headers,
    )

    data = r.json()

    # create embed with title and description
    embed = discord.Embed(
        title="Upcoming CTF Events",
        description="Here are the upcoming CTF events in the next 7 days.",
        type="article",
    )

    # loop through all events
    for event in data:
        # get the event title
        event_title = event["title"]

        # get the event url
        event_url = event["url"]

        # get the event start time
        event_start = event["start"]

        event_id = event["id"]

        # convert start time to unix timestamp in unix epoch time
        event_start = datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S%z")
        event_start = event_start.timestamp()

        # add a field to the embed
        embed.add_field(
            name=event_title,
            value=event_url,
            inline=True,
        )

        # add id field to embed
        embed.add_field(
            name="Event ID",
            value=event_id,
            inline=True,
        )

        # add a field to the embed
        embed.add_field(
            name="Start Date",
            value="<t:" + str(int(event_start)) + ":f>",
            inline=True,
        )

    # send embed
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="more_info",
    description="Get more information about a specific CTF by CTF Time ID",
)
async def ctfinfo(interaction, eventid: int):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    r = requests.get(
        "https://ctftime.org/api/v1/events/" + str(eventid) + "/", headers=headers
    )

    # get json data from api call
    data = r.json()
    event_title = data["title"]
    event_url = data["url"]
    event_start = data["start"]
    event_end = data["finish"]
    event_description = data["description"]

    # get the event image url
    event_image = data["logo"]

    # convert start time to unix timestamp in unix epoch time
    event_start = datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S%z")
    event_start = event_start.timestamp()

    # convert end time to unix timestamp in unix epoch time
    event_end = datetime.strptime(event_end, "%Y-%m-%dT%H:%M:%S%z")
    event_end = event_end.timestamp()

    # create embed
    embed = discord.Embed(
        title=event_title,
        url=event_url,
        description=event_description,
        type="article",
    )

    # Add tumbnail to embed
    embed.set_thumbnail(url=event_image)

    embed.add_field(
        name="Start Date",
        value="<t:" + str(int(event_start)) + ":d>",
        inline=True,
    )

    embed.add_field(
        name="End Date",
        value="<t:" + str(int(event_end)) + ":d>",
        inline=True,
    )

    # new line
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # Add a non-relative start time for the event
    embed.add_field(
        name="Start Time",
        value="<t:" + str(int(event_start)) + ":t>",
        inline=True,
    )

    embed.add_field(
        name="End Time",
        value="<t:" + str(int(event_end)) + ":t>",
        inline=True,
    )

    # new line
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    # add fields to embed
    embed.add_field(
        name="When?",
        value="<t:" + str(int(event_start)) + ":R>",
        inline=False,
    )

    # send embed
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="ctfparticipants",
    description="Get a list of people participating in a CTF event.",
)
async def ctfparticipants(interaction, eventid: int):
    with open("votes.json", "r") as file:
        votes = json.load(file)
    message = (
        "> # ["
        + votes[str(eventid)]["name"]
        + "](<"
        + votes[str(eventid)]["url"]
        + ">)\n"
    )
    message += "> ## Participants:\n"
    for participant in votes[str(eventid)]["participants"]:
        message += (
            "> **"
            + participant["displayname"]
            + "** ("
            + participant["username"]
            + ")\n"
        )
    await interaction.response.send_message(message)


@tree.command(name="ctfpoll", description="Start a poll for CTF participation.")
async def ctfpoll(interaction, eventid: int):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    websiteresponse = requests.get(
        "https://ctftime.org/event/" + str(eventid), headers=headers
    )
    websitehtml = websiteresponse.text
    websitehtml = websitehtml.replace("<br />", "\n").replace("<b>", "### ")

    soup = BeautifulSoup(websitehtml, "html5lib")
    pageheader = soup.find("div", {"class": "page-header"}).find("h2")
    eventname = pageheader.get_text()
    teamamount = soup.find(lambda tag: tag.name == "p" and "teams total" in tag.text)
    teamamount = teamamount.get_text().split(" ")[0]
    teams = []
    for div in soup.find_all("tr")[1:11]:
        linkdiv = div.find("a", href=True)
        teams.append(
            {
                "name": linkdiv.get_text().strip(),
                "link": "https://ctftime.org" + linkdiv["href"],
            }
        )
    informationbox = soup.find("div", {"class": "span10"})
    informationboxes = informationbox.findChildren("p", recursive=False)
    eventformat = informationboxes[4].get_text().replace("Format: ", "")
    eventurl = informationboxes[5].get_text().replace("Official URL: ", "")
    eventlocation = informationboxes[1].get_text().replace("### ", "")

    message = "> # [" + eventname + "](<" + eventurl + ">)" + "\n"
    message += "> ## Event ID: `" + str(eventid) + "`\n"
    message += "> ## Format: " + eventformat + "\n"
    message += "> ## Link: " + eventurl
    await interaction.response.send_message("Starting poll...", ephemeral=True)

    infomessage = await interaction.channel.send(message)
    await infomessage.add_reaction("<:yes:1148772032302039121>")
    await infomessage.add_reaction("<:no:1148772028216778792>")

    with open("votes.json", "r") as file:
        votes = json.load(file)
    if str(eventid) not in votes:
        votes[str(eventid)] = {
            "poll_id": infomessage.id,
            "url": "",
            "votesyes": 0,
            "votesno": 0,
            "participants": [],
        }
    with open("votes.json", "w") as file:
        json.dump(votes, file, indent=4)


@client.event
async def on_raw_reaction_add(payload):
    with open("votes.json", "r") as file:
        votes = json.load(file)

    valueindex = 0
    for value in votes.values():
        if payload.message_id == value["poll_id"]:
            eventid = list(votes)[valueindex]
            if payload.emoji.is_custom_emoji():
                if payload.emoji.id == 1148772032302039121:  # yes emoji
                    votes[eventid]["votesyes"] += 1
                    member = await client.fetch_user(payload.user_id)
                    votes[eventid]["participants"].append(
                        {
                            "id": member.id,
                            "username": member.name,
                            "displayname": member.display_name,
                        }
                    )
                if payload.emoji.id == 1148772028216778792:  # no emoji
                    votes[eventid]["votesno"] += 1
        valueindex += 1
    with open("votes.json", "w") as file:
        json.dump(votes, file, indent=4)


@client.event
async def on_raw_reaction_remove(payload):
    with open("votes.json", "r") as file:
        votes = json.load(file)

    valueindex = 0
    for value in votes.values():
        if payload.message_id == value["poll_id"]:
            eventid = list(votes)[valueindex]
            member = await client.fetch_user(payload.user_id)
            if payload.emoji.is_custom_emoji():
                if payload.emoji.id == 1148772032302039121:  # yes emoji
                    votes[eventid]["votesyes"] -= 1
                    votes[eventid]["participants"].remove(
                        {
                            "id": member.id,
                            "username": member.name,
                            "displayname": member.display_name,
                        }
                    )
                if payload.emoji.id == 1148772028216778792:  # no emoji
                    votes[eventid]["votesno"] -= 1
        valueindex += 1
    with open("votes.json", "w") as file:
        json.dump(votes, file, indent=4)


'''@tree.command(name="getctf", description="Find upcoming CTFs")
# variable structure: VARIABLENAME: TYPE = DEFAULTVALUE
async def getctf(interaction, amount: app_commands.Range[int, 1, 15] = 10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    websiteresponse = requests.get(
        "https://ctftime.org/event/list/upcoming", headers=headers
    )
    websitehtml = websiteresponse.text
    # websitehtml = websitehtml.replace("<br />", "\n").replace("<b>", "### ")
    soup = BeautifulSoup(websitehtml, "html5lib")
    table = soup.find_all("div", {"class": "container"})[1]
    tablerows = table.findChildren("tr")
    finalmessage = """
    > ## Here are some upcoming CTFs:
    """
    for row in tablerows[
        1 : amount + 1
    ]:  # we loop from the second item to skip the header
        datarows = row.findChildren("td")
        eventlink = "https://ctftime.org" + datarows[0].find("a", href=True)["href"]
        eventdate = datarows[1].get_text().replace("Sept", "Sep").split(" — ")
        startdt = datetime.strptime(
            str(datetime.now().year) + " " + eventdate[0], "%Y %d %b., %H:%M %Z"
        )
        enddt = datetime.strptime(eventdate[1], "%d %b. %Y, %H:%M %Z")
        eventstart = (
            "<t:"
            + str(startdt.timestamp())[:-2]
            + ":d><t:"
            + str(startdt.timestamp())[:-2]
            + ":t>"
        )
        eventend = (
            "<t:"
            + str(enddt.timestamp())[:-2]
            + ":d><t:"
            + str(enddt.timestamp())[:-2]
            + ":t>"
        )
        finalmessage += (
            "> ["
            + datarows[0].get_text()
            + "](<"
            + eventlink
            + ">) on "
            + eventstart
            + " Event ID: `"
            + eventlink.replace("https://ctftime.org/event/", "")
            + "`\n"
        )
    finalmessage += "> \n> ***all dates are in UTC*** \n"
    # with open("output.html", "w", encoding="UTF-8") as file:
    # file.write(soup.prettify())
    await interaction.response.send_message(finalmessage)
'''


@tree.command(name="createevent", description="Create an event.")
async def createevent(
    interaction,
    month: app_commands.Range[int, 0, 12],
    day: app_commands.Range[int, 0, 31],
    year: int,
    hour: app_commands.Range[int, 0, 12],
    minute: app_commands.Range[int, 0, 60],
    meridiem: str,
):
    eventarray = [
        str(month),
        str(day),
        str(year),
        str(hour),
        str(minute),
        str(meridiem),
    ]
    eventstartdate = datetime.strptime(" ".join(eventarray), "%m %d %Y %I %M %p")
    await interaction.response.send_message(str(eventstartdate), ephemeral=True)


# ADD DECORATOR TO CHECK FOR USERID
@tree.command(name="addctfchannels", description="add ctf category channel by name")
async def add_ctf_channels(
    interaction, ctf_name: str, headers: bool = True, announce: bool = True
):
    if interaction.user.id in whitelist:
        channels = [
            "general",
            "web",
            "crypto",
            "pwn",
            "misc",
            "rev",
            "forensics",
            "osint",
        ]

        await interaction.response.send_message(
            f"added new CTF category: {ctf_name}", ephemeral=True
        )
        category = await interaction.guild.create_category(ctf_name)
        for chann in channels:
            await interaction.guild.create_text_channel(chann, category=category)
            # send in announcements channel that ctf category has been added

        # send message in every new channel introducing it
        if headers:
            for chann in category.channels:
                if not chann.name == channels[0]:
                    await chann.send(
                        f"""🚩 Welcome to the CTF Channel related to {chann.name}! 🕵️‍♂️💻

        Share your knowledge, discuss vulns, and collaborate here! Let's get this! 💪
                            
        **Important: it's not good practice to share the flags here as intruders could steal them from us ( and we dont want that ofc )**

        Remember, keep the conversation focused on {chann.name} CTF topic. Go Reset!! <:reset:1145367774626062396>
        -----------------------------"""
                    )
                else:
                    await chann.send(
                        f"""🌐 Welcome to the General CTF Channel for {ctf_name}! 🏴‍☠️💻

        here you can talk about pretty much everything (please keep it related to the ctf though 🙏) and please don't share flags here

        -----------------------------"""
                    )
        if announce:
            chann = client.get_channel(1145029741561258015)
            message = await chann.send(f"new ctf category for {ctf_name} added!")
            emoji = "\U0001F973"
            await message.add_reaction(emoji)
    else:
        await interaction.response.send_message(
            "you are not allowed to run this command!", ephemeral=True
        )


def vrfy_ctf_category(category: discord.CategoryChannel) -> bool:
    vrfy_channels = ["web", "forensics"]
    count = 0
    for vrf in vrfy_channels:
        for chann in category.channels:
            if str(chann.name) == vrf:
                count += 1
    if count >= 2:
        return True
    else:
        return False


@tree.command(name="delctfcategory", description="del ctf category channels by name")
async def del_ctf_channels(interaction, category: discord.CategoryChannel):
    if interaction.user.id in whitelist:
        channels = category.channels

        if vrfy_ctf_category(category):
            await interaction.response.send_message(
                f"Deleted CTF category: {category.name}", ephemeral=True
            )
            for chann in channels:
                await chann.delete()
            await category.delete()
        else:
            await interaction.response.send_message(
                "this is not a CTF category!", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "you are not allowed to run this command!", ephemeral=True
        )


@client.event
async def on_message(message):
    if message.author.bot:
        return
    print(message.author.display_name + ": " + message.content)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    print(message.author.display_name + ": " + message.content)


@client.event
async def on_ready():
    await tree.sync()
    print("yes mom i'm awake")


with open("token.token", "r") as file:
    token = file.read()
client.run(token)
