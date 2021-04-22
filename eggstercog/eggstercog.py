from redbot.core import Config, bot, commands
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.mod import slow_deletion
from redbot.core.commands import Context, Cog
from redbot.core.config import Group
import asyncio
import time
import datetime
import discord
import logging
import hashlib
import contextlib
import itertools
#from .eggstercog import mytestbench
import random

class Eggstercog(Cog):   
    
    BUUL = None
    client = discord.Client()
    
    @commands.group()
    async def egg(self, ctx: Context):
        """Egg"""
        pass
    
    async def refreshBuul(self, a: bool):
        global BUUL
        a = BUUL
        return a
    
    @commands.command()
    async def doit(self, ctx):
        """activates an egg"""
        msg = await ctx.send("What's that over there?")
        a = 0
        start_adding_reactions(msg, ["\N{EGG}"])
        pred = ReactionPredicate.with_emojis(["\N{EGG}"], msg)
        try:
            await ctx.bot.wait_for("reaction_add", check=pred, timeout=10)
            a = 1
        except asyncio.TimeoutError:
            await slow_deletion([msg])
            await ctx.send("Someone destroyed the egg!")
        
        if not pred.result and a == 1:
            await ctx.send("You have found the egg!")
    
    @commands.command()
    async def dennis(self, ctx): 
        """yeet"""
        global BUUL
        BUUL = True
        thang = True
        yikes = 0
        while yikes<5: 
            yikes +=1
            await ctx.send("this is dennis")
            time.sleep(3)
            try:
                self.refreshBuul(BUUL)
            except:
                await ctx.send("ERROR: buul ist nicht definiert")
                break
            thang = BUUL
            if thang == False: 
                await ctx.send("oke i stop")
                BUUL = True
                break
    
    @commands.command()
    async def whereegg(self, ctx):
        """Wirft zwar keinen fehler mehr, aber halt doch."""
        
        count = 0
        yeet = True
        
        while yeet and count < 10:
            try:
                #for guild in bot.guilds:
                
                 #   channel = guild.channels.cache.find('madster');
                for guild in bot.guilds:
                    _guild = bot.get_guild(int(guild))
                    await _guild.get_channel(696395792742613083)
#                        if random.randint(1, 2) == 2:
 #                           continue
  #                      _guild = self.bot.get_guild(int(guild))
   #                     if _guild is None:
    #                        continue
     #                   channel = _guild.get_channel(
      #                      int(random.choice(self.guildcache[guild]["activechannels"]))
       #                 )
                    if channel is None:
                        continue
                        
                    await ctx.send("Where egg?")
                await asyncio.sleep(2)
                x+=1
                yeet = refreshBuul(yeet)
            except Exception:
                await ctx.send("taht went wrong")
                break

    @client.event
    async def an_eggo(self, message, ctx):
        if message.author == discord.Client.user:
            return
        if BUUL == True:
            x = 1
            if x <= 1:
                start_adding_reactions(message, ["\N{EGG}"])
                pred = ReactionPredicate.with_emojis(["\N{EGG}"], message)
                try:
                    await ctx.bot.wait_for("reaction_add", check=pred, timeout=10)
                    a = 1
                except asyncio.TimeoutError:
                    await ctx.send("Someone destroyed the egg!")

                if not pred.result and a == 1:
                    await ctx.send("You have found the egg!")
        return

    @commands.command()
    async def dont(self, ctx):
        global BUUL
        BUUL = False
#        await ctx.send("buul is " + str(BUUL))
        return BUUL
    
    @commands.command()
    async def nochmal(self, ctx):
        global BUUL
        BUUL = True
        await ctx.send("buul is " + str(BUUL))
        return BUUL
        
    @commands.command()
    async def eggboard(self, ctx): 
        """This is where the leaderboard is supposed to go."""
        await ctx.send("This is where the leaderboard ist supposed to go.")
        
    @commands.command()
    async def setchannel(self, ctx): 
        """You should be able to set the channel with this. Eventually."""
        await ctx.send("This is where you'd be able to set the channel.")
        
    @commands.command()
    async def dick(self, ctx): 
        """Its big - or is it?"""
        await ctx.send("Its very big")
    
    @commands.command()
    async def cock(self, ctx): 
        """Shows cock"""
        now = datetime.datetime.utcnow().day
        await ctx.send(str(now))

    @egg.command(name="channel")
    async def egg_channel(self, ctx: Context, channel: discord.TextChannel):
        """Set and shows the channel"""
        unique_id = int(hashlib.sha512(("PavAkw" + "@" + self.__class__.__name__).encode()).hexdigest(), 16)
        self.config = Config.get_conf(self, identifier=unique_id)
        self.config.register_guild(channel=None, role=None, yesterdays=[])
        message = ctx.message
        guild = message.guild
        await self.config.guild(channel.guild).channel.set(channel.id)
       # await message.channel.send(self.CHANNEL_SET(g=guild.name, c=channel.name))
        await ctx.send(str(channel))
        
#    @egg.command(name="user")
 #   async def egg_user(self, ctx: Context, user: discord.user_id): 
  #      """Its big"""
   #     x = self.get_or_fetch_user(user)
    #    await ctx.send(str(user))

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#STUFF FOR CHANNEL_SET

#import logging
#import hashlib
#import contextlib
#import itertools

#from redbot.core import Config, checks
#from redbot.core.bot import Red
#from redbot.core.config import Group
#from redbot.core.i18n import Translator, cog_i18n
#from redbot.core.commands import Context, Cog
#from redbot.core.utils.chat_formatting import bold, pagify

#T_ = Translator("Eggstercog", __file__)


#def _(s):
#    def func(*args, **kwargs):
#        real_args = list(args)
#        real_args.pop(0)
#        return T_(s).format(*real_args, **kwargs)
#    return func


#@cog_i18n(T_)

#    CHANNEL_SET = _(":white_check_mark: "
#                    "The channel for announcing eggs **{g}** has been set to: **{c}**.")
#    CHANNEL_SET = (g, c)

#    @commands.command()
#    async def channel(self, ctx: Context, channel: discord.TextChannel):
#        """Sets the channel"""
#        message = ctx.message
#        guild = message.guild
#        await self.config.guild(channel.guild).channel.set(channel.id)
#        await message.channel.send(self.CHANNEL_SET(g=guild.name, c=channel.name))
