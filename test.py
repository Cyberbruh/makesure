import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from mongoengine import *

from src.dispute import *
from src.deposit import *
from src.payout import *
from src.proof import *

from src.chatex import *

load_dotenv()
connect(host="mongodb://127.0.0.1:27017/makesure")

d1 = Dispute(user1_id=21, user2_id=123, description="23", amount=12)
d1.save()
prof = Proof(description="1234", user_id=123, dispute=d1)
prof.save()
dep = Deposit(user_id=123, dispute=d1, method=1, payment_link="1234")
dep.save()
pay = Payout(dispute=d1, method=1, data="1234")
pay.save()