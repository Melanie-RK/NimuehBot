import random
import pymongo
import discord
from help_command import NewHelpCommand
from vicious_mockery import random_insult
from discord.ext import commands

QUOTES_CHANNEL = ""

TOKEN = ""
with open('token.txt') as f:
    TOKEN = f.readline().strip('\n')

DB_USER = ""
with open('db_user.txt') as f:
    DB_USER = f.readline().strip('\n')

DB_PASSWORD = ""
with open('db_pw.txt') as f:
    DB_PASSWORD = f.readline().strip('\n')

CLUSTERSTRING = ""
with open('clusterstring.txt') as f:
    CLUSTERSTRING = f.readline().strip('\n')

client = pymongo.MongoClient(f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@{CLUSTERSTRING}/?retryWrites=true&w=majority&appName=NimueBot")
db = client.discord
quotes_channels = db.quotes_channels

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

bot.help_command = NewHelpCommand()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def set_quotes_channel(ctx, arg):
    global QUOTES_CHANNEL
    QUOTES_CHANNEL = arg
    print(QUOTES_CHANNEL)

    if QUOTES_CHANNEL:
        # Store quotes channel information in MongoDB
        get_from_database = quotes_channels.find_one({'server': ctx.guild.id})

        if get_from_database is not None:
            quotes_channels.update_one({"server": ctx.guild.id}, {"$set": {"channel_name": arg}}, upsert=True)
        else:                              
            channel_entry = {
                'server': ctx.guild.id,
                'channel_name': QUOTES_CHANNEL
            }
            quotes_channels.insert_one(channel_entry)

    await ctx.send(f'Quotes channel set to {arg}')

async def get_quotes_channel(ctx):
    get_from_database = quotes_channels.find_one({'server': ctx.guild.id})    
    if get_from_database is None:
        await ctx.send("No quotes channel found")
        return QUOTES_CHANNEL
    else:
        channel_name = get_from_database['channel_name']
        return channel_name

@bot.command()
async def random_quote(ctx):
    global QUOTES_CHANNEL

    if QUOTES_CHANNEL == '':
        QUOTES_CHANNEL = await get_quotes_channel(ctx)    
        if QUOTES_CHANNEL == '':
            return      
    try:
        channel = discord.utils.get(ctx.guild.channels, name=QUOTES_CHANNEL)
        messages = [message async for message in channel.history(limit=100)] #limit the bot to the last 100 messages
        if len(messages) > 0:
            random_message = random.choice(messages)   
            await ctx.send(random_message.content)
        else:
            await ctx.send("No quotes found")
    except discord.Forbidden:
        await ctx.send("I don't have permission to read messages in that channel")

@bot.command()
async def quote(ctx,*, arg):
    try:
        channel = discord.utils.get(ctx.guild.channels, name=QUOTES_CHANNEL)
        await channel.send(arg)
    except:
        await ctx.send("Error occured while quoting")

@bot.command()
async def remove_quotes_channel(ctx):
    get_from_database = quotes_channels.find_one({'server': ctx.guild.id})
    if (get_from_database != None): 
      await ctx.send(f"Deleted quotes channel: {get_from_database.get('channel_name')}")
      quotes_channels.delete_one({'server': ctx.guild.id})      
    else: 
      await ctx.send(f"Server does not have a quotes channel")

@bot.command()
async def quotes_channel(ctx):
    get_from_database = quotes_channels.find_one({'server': ctx.guild.id})
    if (get_from_database != None):
        await ctx.send(f"Quotes channel is set to: {get_from_database.get('channel_name')}")
    else:
        await ctx.send("Server does not have a quotes channel")

@bot.command()
async def vicious_mockery(ctx):
    insult = random_insult()
    await ctx.send(f"{insult}, {ctx.author.mention}")

bot.run(TOKEN)

