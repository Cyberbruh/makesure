import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from src.dispute import *

import src.mongo

load_dotenv()

db = MongoClient('mongodb://localhost:27017/').makesure
test = Dispute(db, 213, 123, "aDAWD", 123);