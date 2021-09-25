"""
Main entripoint of a bot.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


# Load variables from .env file
load_dotenv()

dialogs = []

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def start(ctx):
    """
    Start command. User begins interaction with the bot with this command.
    """
    
    await ctx.author.send(
        'Введите тег пользователя, с которым вы хотите начать спор?')
    dialogs.append(ctx.author)
    members = ctx.guild.members

    def check_right_user(member):
        return member.author == ctx.author

    msg = await bot.wait_for("message", check=check_right_user)
    for m in members:
        if (m.name + '#' + m.discriminator) == msg.content:
            await m.send('Бросаю перчатку!')


bot.run(os.environ.get('DISCORD_TOKEN'))
