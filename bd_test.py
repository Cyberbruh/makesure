import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from mongoengine import *

from src.dispute import *
from src.deposit import *
from src.proof import *

from src.chatex import *

load_dotenv()
connect(host="mongodb://127.0.0.1:27017/makesure")

d1 = Dispute(user1_id=123, user2_id=345, description="23", amount=12, status=DisputeStatus.REPORTED)
d1.save()
prof = Proof(description="1234", user_id=123, dispute=d1)
prof.save()
prof = Proof(description="1212312334", user_id=345, dispute=d1)
prof.save()
dep = Deposit(user_id=123, dispute=d1, method=1, payment_url="1234")
dep.save()