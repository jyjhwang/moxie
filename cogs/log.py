import discord
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
        return link.split('/').at(-1)
            

    @discord.slash_command(name='log', description='LOGS MESSAGES.', guild_only=True)
    @commands.has_permissions(read_message_history=True)
    async def log(self, ctx, thread: Option(discord.Thread, 'UNARCHIVED DISCORD THREAD', required=True), start: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', default=None), end: Option(str, 'COPY MESSAGE LINK OR MESSAGE ID', default=None), limit: Option(int, 'only how many messages?', min_value=1, required=False)):
        if start and end:
            start_postID = self.get_postID(start)
            end_postID = self.get_postID(start)
        elif start:
            start_postID = self.get_postID(start)
        elif end:
            end_postID = self.get_postID(start)
        try:
            if start_postID:
                start_msg = await discord.get_message(start_postID)
            if end_postID:
                end_msg = await discord.get_message(end_postID)
        except:
            error_embed_creator('**` THESE MESSAGES COULD NOT BE FOUND. `**' + '\n\n' + f'❓ ` DID YOU INPUT A DISCORD MESSAGE LINK OR MESSAGE ID? `')
        if not limit:
            limit = None

        all_messages = [message async for message in thread.history(limit=limit, before=end_msg, after=start_msg)]
        
        await ctx.send_response(all_messages)

def setup(bot):
    bot.add_cog(Log(bot))