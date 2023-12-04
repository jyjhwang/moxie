import discord
from discord.ext import commands
from discord.commands import Option

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation COG loaded.')

    @discord.slash_command(name='prune', description='PRUNE MESSAGES.')
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: Option(int, 'how many messages?', min_value=1, required=True), user: Option(discord.User, 'from a specific user?', required=False)):
        def specific_user(message):
            return message.author == user
        if not user:
            await ctx.channel.purge(limit=amount)
            await ctx.send_response(f'PRUNED **{amount}** MESSAGES.', ephemeral=True, delete_after=10)
        else:
            await ctx.channel.purge(limit=amount, check=specific_user)
            await ctx.send_response(f'PRUNED **{amount}** MESSAGES FROM {user.mention}', ephemeral=True, delete_after=10)

def setup(bot):
    bot.add_cog(moderation(bot))