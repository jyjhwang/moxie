import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

bot = discord.Bot()

class roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    roster = SlashCommandGroup('roster', 'ROSTER.', checks=[commands.has_permissions(administrator=True)])
    update_roster = roster.create_subgroup('update', 'UPDATE ROSTER.')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Roster COG loaded.')

        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS characters (
                    user_id INT,
                    user_name TEXT,
                    guild_id INT,
                    guild_name TEXT,
                    character_name TEXT,
                    character_color INT,
                    character_img TEXT,
                    stat_con INT,
                    stat_str INT,
                    stat_dex INT,
                    stat_wis INT,
                    stat_int INT,
                    stat_cha INT
                )''')
            await db.commit()

    @roster.command(name='add', description='ADD CHARACTER.')
    async def add(self, ctx, user: Option(discord.User, 'USER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), characolor: Option(str, 'CHARACTER COLOR', required=True), charaimg: Option(str, 'CHARACTER IMAGE', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(user.id), str(user.name), str(ctx.guild.id), str(ctx.guild.name), str(charaname), str(characolor), str(charaimg), str(constitution), str(strength), str(dexterity), str(wisdom), str(intelligence), str(charisma)))
            await db.commit()
            await ctx.send_response(f'ADDED CHARACTER **{charaname}**', ephemeral=True, delete_after=10)
    
    @update_roster.command(name='stats', description='UPDATE CHARACTER STATS.')
    async def stats(self, ctx, user: Option(discord.User, 'USER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE characters SET character_con = ?, character_str = ?, character_dex = ?, character_wis = ?, character_int = ?, character_cha = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(constitution), str(strength), str(dexterity), str(wisdom), str(intelligence), str(charisma), str(user.name), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'UPDATED CHARACTER **{charaname}** STATS', ephemeral=True, delete_after=10)

    @update_roster.command(name='visuals', description='UPDATE CHARACTER VISUALS.')
    async def visuals(self, ctx, user: Option(discord.User, 'USER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), characolor: Option(str, 'CHARACTER COLOR', required=True), charaimg: Option(str, 'CHARACTER IMAGE', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE characters SET character_color = ?, character_img = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(characolor), str(charaimg), str(user.name), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'UPDATED CHARACTER **{charaname}** VISUALS', ephemeral=True, delete_after=10)

    @roster.command(name='delete', description='DELETE CHARACTER.')
    async def delete(self, ctx, user: Option(discord.User, 'USER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM characters WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(user.name), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'DELETED CHARACTER **{charaname}**', ephemeral=True, delete_after=10)

def setup(bot):
    bot.add_cog(roster(bot))