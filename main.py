"""
Main entripoint of a bot.
"""

import os
import urllib
import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from dotenv import load_dotenv
from datetime import datetime
import time
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
    opponent_tag = await bot.wait_for("message", check= lambda msg: (msg.author == usr) & isinstance(msg.channel, discord.DMChannel))
    opponent = None
    await usr.send('Введите сумму вашего взноса')
    fee = await bot.wait_for('message', check= lambda msg: (msg.author == usr) & isinstance(msg.channel, discord.DMChannel))
    await usr.send('Опишите суть вашего спора')
    desc = await bot.wait_for('message', check= lambda msg: (msg.author == usr) & isinstance(msg.channel, discord.DMChannel))
    for m in members:
        if (m.name + '#' + m.discriminator) == opponent_tag.content:
            opponent = m
    await opponent.send(f'{usr.name} вызывает вас на спор. Сумма ставки {fee.content} тугриков. {desc.content}')
    await opponent.send(embed=discord.Embed(title='Вы согласны на условия спора?'), components=[[
        Button(style=ButtonStyle.green, label='Да'),
        Button(style=ButtonStyle.red, label='Нет')
    ]])
    dispute = Dispute(user1_id=usr.id, user2_id=opponent.id, description=desc.content,
                      amount=int(fee.content), status=DisputeStatus.CREATED, date=datetime.now())
    dispute.save()
    res = await bot.wait_for('button_click', check= lambda msg: (msg.author == opponent) & isinstance(msg.channel, discord.DMChannel))
    if res.component.label == 'Да':
        await usr.send(f'Спор c {opponent.name} начат!')
        await res.respond(content=f'Спор с {usr.name} начат!')
        await run_dispute(usr, opponent, dispute)
    else:
        await usr.send('Оппонент отклонил спор!')
        await res.respond(content='Спор отклонен!')


async def run_dispute(usr1, usr2, dispute):

    #tasks = [asyncio.create_task(get_payment(usr1, dispute)), asyncio.create_task(get_payment(usr2, dispute))]
    #await asyncio.wait(tasks)
    #tasks = [asyncio.create_task(get_dispute_results(usr1, dispute)), asyncio.create_task(get_dispute_results(usr2, dispute))]
    #await asyncio.wait(tasks)
    await asyncio.gather(get_payment(usr1, dispute), get_payment(usr2, dispute))
    if (tasks[0].result() == 'Победитель') & (tasks[1].result() == 'Проигравший'):
        await end_dispute(usr1, usr2, dispute)
    elif (tasks[0].result() == 'Проигравший') & (tasks[0].result() == 'Победитель'):
        await end_dispute(usr2, usr1, dispute)
    elif (tasks[0].result() == 'Проигравший') & (tasks[0].result() == 'Проигравший'):
        await return_fee(usr1, usr2, dispute)
    else:
        await judge(usr1, usr2, dispute)

async def judge(usr1, usr2, dispute):
    pass

async def end_dispute(winner, loser, dispute):
    pass

async def return_fee(usr1, usr2, dispute):
    pass

async def get_dispute_results(usr, dispute):
    await usr.send(embed=discord.Embed(title='После окончания спора укажите ваш статус по его итогам'), components=[[
        Button(style=ButtonStyle.green, label='Победитель'),
        Button(style=ButtonStyle.red, label='Проигравший')
    ]])
    usr.send('Ждем ответа вашего оппонента...')
    return (await bot.wait_for('button_click', check= lambda msg: (msg.author == usr) & isinstance(msg.channel, discord.DMChannel))).label

async def get_payment(usr, dispute):
    dep = Deposit(user_id=usr.id, dispute=dispute)
    while dep.status != DisputeStatus.ACCEPTED:
        comps = []
        paySysList = await src.chatex.getPaymentMethods()
        ids = dict()
        for i in range(5):
            comps.append(Button(style=ButtonStyle.gray, label=paySysList[i]['name'], custom_id=str(time.time() + i)))
            ids[paySysList[i]['name']] = paySysList[i]['id']
        await usr.send(embed=discord.Embed(title='Выберите платежную систему'), components=[comps])
        res = await bot.wait_for('button_click', check= lambda msg: (msg.author == usr) & isinstance(msg.channel, discord.DMChannel))
        dep.method = 347
        await res.respond(content=f'Перейдите по ссылке и проведите оплату взноса:')
        dep = await src.chatex.getPaymentLink(dep)
        await usr.send(dep.payment_url)
        await usr.send(embed=discord.Embed(title='Нажмите на кнопку для подтверждения оплаты'), components=[[Button(style=ButtonStyle.grey, label='Подтвердить', custom_id=str(time.time()))]])
        res = await bot.wait_for('button_click', check= lambda msg: msg.author == usr)
        if res.component.label == 'Подтвердить':
            await res.respond(content='Проверка оплаты...')
            dep = await src.chatex.updatePayment(dep)
            if dep.status != DepositStatus.SUCCESS:
                await usr.send(content='Оплата не удалась! Повторите попытку.')
            else:
                await usr.send(content='Оплата прошла успешно!')


@bot.command(name="start")
async def start(ctx):
    """
    Start command. User begins interaction with the bot with this command.
    """
    await ctx.author.send('Введите тег пользователя, с которым вы хотите начать спор?')
    members = ctx.guild.members
    await dialog(ctx.author, members)

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