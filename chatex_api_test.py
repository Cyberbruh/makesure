import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from mongoengine import *
import requests

from src.dispute import *
from src.deposit import *
from src.proof import *

from src.chatex import *
import asyncio

load_dotenv()

connect(host="mongodb://127.0.0.1:27017/makesure")

async def main():
    dispute = Dispute.objects().first()
    dep = Deposit(user_id=123, dispute=dispute, method=347)
    dep.save()
    dep = await get_payment_link(dep)
    print(dep.payment_url, dep.id)

async def main2():
    dep = Deposit.objects(id="614f7a1dd8cd5d1f1f52b69b").first()
    dep = await update_payment(dep)
    print(dep.status)

# asyncio.run(payout())