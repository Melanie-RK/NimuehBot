import random
import discord
from discord.ext import commands

TOKEN = ""
with open('token.txt') as f:
    TOKEN = f.readline().strip('\n')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def set_quotes_channel(ctx, arg):
    global QUOTES_CHANNEL
    QUOTES_CHANNEL = arg
    await ctx.send(f'Quotes channel set to {arg}')

@bot.command()
async def random_quote(ctx):
    global QUOTES_CHANNEL
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

bot.run(TOKEN)

