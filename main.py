import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

import src.mongo

load_dotenv()

dlgs = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@bot.command()
async def start(ctx):
    await ctx.author.send('Введите тег пользователя, с которым вы хотите начать спор?')
    print(ctx.author.id)
    dlgs.append(ctx.author)
    members = ctx.guild.members

    def check(m):
        return m.author == ctx.author
    msg = await bot.wait_for("message", check=check)
    for m in members:
        if (m.name + '#' + m.discriminator) == msg.content:
            await m.send('Бросаю перчатку!')

#bot.remove_command(startt)
#bot.add_command(startt)



bot.run(os.environ.get('DISCORD_TOKEN'))
