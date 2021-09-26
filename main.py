"""
Main entripoint of a bot.
"""

import os
import urllib
import discord
import asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
# from dotenv import load_dotenv
from datetime import datetime
import time
from mongoengine import connect, Q
import src.chatex

from src.dispute import Dispute, DisputeStatus
from src.proof import Proof
from src.deposit import Deposit, DepositStatus

# Load variables from .env file
# load_dotenv()


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
DiscordComponents(bot)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


def check_msg(msg, usr):
    """
    Check that message recieved from desired user in desired channel.
    """
    return (msg.author == usr) and isinstance(msg.channel, discord.DMChannel)


async def dialog(usr, phone1, members):
    """
    Dispute creation dialog.
    """

    check_msg_usr = lambda msg: check_msg(msg, usr)

    # Request opponent tag
    opponent_tag = await bot.wait_for("message", check=check_msg_usr)
    opponent = None

    # Request fee size
    await usr.send('Введите сумму вашего взноса')
    fee = await bot.wait_for('message', check=check_msg_usr)

    # Request dispute description
    await usr.send('Опишите суть вашего спора')
    desc = await bot.wait_for('message', check=check_msg_usr)

    # Get opponent user
    for m in members:
        if (m.name + '#' + m.discriminator) == opponent_tag.content:
            opponent = m

    # Propose dispute to the opponent
    await opponent.send(
        f'{usr.name} вызывает вас на спор. Сумма ставки {fee.content} тугриков. {desc.content}')
    await opponent.send(
        embed=discord.Embed(title='Вы согласны на условия спора?'), components=[[
            Button(style=ButtonStyle.green, label='Да'),
            Button(style=ButtonStyle.red, label='Нет')
        ]])
    
    # Create and save dispute object
    dispute = Dispute(
        user1_id=usr.id,
        user2_id=opponent.id,
        description=desc.content,
        amount=int(fee.content),
        status=DisputeStatus.CREATED,
        date=datetime.now())
    dispute.save()

    check_msg_opponent = lambda msg: check_msg(msg, opponent)

    # Process the opponent's response
    res = await bot.wait_for('button_click', check=check_msg_opponent)
    # If the opponent accepted the dispute
    if res.component.label == 'Да':
        dispute.status = DisputeStatus.ACCEPTED
        dispute.save()

        # Tell the users that dispute is accepted
        await usr.send(f'Спор c {opponent.name} начат!')
        await res.respond(content=f'Спор с {usr.name} начат!')

        # Request opponent's phone number
        await res.author.send(
            'Укажи, пожалуйста, свой номер телефона, привязанный к аккаунту в Chatex:')
        phone2 = (await bot.wait_for('message', check=check_msg_opponent)).content

        # Run dispute
        await run_dispute(usr, opponent, phone1, phone2, dispute)
    # Dispute is rejected
    else:
        dispute.status = DisputeStatus.REJECTED
        dispute.save()
        await usr.send('Оппонент отклонил спор!')
        await res.respond(content='Спор отклонен!')


async def run_dispute(usr1, usr2, phone1, phone2, dispute):
    """
    Runs the dispute: processes payments and claims.
    """
    
    # Wait for the payments
    await asyncio.gather(
        get_payment(usr1, dispute), get_payment(usr2, dispute))

    # Set phone numbers of the dispute
    dispute.data1 = str(phone1)
    dispute.data2 = str(phone2)
    dispute.save()

    # Wait for users' claims
    res1, res2 = await asyncio.gather(
        get_dispute_results(usr1, dispute), get_dispute_results(usr2, dispute))
    
    # Process different claims combinations
    if (res1 == 'Победитель') and (res2 == 'Проигравший'):
        dispute.status = DisputeStatus.WIN1
        dispute.save()
        await asyncio.gather(
            win(usr1, dispute, dispute.data1), lose(usr2, dispute))
    elif (res1 == 'Проигравший') and (res2 == 'Победитель'):
        dispute.status = DisputeStatus.WIN2
        dispute.save()
        await asyncio.gather(
            win(usr2, dispute, dispute.data1), lose(usr1, dispute))
    elif (res1 == 'Проигравший') and (res2 == 'Проигравший'):
        dispute.status = DisputeStatus.TIE
        dispute.save()
        await tie(usr1, usr2, dispute)
    else:
        # Both claimed their victory, need to investigate
        dispute.status = DisputeStatus.EVIDENCE
        dispute.save()
        await usr1.send('Один из игроков ответил нечестно. Спор отправлен в арбитраж. Отправьте в чат доказательства вашей правоты.')
        await usr2.send('Один из игроков ответил нечестно. Спор отправлен в арбитраж. Отправьте в чат доказательства вашей правоты.')

        # Wait for evidence
        await asyncio.gather(get_evidence(usr1, dispute), get_evidence(usr2, dispute))
        dispute.status = DisputeStatus.REPORTED
        dispute.save()


