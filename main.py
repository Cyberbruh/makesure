"""
Main entripoint of a bot.
"""

import os
import urllib
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from dotenv import load_dotenv
import datetime
from mongoengine import *
import src.chatex

from src.dispute import Dispute, DisputeStatus
from src.proof import Proof
from src.deposit import Deposit, DepositStatus
from src.payout import Payout

# Load variables from .env file
load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
DiscordComponents(bot)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


async def dialog(usr, members):

    def from_user(m):
        return m.author == usr
    opponent_tag = await bot.wait_for("message", check=from_user)
    opponent = None
    await usr.send('Введите сумму вашего взноса')
    fee = await bot.wait_for('message', check=from_user)
    await usr.send('Опишите суть вашего спора')
    desc = await bot.wait_for('message', check=from_user)
    for m in members:
        if (m.name + '#' + m.discriminator) == opponent_tag.content:
            opponent = m
    await opponent.send(f'{usr.name} вызывает вас на спор. Сумма ставки {fee.content} тугриков. {desc.content}')
    await opponent.send(embed=discord.Embed(title='Вы согласны на условия спора?'), components=[[
        Button(style=ButtonStyle.green, label='Да'),
        Button(style=ButtonStyle.red, label='Нет')
    ]])
    dispute = Dispute(user1_id=usr.id, user2_id=opponent.id, description=desc.content,
                      amount=int(fee.content), status=DisputeStatus.CREATED, date=datetime.datetime.now())
    dispute.save()

    def from_opponent(m):
        return m.author == opponent
    res = await bot.wait_for('button_click', check=from_opponent)
    if res.component.label == 'Да':
        await usr.send(f'Спор c {opponent.name} начат!')
        await res.respond(content=f'Спор с {usr.name} начат!')
        await run_dispute(usr, opponent)
    else:
        await usr.send('Оппонент отклонил спор!')
        await res.respond(content='Спор отклонен!')


async def run_dispute(usr1, usr2):
    comps = []
    paySysList = (await src.chatex.getPaymentMethods())
    for i in range(5):
        comps.append(Button(style=ButtonStyle.gray, label=paySysList[i]['name']))
    await usr1.send(embed=discord.Embed(title='Выберите платежную систему'), components=[comps])
    await usr2.send(embed=discord.Embed(title='Выберите платежную систему'), components=[comps])


# @bot.command(name="start")
# async def start(ctx):
#     """
#     Start command. User begins interaction with the bot with this command.
#     """
#     await ctx.author.send('Введите тег пользователя, с которым вы хотите начать спор?')
#     members = ctx.guild.members
#     await dialog(ctx.author, members)

exec(open("tmp/admin.py", encoding="utf-8").read())

db_connect_url = os.environ.get('MONGO_LINK')

if db_connect_url is None:
    db_username = os.environ.get('MONGO_USERNAME')
    db_password = urllib.parse.quote(os.environ.get('MONGO_PASSWORD'))
    db_host = os.environ.get('MONGO_HOST')
    db_port = os.environ.get('MONGO_PORT')
    db_name = os.environ.get('MONGO_DATABASE')
    connect(host=f'mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}?authSource=admin')
else:
    connect(host=db_connect_url)

bot.run(os.environ.get('DISCORD_TOKEN'))

