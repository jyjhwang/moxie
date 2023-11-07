import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents().all()
client = discord.Client(intents=intents)

bot = discord.Bot()

cogs_list = [
    'randomizer',
    'roster',
    'stat_roller',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)