async def get_evidence(usr, dispute):
    """
    Requests payments
    """

    check_msg_usr = lambda msg: check_msg(msg, usr)

    # Wait for user response
    msg = await bot.wait_for('message', check=check_msg_usr)

    # Process proof materials
    att = msg.attachments
    res = msg.content
    for a in att:
        res += ' ' + a.url
    proof = Proof(user_id=usr.id, description=res, dispute=dispute)
    proof.save()

    # Notify user about success
    await usr.send(
        'Ваши доказательства приняты! Ожидайте решения судьи (в течение 24 часов)')


async def win(usr, dispute, data):
    """
    Process victory of a user.
    """

    # Congratulate the user
    await usr.send(f'Поздравляю, ты выиграл(а). Тебе будет перечислено {2*dispute.amount} тугриков.')

    # Make the payout
    dep = Deposit.objects(Q(user_id=usr.id) and Q(dispute=dispute.id)).first()
    payout = {
        "amount": dep.coin_amount * 2,
        "data": data,
    }
    await src.chatex.make_payout(payout)


async def lose(usr, dispute):
    await usr.send('К сожалению ты проиграл! Прости...')


async def tie(usr1, usr2, dispute):
    """
    Process the tie.
    """

    # Notify users about the tie
    await usr1.send('Ничья. Твои средства будут возвращены на твой аккаунт Chatex')
    await usr2.send('Ничья. Твои средства будут возвращены на твой аккаунт Chatex')

    # Make the payouts
    dep1 = Deposit.objects(Q(user_id=usr1.id) and Q(dispute=dispute.id)).first()
    dep2 = Deposit.objects(Q(user_id=usr2.id) and Q(dispute=dispute.id)).first()
    payout1 = {
        "amount": dep1.coin_amount,
        "data": dispute.data1,
    }
    payout2 = {
        "amount": dep2.coin_amount,
        "data": dispute.data2,
    }
    await src.chatex.make_payout(payout1)
    await src.chatex.make_payout(payout2)


async def get_dispute_results(usr, dispute):
    """
    Get user claims.
    """

    check_msg_usr = lambda msg: check_msg(msg, usr)

    # Request users to submit their claims
    await usr.send(embed=discord.Embed(title='После окончания спора укажите ваш статус по его итогам'), components=[[
        Button(style=ButtonStyle.green, label='Победитель', custom_id = str(time.time())),
        Button(style=ButtonStyle.red, label='Проигравший', custom_id=str(time.time() + 2))
    ]])
    res = await bot.wait_for('button_click', check=check_msg_usr)
    await res.respond(content='Ждем ответа вашего оппонента...')
    return res.component.label


async def get_payment(usr, dispute):
    """
    Process the payment.
    """

    check_msg_usr = lambda msg: check_msg(msg, usr)

    # Create a deposit
    dep = Deposit(user_id=usr.id, dispute=dispute)

    while dep.status != DepositStatus.SUCCESS:
        # Components
        components = []
        payment_methods = await src.chatex.get_payment_methods()

        # Request payment method from user
        # TODO: Rewrite that
        # Begin of govnocode
        ids = dict()
        for i in range(5):
            components.append(Button(style=ButtonStyle.grey, label=payment_methods[i]['name'], custom_id=str(time.time() + i)))
            ids[payment_methods[i]['name']] = payment_methods[i]['id']
        await usr.send(embed=discord.Embed(title='Выберите платежную систему'), components=[components])
        res = await bot.wait_for('button_click', check=check_msg_usr)
        dep.method = 347
        dep.save()
        # End of govnocode

        # Send payment link
        await res.respond(content=f'Перейдите по ссылке и проведите оплату взноса:')
        dep = await src.chatex.get_payment_link(dep)
        dep.save()
        await usr.send(dep.payment_url)

        # Request user payment confirmation
        await usr.send(embed=discord.Embed(title='Нажмите на кнопку для подтверждения оплаты'), components=[[Button(style=ButtonStyle.grey, label='Подтвердить', custom_id=str(time.time()))]])
        res = await bot.wait_for('button_click', check=check_msg_usr)
        if res.component.label == 'Подтвердить':
            # Check the payment
            await res.respond(content='Проверка оплаты...')
            dep = await src.chatex.update_payment(dep)
            dep.save()

            # Tell user the status of payment
            if dep.status != DepositStatus.SUCCESS:
                await usr.send(content='Оплата не удалась! Повторите попытку.')
            else:
                await usr.send(content='Оплата прошла успешно! Ожидание оплаты оппонента...')


@bot.command(name="start")
async def start(ctx):
    """
    Start command. User begins interaction with the bot using this command.
    """

    check_msg_usr = lambda msg: check_msg(msg, ctx.author)

    # Request phone number
    await ctx.author.send(
        'Привет! Я бот для заключения споров. Введи, пожалуйста, номер'
        + 'телефона, привязанный к твоему аккаунту в Chatex:')
    phone_number = (await bot.wait_for('message', check=check_msg_usr)).content

    # Request opponent's tag
    await ctx.author.send(
        'Введи тег пользователя, с которым вы хотите начать спор?')
    members = ctx.guild.members
    await dialog(ctx.author, phone_number, members)


