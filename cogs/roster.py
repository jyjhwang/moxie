import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option

class roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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
                    character_con INT,
                    character_str INT,
                    character_dex INT,
                    character_wis INT,
                    character_int INT,
                    character_cha INT
                )''')
            await db.commit()
    
    @discord.slash_command(name='add_character', description='ADD CHARACTER.')
    async def add_character(self, ctx, userid: Option(str, 'USER ID', required=True), username: Option(str, 'USER NAME', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(userid), str(username), str(ctx.guild.id), str(ctx.guild.name), str(charaname), str(constitution), str(strength), str(dexterity), str(wisdom), str(intelligence), str(charisma)))
            await db.commit()
            await ctx.send_response(f'ADDED CHARACTER **{charaname}**', ephemeral=True)
    
    @discord.slash_command(name='update_character', description='UPDATE CHARACTER.')
    async def update_character(self, ctx, username: Option(str, 'DISCORD USERNAME', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE characters SET character_con = ?, character_str = ?, character_dex = ?, character_wis = ?, character_int = ?, character_cha = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(constitution), str(strength), str(dexterity), str(wisdom), str(intelligence), str(charisma), str(username), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'UPDATED CHARACTER **{charaname}**', ephemeral=True)

    @discord.slash_command(name='delete_character', description='DELETE CHARACTER.')
    async def delete_character(self, ctx, username: Option(str, 'DISCORD USERNAME', required=True), charaname: Option(str, 'CHARACTER NAME', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM characters WHERE user_name = ? AND guild_id = ? AND character_name = ?', (str(username), str(ctx.guild.id), str(charaname)))
            await db.commit()
            await ctx.send_response(f'DELETED CHARACTER **{charaname}**', ephemeral=True)

def setup(bot):
    bot.add_cog(roster(bot))