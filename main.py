"""
Main entripoint of a bot.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from mongoengine import connect

from src.dispute import Dispute, DisputeStatus



# Load variables from .env file
load_dotenv()

dialogs = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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
    await opponent.send('Вы согласны? Да/Нет')
    dispute = Dispute(user1_id=usr.id, user2_id=opponent.id, description=desc.content,
                      amount=int(fee.content), status=DisputeStatus.CREATED, date=datetime.datetime.now())
    dispute.save()

    def from_opponent(m):
        return m.author == opponent
    res = await bot.wait_for('message', check=from_opponent)
    if res.content == 'Да':
        await usr.send('Спор c {opponent.name} начат!')
        await opponent.send('Спор с {usr.name} начат!')


@bot.command()
async def start(ctx):
    """
    Start command. User begins interaction with the bot with this command.
    """
    await ctx.author.send('Введите тег пользователя, с которым вы хотите начать спор?')
    members = ctx.guild.members
    await dialog(ctx.author, members)

db_username = os.environ.get('MONGO_USERNAME')
db_password = os.environ.get('MONGO_PASSWORD')
db_host = os.environ.get('MONGO_HOST')
db_port = os.environ.get('MONGO_PORT')
db_name = os.environ.get('MONGO_DATABASE')
connect(host=f'mongodb://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')
bot.run(os.environ.get('DISCORD_TOKEN'))
