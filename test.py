import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from src.dispute import *
from src.deposit import *
from src.payout import *
from src.proof import *

load_dotenv()

db = MongoClient('mongodb://localhost:27017/').makesure
d1 = Dispute(db, 213, 123, "aDAWD", 123);
prof = Proof(db, d1, 123, "aDAWD");
dep = Deposit(db, 213, d1, 12);
pay = Payout(db, 213, d1, 1, "1234");
