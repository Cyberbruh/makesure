import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime
from src.mongo import *

import src.mongo

load_dotenv()

db = MongoClient('mongodb://localhost:27017/').makesure

print(addDispute(db, {"user1": 123,
        "user2": 132,
        "description": "спор по кс",
        "amount": 123,
        "date": datetime.datetime.utcnow()}))


def addDispute(db, dispute):
    id = db.disputes.insert_one(dispute).inserted_id
    return id

