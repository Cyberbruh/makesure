import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

dialogs = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


async def dialog(usr, members):

    def check(m):
        return m.author == usr
    opponent_tag = await bot.wait_for("message", check=check)
    opponent = None
    await usr.send('Введите сумму вашего взноса')
    fee = await bot.wait_for('message', check=check)
    await usr.send('Опишите суть вашего спора')
    desc = await bot.wait_for('message', check=check)
    for m in members:
        if (m.name + '#' + m.discriminator) == opponent_tag.content:
            opponent = m
    await opponent.send(f'{usr.name} вызывает вас на спор. Сумма ставки {fee.content} тугриков. {desc.content}')


@bot.command()
async def start(ctx):
    await ctx.author.send('Введите тег пользователя, с которым вы хотите начать спор?')
    members = ctx.guild.members
    await dialog(ctx.author, members)




bot.run(os.environ.get('DISCORD_TOKEN'))
