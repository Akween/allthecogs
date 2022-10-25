import discord
from datetime import datetime
import os
import asyncio
from redbot.core import Config, bot, commands
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.mod import slow_deletion
from redbot.core.commands import Context, Cog
from redbot.core.config import Group


# noinspection PyBroadException
class Birthday(commands.Cog):
    """An Extension to remind people of birthdays."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Dictionary to save the birthdays, format:
        # birthday_dict = {<server> : {<date> : {<user> : <year>,
        #                                        <user> : <year>,
        #                                        <user> : <year>},
        #                              <date> : {<user> : <year>,
        #                                        <user> : <year>,
        #                                        <user> : <year>}},
        #                  <server> : {<date> : {<user> : <year>,
        #                                        <user> : <year>,
        #                                        <user> : <year>},
        #                              <date> : {<user> : <year>,
        #                                        <user> : <year>,
        #                                        <user> : <year>}}}
        # where <user> and <server> are ids, <date> has the form of <d>.<m>. and year is either zero or int.

        self.birthday_dict = {}

        self.month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        # list of global admins for this extension
        self.admin_list = []
        self.owner_id = 506083422834262016  # Akween

        # Dictionary to save the maintenance channel for each server. Default is None. Global maintenance should be on
        # support server and set only by admins.
        # Format: {server: channel id}
        self.maintenance_dict = {}
        self.global_maintenance = None

        # Dictionary to save the announcement channel for each server. Default is None. Needs to be set in order for
        # the bot to send announcements!
        # Format: {server: channel id}
        self.announcementchannel_dict = {}

        # Dictionary to save the custom announcement message for each server. Default is global.
        # Format: {server: message}
        self.announcement_dict = {}

        # Dictionary to save the custom toggle of birthday announcements. Default is off and is changed to on as a
        # channel for announcements is set! -1 or none is off, 0 is on.
        # Format: {server: toggle}
        self.announcement_toggle = {}

        # Automatically load saved birthdays at startup
        self.bdLoad()

        # Automatically load admins from file "birthday_admins.txt"
        self.admLoad()

        # Automatically load maintenance channels from file "maintenance_channels.txt"
        self.mtnLoad()

        # Automatically load announcement channels from file "announcement_channels.txt"
        self.annChLoad()

        # Automatically load announcement toggles from file "announcement_toggles.txt"
        self.annTgLoad()

        # Automatically load announcement messages from file "announcement_messages.txt"
        self.annMsgLoad()

        self.bot.loop.create_task(self.checkTime())

    async def checkTime(self):
        await self.bot.wait_until_ready()
        yesterday = datetime.now()
        while not self.bot.is_closed():
            if datetime.now().day > yesterday.day or (datetime.now().day == 1 and datetime.now().month > yesterday.month) or (datetime.now().day == 1 and datetime.now().month == 1 and datetime.now().year > yesterday.year):
                current_date = str(datetime.now().day) + "." + str(datetime.now().month) + "."
                # check every server
                for server in self.birthday_dict:
                    for date in self.birthday_dict[server]:
                        if date == current_date:
                            for user in self.birthday_dict[server][date]:
                                await self.announce(server, user)
                yesterday = datetime.now()

            print("checked time")

            if datetime.now().hour <= 1:
                await asyncio.sleep(3600*24)  # check every 24 hours
            else:
                await asyncio.sleep(3600)  # Check once an hour

    def remove(self, server, date, user=None):
        if user is not None:
            self.birthday_dict[server][date].pop(user)
        else:
            self.birthday_dict[server].pop(date)

    def bdSave(self, target_server=None):
        if target_server is None:  # global save
            index = 0

            # each server has a file named "server<index>.txt" which holds the server id in the first row and the
            # list of dates, users and years in the rest
            # Format: date user year

            for server in self.birthday_dict:

                name = "server" + str(index) + ".txt"

                with open(name, 'w') as writer:
                    writer.write(str(server) + '\n')
                    temp_string = ""
                    for date in self.birthday_dict[server]:
                        for user in self.birthday_dict[server][date]:
                            temp_string += date + " " + str(user) + " " + str(self.birthday_dict[server][date][user]) + '\n'
                        writer.write(temp_string)
                        temp_string = ""

                index += 1
        else:
            index = list(self.birthday_dict).index(target_server)
            name = "server" + str(index) + ".txt"

            with open(name, 'w') as writer:
                writer.write(str(target_server) + '\n')
                temp_string = ""
                for date in self.birthday_dict[target_server]:
                    for user in self.birthday_dict[target_server][date]:
                        temp_string += date + " " + str(user) + " " + str(self.birthday_dict[target_server][date][user]) + '\n'
                    writer.write(temp_string)
                    temp_string = ""

    def bdLoad(self):
        index = 0
        while True:  # until it finds a non-existing file and returns
            name = "server" + str(index) + ".txt"
            try:
                reader = open(name, 'x')  # if file does not exist, it now does
            except:
                reader = None  # file exists

            # each server has a file named "server<index>.txt" which holds the server id in the first row and the
            # list of dates, users and years in the rest
            # Format: date user year

            if reader is None:  # if the file exists
                with open(name) as reader:
                    load_server = reader.readline()
                    for line in reader:
                        if line == "":
                            break
                        line_split = line.split(" ", 2)
                        load_date = line_split[0]
                        load_user = line_split[1]
                        load_year = line_split[2]
                        if load_year == '\n':
                            load_year = 0
                        self.addToDict(int(load_server), load_date, int(load_user), int(load_year))
                index += 1
            else:
                reader.close()
                os.remove(name)
                return

    def mtnSave(self):
        # format: first line holds global, then <server id> whitespace <channel id>
        with open("maintenance_channels.txt", 'w') as writer:
            writer.write(str(self.global_maintenance) + '\n')
            for server in self.maintenance_dict:
                writer.write(str(server) + " " + str(self.maintenance_dict[server]) + '\n')

    def mtnLoad(self):
        try:
            reader = open("maintenance_channels.txt", 'x')  # if file does not exist, it now does
        except:
            reader = None  # file exists

        if reader is None:  # if the file exists
            # format: first line holds global, then <server id> whitespace <channel id>
            with open("maintenance_channels.txt", 'r') as reader:
                self.global_maintenance = int(reader.readline())
                for line in reader:
                    if line == "":
                        break
                    line_split = line.split(" ", 1)
                    load_server = int(line_split[0])
                    load_channel = int(line_split[1])

                    self.maintenance_dict.update({load_server: load_channel})
        else:
            reader.close()
            os.remove("maintenance_channels.txt")
            return

    def annChSave(self):
        # format: <server id> whitespace <channel id>
        with open("announcement_channels.txt", 'w') as writer:
            for server in self.announcementchannel_dict:
                writer.write(str(server) + " " + str(self.announcementchannel_dict[server]) + '\n')

    def annChLoad(self):
        try:
            reader = open("announcement_channels.txt", 'x')  # if file does not exist, it now does
        except:
            reader = None  # file exists

        if reader is None:  # if the file exists
            # format: <server id> whitespace <channel id>
            with open("announcement_channels.txt", 'r') as reader:
                for line in reader:
                    if line == "":
                        break
                    line_split = line.split(" ", 1)
                    load_server = int(line_split[0])
                    load_channel = int(line_split[1])

                    self.announcementchannel_dict.update({load_server: load_channel})
        else:
            reader.close()
            os.remove("announcement_channels.txt")
            return

    def annTgSave(self):
        # format: <server id> whitespace <toggle int>
        with open("announcement_toggles.txt", 'w') as writer:
            for server in self.announcement_toggle:
                writer.write(str(server) + " " + str(self.announcement_toggle[server]) + '\n')

    def annTgLoad(self):
        try:
            reader = open("announcement_toggles.txt", 'x')  # if file does not exist, it now does
        except:
            reader = None  # file exists

        if reader is None:  # if the file exists
            # format: <server id> whitespace <toggle int>
            with open("announcement_toggles.txt", 'r') as reader:
                for line in reader:
                    if line == "":
                        break
                    line_split = line.split(" ", 1)
                    load_server = int(line_split[0])
                    load_channel = int(line_split[1])

                    self.announcement_toggle.update({load_server: load_channel})
        else:
            reader.close()
            os.remove("announcement_toggles.txt")
            return

    def admLoad(self):
        try:
            reader = open("birthday_admins.txt", 'x')  # if file does not exist, it now does
        except:
            reader = None  # file exists

        if reader is None:  # if the file exists
            with open("birthday_admins.txt") as reader:
                for line in reader:
                    if line == "":
                        break
                    self.admin_list.append(int(line))

    def removeFromDict(self, server, rm_user):
        rm_date = ""
        success = -1
        if server in self.birthday_dict:
            for date in self.birthday_dict[server]:
                if rm_user in self.birthday_dict[server][date]:
                    self.remove(server, date, rm_user)
                    rm_date = date
                    success = 0

            # If the date the user was previously registered in is now empty, remove it from that server
            if rm_date != "" and self.birthday_dict[server][rm_date] == {}:
                self.remove(server, rm_date)

        return success

    def addToDict(self, set_server, set_date, set_user, set_year):
        if set_server in self.birthday_dict:
            self.removeFromDict(set_server, set_user)

            # set the users new birthday
            if set_date in self. birthday_dict[set_server]:
                self.birthday_dict[set_server][set_date].update({set_user: set_year})
            else:
                self.birthday_dict[set_server].update({set_date: {set_user: set_year}})
        else:
            # set the users birthday
            self.birthday_dict.update({set_server: {set_date: {set_user: set_year}}})

    @staticmethod
    def datecheck(day: int, month: int, year: int):
        daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if month < 1 or month > 12 or day < 1 or day > daysInMonth[
                month - 1] or year < datetime.now().year - 100 or year > datetime.now().year:
            return False
        else:
            return True

    def fetchUser(self, server: int, user: int):
        for temp_server in self.bot.guilds:
            if temp_server.id == server:
                server = temp_server
                break

        for temp_user in server.members:
            if temp_user.id == user:
                return temp_user

    async def announce(self, ann_server: int, ann_user: int):
        # Check if announcement is legal
        if ann_server in self.announcementchannel_dict and ann_server in self.announcement_toggle and self.announcement_toggle[ann_server] == 0:

            # Fetching the user object of ann_user
            ann_user = self.fetchUser(ann_server, ann_user)

            ann_year = 0
            # finding whether the user has an age to be announced as well
            for date in self.birthday_dict[ann_server]:
                if ann_user.id in self.birthday_dict[ann_server][date]:
                    ann_year = self.birthday_dict[ann_server][date][ann_user.id]
                    break

            if ann_year != 0:
                age = datetime.now().year - int(ann_year)
                msg = "Happy " + str(age) + "th Birthday, " + ann_user.mention + "! "
            else:
                msg = "Happy Birthday, " + ann_user.mention + "! "

            if ann_server in self.announcement_dict:
                msg += self.announcement_dict[ann_server]

            channel = await self.bot.fetch_channel(self.announcementchannel_dict[ann_server])

            await channel.send(msg)

    def annMsgSave(self):
        # format: <server id> newline <message> ?
        with open("announcement_messages.txt", 'w') as writer:
            for server in self.announcement_dict:
                writer.write(str(server) + " " + str(self.announcement_dict[server]) + '\n')

    def annMsgLoad(self):
        try:
            reader = open("announcement_messages.txt", 'x')  # if file does not exist, it now does
        except:
            reader = None  # file exists

        if reader is None:  # if the file exists
            # format: <server id> whitespace <toggle int>
            with open("announcement_messages.txt", 'r') as reader:
                for line in reader:
                    if line == "":
                        break
                    line_split = line.split(" ", 1)
                    load_server = int(line_split[0])
                    load_message = line_split[1]

                    self.announcement_dict.update({load_server: load_message})
        else:
            reader.close()
            os.remove("announcement_messages.txt")
            return

    @commands.command(hidden=True)
    async def msgshow(self, ctx: commands.Context):
        """Shows the birthday message for this server. Admin only!"""
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        await ctx.send(self.announcement_dict[ctx.guild.id])

    @commands.command(hidden=True)
    async def bdmessage(self, ctx: commands.Context, *, message: str):
        """Sets a custom message for birthday announcements on this server. Admin only!"""
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        # Changing and adding an entry in a dictionary is the same keyword
        self.announcement_dict.update({ctx.guild.id: message})
        self.annMsgSave()

        await ctx.send("Announcement message set successfully.")

    @commands.command(hidden=True)
    async def bdannounceforce(self, ctx: commands.Context):
        """Force-announces a user's birthday. Only for testing."""

        await self.announce(ctx.guild.id, ctx.message.author.id)

    @commands.command(hidden=True)
    async def bdmtnglobal(self, ctx: commands.Context, channel: str):
        """Sets a channel for updates on the birthday extension globally. Owner only!"""
        if ctx.author.id != self.owner_id:
            await ctx.send("You do not have permission to use this command. Please contact bot owner.")
            return

        # Channel tag is of Format <#channelid>
        new_channel_id = int(channel[2:-1])

        # Changing and adding an entry in a dictionary is the same keyword
        self.global_maintenance = new_channel_id

        self.mtnSave()

        await ctx.send("Global maintenance channel set successfully.")

    @commands.command(hidden=True)
    async def bdmaintenance(self, ctx: commands.Context, channel: str):
        """Sets a channel for updates on the birthday extension on this server. Admin only!"""
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        # Channel tag is of Format <#channelid>
        new_channel_id = int(channel[2:-1])

        # Changing and adding an entry in a dictionary is the same keyword
        self.maintenance_dict.update({ctx.guild.id: new_channel_id})

        self.mtnSave()

        await ctx.send("Maintenance channel set successfully.")

    @commands.command(hidden=True)
    async def bdannounce(self, ctx: commands.Context, channel: str):
        """Sets a channel for birthday announcements on this server. Admin only!"""
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        # Channel tag is of Format <#channelid>
        new_channel_id = int(channel[2:-1])

        # Changing and adding an entry in a dictionary is the same keyword
        self.announcementchannel_dict.update({ctx.guild.id: new_channel_id})
        self.announcement_toggle.update({ctx.guild.id: 0})  # turn on

        self.annTgSave()
        self.annChSave()

        await ctx.send("Announcement channel set successfully.")

    @commands.command(hidden=True)
    async def bdtoggle(self, ctx: commands.Context):
        """Toggles birthday announcements for this server. Admin only!"""
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        # Changing and adding an entry in a dictionary is the same keyword
        if ctx.guild.id in self.announcement_toggle:  # if the guild has a toggle
            if self.announcement_toggle[ctx.guild.id] == -1:  # if off
                self.announcement_toggle.update({ctx.guild.id: 0})  # turn on
                msg = "on"
            else:
                self.announcement_toggle.update({ctx.guild.id: -1})  # turn off
                msg = "off"
        else:
            self.announcement_toggle.update({ctx.guild.id: 0})  # turn on
            msg = "on"

        self.annTgSave()

        await ctx.send("Announcement toggled successfully: now " + msg + ".")

    @commands.command(hidden=True)
    async def bdadmin(self, ctx: commands.Context, user: str):
        """Adds a user as an admin for the birthday extension. Admin only!"""
        # a tagged user has the form <@user id>
        if ctx.author.id == self.owner_id and self.owner_id not in self.admin_list:
            self.admin_list.append(self.owner_id)  # Nobody can deny me (Akween) access!
            with open("birthday_admins.txt", 'a') as writer:
                writer.write(str(self.owner_id))

        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        if user[0] != '<' or user[1] != '@' or user[len(user) - 1] != '>':
            await ctx.send("Invalid user.")
            return
        new_admin_id = int(user[2:-1])
        self.admin_list.append(new_admin_id)

        with open("birthday_admins.txt", 'a') as writer:
            writer.write(str(new_admin_id))

        await ctx.send("New admin added successfully!")

    @commands.command(hidden=True)
    async def bdadminrm(self, ctx: commands.Context, user: str):
        """Removes a user as an admin for the birthday extension. Admin only!"""
        # a tagged user has the form <@user id>
        if ctx.author.id == self.owner_id and self.owner_id not in self.admin_list:
            self.admin_list.append(self.owner_id)  # Nobody can deny me (Akween) access!
            with open("birthday_admins.txt", 'a') as writer:
                writer.write(str(self.owner_id))

        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        if user[0] != '<' or user[1] != '@' or user[len(user) - 1] != '>':
            await ctx.send("Invalid user.")
            return

        old_admin_id = int(user[2:-1])
        self.admin_list.remove(old_admin_id)

        with open("birthday_admins.txt", 'w') as writer:
            for admin in self.admin_list:
                writer.write(str(admin))

        await ctx.send("Admin removed successfully!")

    @commands.command(hidden=True)
    async def showadmins(self, ctx: commands.Context):
        """Shows present admins for the birthday extension."""
        temp_string = "List of Birthday admins:" + '\n'
        server_members = []
        for user in ctx.guild.members:
            server_members.append(user.id)
        for x in self.admin_list:
            if x in server_members:
                for temp_user in ctx.guild.members:
                    if temp_user.id == x:
                        temp_string += temp_user.name + "#" + temp_user.discriminator + '\n'
        await ctx.send(temp_string)

    @commands.command()
    async def bdsave(self, ctx: commands.Context):
        """Force-saves Birthdays into file."""
        self.bdSave()
        await ctx.send("Birthday List has been saved successfully!")

    @commands.command(hidden=True)
    async def bdload(self, ctx: commands.Context):
        """Force-loads Birthdays from last save."""
        self.bdLoad()
        await ctx.send("Birthdays have been loaded successfully!")

    @commands.command()
    async def bdlist(self, ctx: commands.Context):
        """Displays birthdays registered on this server."""

        birthday_list = []
        for i in range(0, 12):
            birthday_list.append([])
        list_server = ctx.guild.id
        list_server_members = []
        for user in ctx.guild.members:
            list_server_members.append(user.id)
        rm_user_list = []

        if list_server in self.birthday_dict:  # if there are birthdays registered on this server
            for date in self.birthday_dict[list_server]:  # add users for every date

                date_split = date.split(".", 2)

                for user in self.birthday_dict[list_server][date]:
                    if user in list_server_members:  # check if the user is still a member of the server
                        temp_user = self.fetchUser(list_server, user)  # fetch the user's name

                        temp_string = date + ": " + temp_user.name  # create temporary string to display in the list

                        bd_year = int(self.birthday_dict[list_server][date][user])
                        if bd_year != 0:  # add age, if a year is given
                            age = datetime.now().year - bd_year
                            temp_string += " - " + str(age) + " years"

                        # append to correct birthday sublist
                        birthday_list[int(date_split[1]) - 1].append(temp_string)

                    else:  # if the user is no longer on this server, add to a list of users to remove
                        rm_user_list.append(user)

            for user in rm_user_list:
                self.removeFromDict(list_server, user)
            self.bdSave(list_server)

        else:  # no birthdays
            await ctx.send("There are no registered birthdays on this server :(")
            return

        # so the dates within a month are of ascending order
        for i in range(0, 12):
            birthday_list[i].sort()

        # make the embed for the calendar
        bdembed = discord.Embed(title="Birthday List", color=discord.Color.greyple())

        # produce the list to be shown
        for i in range(0, 12):
            text = ""
            for line in birthday_list[i]:
                text += line + '\n'
            if text != "":
                bdembed.add_field(name=self.month_names[i], value=text, inline=False)

        await ctx.send(embed=bdembed)

    @commands.command()
    async def bdset(self, ctx: commands.Context, date: str):
        """Format: !bdset <d>.<m>.<y> or !bdset <d>.<m>."""
        # Split input text into a date in the form <d>.<m>. and a year; if the input format is faulty, an error message
        # is given. If no year is provided, it is set as zero.
        date_split = date.split(".", 2)

        # Check whether the entered date is valid
        if len(date_split) == 3 and date_split[0] != "":
            try:
                if date_split[2] != "":
                    if not self.datecheck(int(date_split[0]), int(date_split[1]), int(date_split[2])):
                        await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                        return
                else:
                    if not self.datecheck(int(date_split[0]), int(date_split[1]), datetime.now().year):
                        await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                        return
            except:
                await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                return
        else:
            await ctx.send("Date was entered incorrectly. Please check the format and try again!")
            return

        set_date = date_split[0] + "." + date_split[1] + "."
        set_year = date_split[2]

        if set_year == "":
            set_year = 0

        set_user = ctx.message.author.id
        set_server = ctx.guild.id

        self.addToDict(set_server, set_date, set_user, set_year)
        self.bdSave(set_server)

        await ctx.send("Birthday for " + ctx.author.name + " in " + ctx.guild.name + " has been set as " + set_date + "!")

        # just for testing:
        # await ctx.send(self.birthday_dict)

    @commands.command(hidden=True)
    async def bdsetuser(self, ctx: commands.Context, user: str, date: str):
        """Format: !bdset @<user> <d>.<m>.<y> or !bdset @<user> <d>.<m>.. Admin only!"""

        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        if user[0] != '<' or user[1] != '@' or user[len(user) - 1] != '>':
            await ctx.send("Invalid user.")
            return

        # Split input text into a date in the form <d>.<m>. and a year; if the input format is faulty, an error message
        # is given. If no year is provided, it is set as zero.
        date_split = date.split(".", 2)

        # Check whether the entered date is valid
        if len(date_split) == 3 and date_split[0] != "":
            try:
                if date_split[2] != "":
                    if not self.datecheck(int(date_split[0]), int(date_split[1]), int(date_split[2])):
                        await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                        return
                else:
                    if not self.datecheck(int(date_split[0]), int(date_split[1]), datetime.now().year):
                        await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                        return
            except:
                await ctx.send("Date was entered incorrectly. Please check the format and try again!")
                return
        else:
            await ctx.send("Date was entered incorrectly. Please check the format and try again!")
            return

        set_date = date_split[0] + "." + date_split[1] + "."
        set_year = date_split[2]

        if set_year == "":
            set_year = 0

        set_user = int(user[2:-1])
        set_server = ctx.guild.id

        self.addToDict(set_server, set_date, set_user, set_year)
        self.bdSave(set_server)

        set_user_name = ""
        for temp_user in ctx.guild.members:
            if temp_user.id == set_user:
                set_user_name = temp_user.name

        await ctx.send(
            "Birthday for " + set_user_name + " in " + ctx.guild.name + " has been set as " + set_date + "!")

        # just for testing:
        # await ctx.send(self.birthday_dict)

    @commands.command()
    async def bdremove(self, ctx: commands.Context):
        """Removes your birthday from the list."""
        rm_server = ctx.guild.id
        rm_user = ctx.author.id

        if self.removeFromDict(rm_server, rm_user) == 0:
            await ctx.send("Birthday removed successfully.")
            self.bdSave(rm_server)
        else:
            await ctx.send("You have no registered birthday on this server. No changes were made.")

    @commands.command(hidden=True)
    async def bdremoveuser(self, ctx: commands.Context, user: str):
        """Format: !bdremove @<user>. Admin only!"""
        # a tagged user has the form <@user id>
        if ctx.author.id not in self.admin_list:
            await ctx.send("You do not have permission to use this command. Please contact bot admins.")
            return

        if user[0] != '<' or user[1] != '@' or user[len(user) - 1] != '>':
            await ctx.send("Invalid user.")
            return

        rm_user = int(user[2:-1])
        rm_server = ctx.guild.id

        if self.removeFromDict(rm_server, rm_user) == 0:
            await ctx.send("Birthday removed successfully.")
            self.bdSave(rm_server)
        else:
            await ctx.send("This user has no registered birthday on this server. No changes were made.")

