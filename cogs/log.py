import discord
import numpy as np
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import error_embed_creator

class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Log COG loaded.')

    def get_postID(self, link):
        return link.split('/')[-1]

    @discord.slash_command(name='log', description='LOGS MESSAGES.', guild_only=True)
    @commands.has_permissions(read_message_history=True)
    async def log(self, ctx, thread: Option(discord.Thread, 'UNARCHIVED DISCORD THREAD', required=True), start: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', default=None), end: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', default=None), limit: Option(int, 'only how many messages?', min_value=1, default=None)):
        start_postID = self.get_postID(start) if start else None
        end_postID = self.get_postID(end) if end else None
        try:
            if start_postID:
                start = await discord.get_message(start_postID)
            if end_postID:
                end = await discord.get_message(end_postID)
        except:
            error_embed_creator('**` THESE MESSAGES COULD NOT BE FOUND. `**' + '\n\n' + f'❓ ` DID YOU INPUT A DISCORD MESSAGE LINK OR MESSAGE ID? `')

        participants = []
        textlog = []
        async for msg in thread.history(limit=limit, after=start, before=end, oldest_first=True):
            participants.append(msg.author.name)
            textlog.append(msg.clean_content)
        unique_participants = np.unique(participants)
        output = f'{unique_participants}' + '\n' + f'{textlog}'
        await ctx.send_response(output)

def setup(bot):
    bot.add_cog(Log(bot))