import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from mongoengine import *
import requests

from src.dispute import *
from src.deposit import *
from src.payout import *
from src.proof import *

from src.chatex import *
import asyncio

load_dotenv()

connect(host="mongodb://127.0.0.1:27017/makesure")
dispute = Dispute.objects(id="614f0d7418a09708c0b5075e").first()
dep = Deposit(user_id=123, dispute=dispute, method=1, payment_link="1234")
dep.save()

async def main():
    print(await getPaymentLink(dep))
asyncio.run(main())