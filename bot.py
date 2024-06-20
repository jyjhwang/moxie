import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
activity = discord.Activity(type=discord.ActivityType.watching, name='over you.')
bot = discord.Bot(intents=intents, activity=activity, status=discord.Status.idle)

cogs_list = [
    'exporter',
    'moderation',
    'randomizer',
    'roster',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)