import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import error_embed_creator

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
            error_embed = error_embed_creator('**` SEPARATE OUT ROLE GROUPS WITH COMMAS. `**' + '\n\n' + '❌ ` /choose role_id_1 role_id_2            `' + '\n' + '✅ ` /choose role_id_1,role_id_2            `' + '\n' + '✅ ` /choose role_id_1 , role_id_2          `' + '\n' + '✅ ` /choose role_id_1, role_id_2, role_id_3  `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        else:
            async with aiosqlite.connect('rolegroups.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('INSERT INTO rolegroups_table VALUES (?, ?, ?, ?)', (ctx.guild.id, ctx.guild.name, rolegroup_name, role_ids))
                await db.commit()
                await ctx.send_response(f'ADDED ROLE GROUP **{rolegroup_name}**', ephemeral=True)

    @rolegroups.command(name='update', description='UPDATE ROLE GROUPS.')
    async def update(self, ctx, rolegroup_name: Option(str, 'ROLE GROUP NAME', required=True), role_ids: Option(str, 'ROLES', required=True)):
        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE characters SET character_color = ?, character_img = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(characolor), str(charaimg), str(user.name), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'UPDATED ROLE GROUP **{rolegroup_name}** VISUALS', ephemeral=True)

    @rolegroups.command(name='delete', description='DELETE ROLE GROUPS.')
    async def delete(self, ctx, rolegroup_name: Option(str, 'role group name', required=True)):
        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM rolegroups_table WHERE guild_id = ? AND rolegroup_name = ?', (ctx.guild.id, rolegroup_name))
            await db.commit()
            await ctx.send_response(f'DELETED ROLE GROUP **{rolegroup_name}**', ephemeral=True)

def setup(bot):
    bot.add_cog(RoleGroups(bot))