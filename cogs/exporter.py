import discord
import re
import numpy as np
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import basic_embed_creator, error_embed_creator, get_postID
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

class Exporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    export = SlashCommandGroup('export', 'EXPORTS MESSAGES.')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Exporter COG loaded.')

    def word_counter(self, string):
        words = re.findall('[a-zA-Z0-9]+(?:\'[a-zA-Z0-9]+)?', string)
        return len(words)
    
    def word_or_words(self, count):
        return 'word' if count == 1 else 'words'
    
    def attachment_or_attachments(self, count):
        return 'attachment' if count == 1 else 'attachments'
    
    def message_or_messages(self, count):
        return 'message' if count == 1 else 'messages'

    @export.command(name='overview', description='AN OVERVIEW OF THE EXPORT.', guild_only=True)
    @commands.has_permissions(read_message_history=True)
    async def overview(self, ctx, private: Option(str, 'only visible to you (TRUE) or visible to everyone (FALSE)', choices=['True', 'False'], required=True)):
        participants, textlog = [], []
        all_word_count, all_attachment_count, all_message_count = 0, 0, 0
        self.participant_word_counts = {}
        self.participant_attachments = {}
        async for message in ctx.channel.history(limit=None, oldest_first=True):
            all_message_count += 1
            embed_word_count = 0
            if message.clean_content:
                all_word_count += self.word_counter(message.clean_content)
            for embed in message.embeds:
                if embed.title:
                    embed_word_count += self.word_counter(embed.title)
                    all_word_count += self.word_counter(embed.title)
                if embed.description:
                    embed_word_count += self.word_counter(embed.description)
                    all_word_count += self.word_counter(embed.description)
                if embed.fields:
                    for field in embed.fields:
                        embed_word_count += self.word_counter(field.name)
                        embed_word_count += self.word_counter(field.value)
                        all_word_count += self.word_counter(field.name)
                        all_word_count += self.word_counter(field.value)
            if not message.author.bot and not message.webhook_id:
                participant = message.author.mention
            else:
                participant = message.author.display_name
            participants.append(participant)
            textlog.append(message.clean_content)
            attachment_count = len(message.attachments)
            all_attachment_count += attachment_count
            if participant not in self.participant_attachments:
                self.participant_attachments[participant] = 0
            self.participant_attachments[participant] += attachment_count
            if participant not in self.participant_word_counts:
                self.participant_word_counts[participant] = 0
            self.participant_word_counts[participant] += embed_word_count
            self.participant_word_counts[participant] += self.word_counter(message.clean_content)
        unique_participants = np.unique(participants)
        output = f'{textlog}'
        embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}'
        info_embed = discord.Embed(
            title = '📠\a Export Overview',
            description = f'<#{ctx.channel.id}>\a `({all_message_count} {self.message_or_messages(all_message_count)})`' + '\n' + f'📝\a `({all_word_count} {self.word_or_words(all_word_count)})` `({all_attachment_count} {self.attachment_or_attachments(all_attachment_count)})`' + '\n' + f'{output}',
            color = int('2B2D31', base=16),
            url = embed_link,
        )
        info_embed.add_field(name='', value='', inline=False)
        participant_info = []
        for participant, word_count in self.participant_word_counts.items():
            attachment_count = self.participant_attachments.get(participant, 0)
            participant_info.append(f'{participant} `({word_count} {self.word_or_words(word_count)})` `({attachment_count} {self.attachment_or_attachments(attachment_count)})`')
        info_embed.add_field(
            name=f'Participants `({len(unique_participants)})`',
            value='\n'.join(participant_info),
            inline=False
        )
        bool_map = {
            'True': True,
            'False': False
        }
        private = bool_map.get(private, None)
        await ctx.respond('_ _', embed=info_embed, ephemeral=private)

    @export.command(name='file', description='EXPORTS A FILE OF DISCORD MESSAGES.', guild_only=True)
    @commands.has_permissions(read_message_history=True)
    async def file(self, ctx, file_type: Option(str, 'which file type?', choices=['HTML (Dark Mode)', 'HTML (Light Mode)', 'TXT (Plain)'], required=True), start_after: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID of the message BEFORE the first one you want.', required=False), end_before: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID of the message AFTER the last one you want.', required=False)):
        loading_embed = basic_embed_creator('⏳\a Processing messages... Please wait...', '📸\a **REMINDER!** \aMedia files (images, videos, etc.) in these exports are linked to Discord, and those links will break over time.' + '\n\n' + 'For HTML exports, one quick workaround is to open the HTML file in Chrome, right-click on the webpage, and then choose `Save As...` to save the file again. By doing so, a folder with the images will be locally saved to your computer.')
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

            embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}'
            completion_embed = discord.Embed(
                title = '📠\a Your messages have been exported!',
                description = f'🆔\a {ctx.author.mention}',
                color = int('2B2D31', base=16),
                url = embed_link,
            )

            subprocess.run(f'{export_command_str} --channel {ctx.channel.id} --output {exports_folder_path}/%g_%c.{file_extension} -p 20mb', check=True, shell=True, cwd=folder_path)
            with open(f'{exports_folder_path}/{ctx.guild.id}_{ctx.channel.id}.{file_extension}', 'rb') as exported_file:
                await ctx.send('_ _', embed=completion_embed, file=discord.File(exported_file, filename=f'{ctx.guild.name}_{ctx.channel.name}.{file_extension}'))
            
            os.remove(f'{exports_folder_path}/{ctx.guild.id}_{ctx.channel.id}.{file_extension}')
        except:
            error_embed = error_embed_creator('**` THESE MESSAGES COULD NOT BE FOUND. `**' + '\n\n' + f'❓ ` DID YOU INPUT A DISCORD MESSAGE LINK OR MESSAGE ID? `')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Exporter(bot))