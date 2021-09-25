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

load_dotenv()
connect(host="mongodb://127.0.0.1:27017/makesure")

d1 = Dispute(user1_id=21, user2_id=123, description="23", amount=12)
d1.save()
#prof = Proof(db, d1, 123, "aDAWD")
#dep = Deposit(db, 213, d1, 12)
#pay = Payout(db, 213, d1, 1, "1234")
