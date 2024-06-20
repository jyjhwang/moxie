import discord
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import basic_embed_creator, error_embed_creator

stat_array = ['CON', 'STR', 'DEX', 'INT', 'WIS', 'CHA']
stat_dict = {'CON': 7, 'STR': 8, 'DEX': 9, 'INT': 10, 'WIS': 11, 'CHA': 12}

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

    @roster.command(name='list', description='List of characters in the roster.')
    async def list(self, ctx):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT user_id, character_name FROM roster_table WHERE guild_id = ?', ([ctx.guild.id]))
                rows = await cursor.fetchall()
                user_id_list = [row[0] for row in rows]
                character_name_list = [row[1] for row in rows]
            list_embed = discord.Embed(
                title = '🗃️\a ROSTER FOR \a' + f'**` {ctx.guild.name} `**',
                color = int('2B2D31', base=16),
            )
            owned_by_list = '\n'.join(f'<@{id}>' for id in user_id_list)
            character_list = '\n'.join(str(name) for name in character_name_list)
            list_embed.add_field(name='Character', value=character_list, inline=True)
            list_embed.add_field(name='Owned By', value=owned_by_list, inline=True)
            await ctx.respond('_ _', embed=list_embed, ephemeral=True)

    async def select_character(self, userid, guildid, charaname):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM roster_table WHERE user_id = ? AND guild_id = ? AND character_name = ?', (str(userid), str(guildid), str(charaname)))
                chara_info = await cursor.fetchone()
                return chara_info

    @roster.command(name='profile', description='Get a character\'s profile.')
    async def profile(self, ctx, owner: Option(discord.User, 'CHARACTER OWNER', required=True), chara_name: Option(str, 'CHARACTER NAME', required=True)):
        selected_character = await self.select_character(owner.id, ctx.guild.id, chara_name.upper())
        if not selected_character:
            error_embed = error_embed_creator('**` THIS CHARACTER COULD NOT BE FOUND. `**' + '\n\n' + f'❓\a **{chara_name.upper()}** \a` DOES NOT EXIST FOR ` {owner.mention}')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            hex_str = selected_character[5]
            chara_img = selected_character[6]
            profile_embed = discord.Embed(
                title = '👤\a PROFILE FOR \a' + f'**` {chara_name} `**',
                description = '👑\a **OWNED BY** \a' + f'{owner.mention}' + '\n',
                color = int(hex_str, base=16),
            )
            profile_embed.set_thumbnail(url=chara_img)
            profile_embed.add_field(name='CON', value=selected_character[7], inline=True)
            profile_embed.add_field(name='STR', value=selected_character[8], inline=True)
            profile_embed.add_field(name='DEX', value=selected_character[9], inline=True)
            profile_embed.add_field(name='INT', value=selected_character[10], inline=True)
            profile_embed.add_field(name='WIS', value=selected_character[11], inline=True)
            profile_embed.add_field(name='CHA', value=selected_character[12], inline=True)
            await ctx.respond('_ _', embed=profile_embed, ephemeral=True)

    @roster.command(name='add', description='Add a character to the roster.')
    async def add(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), chara_name: Option(str, 'CHARACTER NAME', required=True), chara_color: Option(str, 'CHARACTER COLOR', required=True), chara_img: Option(str, 'CHARACTER IMAGE', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('INSERT INTO roster_table VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (owner.id, owner.name, ctx.guild.id, ctx.guild.name, chara_name.upper(), chara_color, chara_img, constitution, strength, dexterity, wisdom, intelligence, charisma))
            await db.commit()
            roster_embed = basic_embed_creator(f'✅\a ` ADDED CHARACTER ` \a{chara_name.upper()}', None)
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)
    
    @roster.command(name='remove', description='Remove a character from the roster.')
    async def remove(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), chara_name: Option(str, 'CHARACTER NAME', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('DELETE FROM roster_table WHERE user_name = ? AND guild_id = ? AND character_name = ?', (owner.name, ctx.guild.id, chara_name.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'❌\a ` REMOVED CHARACTER ` \a{chara_name.upper()}', None)
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)
    
    @update_roster.command(name='stats', description='Update a character\'s stats.')
    async def stats(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), chara_name: Option(str, 'CHARACTER NAME', required=True), constitution: Option(int, 'CONSTITUTION', required=True), strength: Option(int, 'STRENGTH', required=True), dexterity: Option(int, 'DEXTERITY', required=True), wisdom: Option(int, 'WISDOM', required=True), intelligence: Option(int, 'INTELLIGENCE', required=True), charisma: Option(int, 'CHARISMA', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE roster_table SET character_con = ?, character_str = ?, character_dex = ?, character_wis = ?, character_int = ?, character_cha = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (constitution, strength, dexterity, wisdom, intelligence, charisma, owner.name, ctx.guild.id, chara_name.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'🔄\a ` UPDATED CHARACTER STATS FOR ` \a{chara_name.upper()}', None)
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)

    @update_roster.command(name='visuals', description='Update a character\'s visuals.')
    async def visuals(self, ctx, owner: Option(discord.Member, 'CHARACTER OWNER', required=True), chara_name: Option(str, 'CHARACTER NAME', required=True), chara_color: Option(str, 'CHARACTER COLOR', required=True), chara_img: Option(str, 'CHARACTER IMAGE', required=True)):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('UPDATE roster_table SET character_color = ?, character_img = ? WHERE user_name = ? AND guild_id = ? AND character_name = ?', (chara_color, chara_img, owner.name, ctx.guild.id, chara_name.upper()))
            await db.commit()
            roster_embed = basic_embed_creator(f'🔄\a ` UPDATED CHARACTER VISUALS FOR ` \a{chara_name.upper()}', None)
            roster_embed.add_field(name='', value=f'🆔\a ` OWNED BY ` \a{owner.mention}')
            await ctx.respond('_ _', embed=roster_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Roster(bot))