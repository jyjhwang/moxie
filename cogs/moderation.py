import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from discord.ui import View, button, Button, Select

class RoleButton(Button):
    def __init__(self, role: discord.Role, styletype):
        super().__init__(style=styletype, label=role.name, custom_id=str(role.id))

    async def callback(self, ctx):
        role = ctx.guild.get_role(int(self.custom_id))
        if role is None:
            return
        elif role not in ctx.user.roles:
            await ctx.user.add_roles(role)
            await ctx.response.send_message(f'You added the role {role.mention}', ephemeral=True)
        else:
            await ctx.user.remove_roles(role)
            await ctx.response.send_message(f'You removed the role {role.mention}', ephemeral=True)

class Moderation(commands.Cog):
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
            await ctx.send_response(f'❌ ` PRUNED `  **{amount} MESSAGES.**', ephemeral=True)
        else:
            await ctx.channel.purge(limit=amount, check=specific_user)
            await ctx.send_response(f'❌ ` PRUNED `  **{amount} MESSAGES** FROM {user.mention}', ephemeral=True)

    async def select_rolegroup(self, guildid, rolegroupname):
        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM rolegroups_table WHERE guild_id = ? AND rolegroup_name = ?', (guildid, rolegroupname))
                rolegroup_info = await cursor.fetchone()
                return rolegroup_info

    @discord.slash_command(name='assign_roles', description='CREATE AN EMBED TO ASSIGN ROLES.')
    @commands.has_permissions(manage_roles=True)
    async def assign_roles(self, ctx, rolegroup: Option(str, 'for which role group?', required=True)):
        assign_view = View(timeout=None)
        selected_rolegroup = await self.select_rolegroup(ctx.guild.id, rolegroup)
        role_ids = selected_rolegroup[3].replace(' ', '').split(',')

        button_styles = [discord.ButtonStyle.blurple, discord.ButtonStyle.green, discord.ButtonStyle.red]
        for i, role_id in enumerate(role_ids):
            remainder = i % len(button_styles)
            role = ctx.guild.get_role(int(role_id))
            assign_view.add_item(RoleButton(role, button_styles[remainder]))

        assign_embed = discord.Embed(
            title = f'ASSIGN YOURSELF ROLES FOR \a**` {rolegroup} `**',
            color = int('2B2D31', base=16),
        )
        await ctx.send_response('_ _', ephemeral=True, delete_after=1)
        await ctx.send('_ _', embed=assign_embed, view=assign_view)

def setup(bot):
    bot.add_cog(Moderation(bot))