# key from value:
# key = list(self.birthday_dict[set_server].keys)[list(self.birthday_dict[set_server].values).index(set_user)]


# Changelog-ish:
# 22.10.: added set-function and assured basic functionality of it
#         added a check for the value of day, month and year in the bdset-function
#         made sure the date also gets deleted if the last user occupying it is removed
#         added list-function and assured basic functionality
#         fetch the username from the guild's members
# 23.10.: made the bdlist-embed work properly
#         added a save-function to write user birthdays into files for safe reloading
#         added a load-function, does not load properly (newlines in the saved ids)
# 24.10.: made it cut away the newline character at the end (load_server, load_year) by casting to int
#         added the now functioning reload-function into the __init__
#         added a hidden admin function to add global admins for this extension
#         added a hidden function to display this server's admins
#         added a bdremove-function to delete a users own birthday
#         in bdlist, added a safe removal of users if they are no member of the server any more
#         added a hidden admin version of the bdremove-function which allows to remove other users birthdays
#         added a hidden admin version of the set-function to set other people's birthdays
#         added routine to save admin config into file
#         added backdoor to assure owner access to admin functions
#         added a hidden admin function to remove admins
#         added a hidden admin function to set a channel to post cog updates into per server
#         added a hidden admin function to set a channel to post announcement into per server
#         added a hidden admin function to toggle announcement per server
#         added a hidden admin function to set a custom announcement message per server
#         added routines to save and load the maintenance channels
#         added routines to save and load the announcement channels
#         added routines to save and load the announcement toggles
#         added a function for announcing birthdays
#         added routines to save and load the announcement messages
#         made the bdSave(server) function save a single server's birthdays
#         added a coroutine that checks the current date every 24 h (between 12pm and 1am) or every hour
#         made it actually use (append) custom messages to the announcement
