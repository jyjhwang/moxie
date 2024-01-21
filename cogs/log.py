import discord
import numpy as np
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import basic_embed_creator, error_embed_creator, get_postID
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Log COG loaded.')

    @discord.slash_command(name='log', description='LOGS MESSAGES.', guild_only=True)
    @commands.has_permissions(read_message_history=True)
    async def log(self, ctx, file_type: Option(str, 'which file type?', choices=['HTML (Dark Mode)', 'HTML (Light Mode)', 'TXT (Plain)'], required=True), start_after: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', required=False), end_before: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', required=False)):
        loading_embed = basic_embed_creator('⏳ Processing messages... Please wait...')
        await ctx.respond('_ _', embed=loading_embed, ephemeral=True)
        start_postID = get_postID(start_after) if start_after else None
        end_postID = get_postID(end_before) if end_before else None
        export_command_str = f'dotnet DiscordChatExporter.Cli.dll export --token {DISCORD_TOKEN}'
        try:
            if file_type == 'HTML (Dark Mode)':
                export_command_str += f' --format HtmlDark'
            if file_type == 'HTML (Light Mode)':
                export_command_str += f' --format HtmlLight'
            if file_type == 'TXT (Plain)':
                export_command_str += f' --format PlainText'
            if start_postID:
                export_command_str += f' --after {start_postID}'
            if end_postID:
                export_command_str += f' --before {end_postID}'
            folder_path = os.path.join(os.getcwd(), 'DiscordChatExporter.Cli')
            exports_folder_path = folder_path + '/Exports'
            file_extension = file_type.split(' ')[0].lower()
            subprocess.run(f'{export_command_str} --channel {ctx.channel.id} --output {exports_folder_path}/%g_%c.{file_extension}', check=True, shell=True, cwd=folder_path)
            with open(f'{exports_folder_path}/{ctx.guild.id}_{ctx.channel.id}.{file_extension}', 'rb') as exported_file:
                await ctx.send('_ _', file=discord.File(exported_file, filename=f'{ctx.guild.name}_{ctx.channel.name}.{file_extension}'))
        except:
            error_embed = error_embed_creator('**` THESE MESSAGES COULD NOT BE FOUND. `**' + '\n\n' + f'❓ ` DID YOU INPUT A DISCORD MESSAGE LINK OR MESSAGE ID? `')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Log(bot))