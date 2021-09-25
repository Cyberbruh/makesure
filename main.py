import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

import src.mongo

load_dotenv()

db = MongoClient('mongodb://localhost:27017/').makesure
client = discord.Client()

bot = commands.Bot(command_prefix='!')

@bot.command()
async def start(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')

bot.run(os.getenv('DISCORD_TOKEN'))