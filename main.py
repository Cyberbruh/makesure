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

@bot.command(name="admin")
async def admin(ctx):
    """
    Admin command. Admin starts to look up reported disputes
    """
    if "admin" in [y.name.lower() for y in ctx.author.roles]:
        while(Dispute.objects(Q(status=DisputeStatus.REPORTED) | Q(status=DisputeStatus.JUDGING)).count()):
            await startReportCheck(ctx)

async def startReportCheck(ctx):
    dispute = Dispute.objects(Q(status=DisputeStatus.REPORTED) | Q(status=DisputeStatus.JUDGING)).first()
    if dispute is None:
        return
    await ctx.author.send('Решаем спор номер:'+str(dispute.id))
    dispute.status = DisputeStatus.JUDGING;
    dispute.save()
    test_count = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute)).count()
    if(test_count == 0 or test_count > 1):
        raise Exception('Not enough or too many proofs for 1st user')
    proof1 = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 1')
    await ctx.author.send(proof1.description)
    test_count = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute)).count()
    if(test_count == 0 or test_count > 1):
        raise Exception('Not enough or too many proofs for 2nd user')
    proof2 = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 2')
    await ctx.author.send(proof2.description)
    await ctx.author.send(embed=discord.Embed(title='Решение?'), components=[[
        Button(style=ButtonStyle.green, label='Участник 1', custom_id=str(time.time() + 1)),
        Button(style=ButtonStyle.green, label='Участник 2', custom_id=str(time.time() + 2)),
        Button(style=ButtonStyle.green, label='Ничья', custom_id=str(time.time() + 3))
    ]])
    res = await bot.wait_for('button_click', check= lambda msg: (msg.author == ctx.author) & isinstance(msg.channel, discord.DMChannel))
    if res.component.label == 'Участник 1':
        result = 1
    elif res.component.label == 'Участник 2':
        result = 2
    else:
        result = 0
    await res.respond(content='Спор разрешён! Спасибо!')
    await solveDispute(result, dispute)

async def solveDispute(result, dispute):
    user1 = bot.get_user(dispute.user1_id)
    user2 = bot.get_user(dispute.user2_id)
    if(user1 is None or user2 is None):
        return
    deposit1 = Deposit.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute.id)).first()
    deposit2 = Deposit.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute.id)).first()
    print(user1)
    if(result == 1):
        payout = {
            "amount": deposit1.coin_amount + deposit2.coin_amount,
            "data": dispute.data1,
        }
        dispute.status = DisputeStatus.WIN1
        #dispute.save()
        await user1.send(f'Результат спора с {user2.name}: победил {user1.name}, приз уже отправлен!')
        await user2.send(f'Результат спора с {user1.name}: победил {user1.name}, приз уже отправлен!')
        await src.chatex.makePayout(payout)
    elif(result == 2):
        payout = {
            "amount": deposit1.coin_amount + deposit2.coin_amount,
            "data": dispute.data2,
        }
        dispute.status = DisputeStatus.WIN2
        #dispute.save()
        await user1.send(f'Результат спора с {user2.name}: победил {user2.name}, приз уже отправлен!')
        await user2.send(f'Результат спора с {user1.name}: победил {user2.name}, приз уже отправлен!')
        await src.chatex.makePayout(payout)
    else:
        payout1 = {
            "amount": deposit1.coin_amount,
            "data": dispute.data1,
        }
        payout2 = {
            "amount": deposit2.coin_amount,
            "data": dispute.data2,
        }
        dispute.status = DisputeStatus.TIE
        #dispute.save()
        await user1.send(f'Результат спора с {user2.name}: недостаточно доказательств => ничья, деньги возвращаются на аккаунты!')
        await user2.send(f'Результат спора с {user1.name}: недостаточно доказательств => ничья, деньги возвращаются на аккаунты!')
        await src.chatex.makePayout(payout1)
        await src.chatex.makePayout(payout2)

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