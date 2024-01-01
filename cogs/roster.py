import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import basic_embed_creator

class Roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    roster = SlashCommandGroup('roster', 'ROSTER.', guild_only=True, checks=[commands.has_permissions(manage_roles=True)])
    update_roster = roster.create_subgroup('update', 'UPDATE ROSTER.')
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Roster COG loaded.')

        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS roster_table (
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
    async def add(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), characolor: Option(str, 'CHARACTER COLOR', required=True), charaimg: Option(str, 'CHARACTER IMAGE', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('INSERT INTO roster_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (owner.id, owner.name, ctx.guild.id, ctx.guild.name, charaname.upper(), characolor, charaimg, constitution, strength, dexterity, wisdom, intelligence, charisma))
            await db.commit()
            roster_embed = basic_embed_creator(f'✅\a ` ADDED CHARACTER ` \a{charaname.upper()}')
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)
    
    @update_roster.command(name='stats', description='UPDATE CHARACTER STATS.')
    async def stats(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE roster_table SET character_con = ?, character_str = ?, character_dex = ?, character_wis = ?, character_int = ?, character_cha = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (constitution, strength, dexterity, wisdom, intelligence, charisma, owner.name, ctx.guild.id, charaname.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'🔄\a ` UPDATED CHARACTER STATS FOR ` \a{charaname.upper()}')
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)

    @update_roster.command(name='visuals', description='UPDATE CHARACTER VISUALS.')
    async def visuals(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True), characolor: Option(str, 'CHARACTER COLOR', required=True), charaimg: Option(str, 'CHARACTER IMAGE', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE roster_table SET character_color = ?, character_img = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (characolor, charaimg, owner.name, ctx.guild.id, charaname.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'🔄\a ` UPDATED CHARACTER VISUALS FOR ` \a{charaname.upper()}')
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)

    @roster.command(name='remove', description='REMOVE CHARACTER.')
    async def remove(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), charaname: Option(str, 'CHARACTER NAME', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM roster_table WHERE user_name = ? AND guild_id = ? AND character_name = ?', (owner.name, ctx.guild.id, charaname.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'❌\a ` REMOVED CHARACTER ` \a{charaname.upper()}')
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Roster(bot))