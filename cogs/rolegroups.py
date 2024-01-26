import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import basic_embed_creator, error_embed_creator

class RoleGroups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rolegroups = SlashCommandGroup('rolegroups', 'ROLE GROUPS.', guild_only=True, checks=[commands.has_permissions(manage_roles=True)])
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('RoleGroups COG loaded.')

        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS rolegroups_table (
                    guild_id INT,
                    guild_name TEXT,
                    rolegroup_name TEXT,
                    role_ids TEXT
                )''')
            await db.commit()

    @rolegroups.command(name='add', description='ADD ROLE GROUP.')
    async def add(self, ctx, rolegroup_name: Option(str, 'role group name', required=True), role_ids: Option(str, 'separate out role IDs with commas ( , )', required=True)):
        if ',' not in role_ids:
            error_embed = error_embed_creator('**` SEPARATE OUT ROLE GROUP IDS WITH COMMAS. `**' + '\n\n' + '❌ ` role_id_1 role_id_2            `' + '\n' + '✅ ` role_id_1,role_id_2            `' + '\n' + '✅ ` role_id_1 , role_id_2          `' + '\n' + '✅ ` role_id_1, role_id_2, role_id_3  `')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            async with aiosqlite.connect('rolegroups.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('INSERT INTO rolegroups_table VALUES (?, ?, ?, ?)', (ctx.guild.id, ctx.guild.name, rolegroup_name.upper(), role_ids))
                await db.commit()
                rolegroup_embed = basic_embed_creator(f'✅\a ADDED ROLE GROUP \a` {rolegroup_name.upper()} `', None)
                await ctx.respond('_ _', embed=rolegroup_embed, ephemeral=True)

    @rolegroups.command(name='update', description='UPDATE ROLE GROUP.')
    async def update(self, ctx, rolegroup_name: Option(str, 'ROLE GROUP NAME', required=True), role_ids: Option(str, 'ROLES', required=True)):
        if ',' not in role_ids:
            error_embed = error_embed_creator('**` SEPARATE OUT ROLE GROUP IDS WITH COMMAS. `**' + '\n\n' + '❌ ` role_id_1 role_id_2            `' + '\n' + '✅ ` role_id_1,role_id_2            `' + '\n' + '✅ ` role_id_1 , role_id_2          `' + '\n' + '✅ ` role_id_1, role_id_2, role_id_3  `')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            async with aiosqlite.connect('rolegroups.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('UPDATE rolegroups_table SET role_ids = ? WHERE guild_id = ? AND rolegroup_name = ?', (role_ids, ctx.guild.id, rolegroup_name.upper()))
                await db.commit()
                rolegroup_embed = basic_embed_creator(f'🔄\a UPDATED ROLE GROUP \a` {rolegroup_name.upper()} `', None)
                await ctx.respond('_ _', embed=rolegroup_embed, ephemeral=True)

    @rolegroups.command(name='remove', description='REMOVE ROLE GROUPS.')
    async def remove(self, ctx, rolegroup_name: Option(str, 'role group name', required=True)):
        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM rolegroups_table WHERE guild_id = ? AND rolegroup_name = ?', (ctx.guild.id, rolegroup_name.upper()))
            await db.commit()
            rolegroup_embed = basic_embed_creator(f'❌\a REMOVED ROLE GROUP \a` {rolegroup_name.upper()} `', None)
            await ctx.respond('_ _', embed=rolegroup_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(RoleGroups(bot))