@bot.command(name="admin")
async def admin(ctx):
    """
    Admin command. Admin starts to look up reported disputes
    """

    # If user has an admin role
    if "admin" in [y.name.lower() for y in ctx.author.roles]:
        # Search for unresolved cases
        while (Dispute.objects(
                Q(status=DisputeStatus.REPORTED)
                | Q(status=DisputeStatus.JUDGING)).count()):
            # Run conflict resolvment function
            await start_report_check(ctx)


async def start_report_check(ctx):
    """
    Conflict resolvment process.
    """

    check_msg_usr = lambda msg: check_msg(msg, ctx.author)

    # Select first unresolved dispute
    dispute = Dispute.objects(Q(status=DisputeStatus.REPORTED) | Q(status=DisputeStatus.JUDGING)).first()
    if dispute is None:
        return
    
    # Begin resolvment
    await ctx.author.send(f'Решаем спор {dispute.id}')
    dispute.status = DisputeStatus.JUDGING
    dispute.save()

    # Get the proofs
    test_count = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute.id)).count()
    if(test_count > 1):
        raise Exception(f'Too many proofs for the 1st user: {test_count}')
    if test_count == 0:
        temp = Proof(dispute=dispute, user_id=dispute.user1_id, description='No')
        temp.save()
    proof1 = Proof.objects(Q(user_id=dispute.user1_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 1')
    await ctx.author.send(proof1.description)

    test_count = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute.id)).count()
    if test_count > 1:
        raise Exception(f'Too many proofs for the 2nd user: {test_count}')
    if test_count == 0:
        temp = Proof(dispute=dispute, user_id=dispute.user2_id, description='No')
        temp.save()
    proof2 = Proof.objects(Q(user_id=dispute.user2_id) & Q(dispute=dispute.id)).first()
    await ctx.author.send('Участник 2')
    await ctx.author.send(proof2.description)

    # Make the decision
    await ctx.author.send(embed=discord.Embed(title='Решение?'), components=[[
        Button(style=ButtonStyle.green, label='Участник 1', custom_id=str(time.time() + 1)),
        Button(style=ButtonStyle.green, label='Участник 2', custom_id=str(time.time() + 2)),
        Button(style=ButtonStyle.green, label='Ничья', custom_id=str(time.time() + 3))
    ]])
    res = await bot.wait_for('button_click', check=check_msg_usr)
    if res.component.label == 'Участник 1':
        result = 1
    elif res.component.label == 'Участник 2':
        result = 2
    else:
        result = 0
    await res.respond(content='Спор разрешён! Спасибо!')
    await resolve_dispute(result, dispute)


async def resolve_dispute(result, dispute):
    """
    Fulfill the decision.
    """

    # Get users and deposits
    user1 = bot.get_user(dispute.user1_id)
    user2 = bot.get_user(dispute.user2_id)
    if(user1 is None or user2 is None):
        return
    deposit1 = Deposit.objects(Q(user_id=dispute.user1_id) and Q(dispute=dispute.id)).first()
    deposit2 = Deposit.objects(Q(user_id=dispute.user2_id) and Q(dispute=dispute.id)).first()
    
    if(result == 1):
        payout = {
            "amount": deposit1.coin_amount + deposit2.coin_amount,
            "data": dispute.data1,
        }
        dispute.status = DisputeStatus.WIN1
        dispute.save()
        await user1.send(f'Результат спора с {user2.name}: победил {user1.name}, приз уже отправлен!')
        await user2.send(f'Результат спора с {user1.name}: победил {user1.name}, приз уже отправлен!')
        await src.chatex.make_payout(payout)
    elif(result == 2):
        payout = {
            "amount": deposit1.coin_amount + deposit2.coin_amount,
            "data": dispute.data2,
        }
        dispute.status = DisputeStatus.WIN2
        dispute.save()
        await user1.send(f'Результат спора с {user2.name}: победил {user2.name}, приз уже отправлен!')
        await user2.send(f'Результат спора с {user1.name}: победил {user2.name}, приз уже отправлен!')
        await src.chatex.make_payout(payout)
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
        dispute.save()
        await user1.send(f'Результат спора с {user2.name}: недостаточно доказательств => ничья, деньги возвращаются на аккаунты!')
        await user2.send(f'Результат спора с {user1.name}: недостаточно доказательств => ничья, деньги возвращаются на аккаунты!')
        await src.chatex.make_payout(payout1)
        await src.chatex.make_payout(payout2)



db_connect_url = os.environ.get('MONGO_LINK')

# If mongo connect URL is not present, use individual variables
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
# get_payment()
