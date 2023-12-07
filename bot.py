import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)

activity = discord.Activity(type=discord.ActivityType.watching, name='over you.')
bot = discord.Bot(activity=activity, status=discord.Status.idle)

cogs_list = [
    'log',
    'moderation',
    'randomizer',
    'rolegroups',
    'roster',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)