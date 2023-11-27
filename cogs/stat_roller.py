import discord
import random
import aiosqlite
from discord.ext import commands
from discord.commands import Option

stat_array = ['CON', 'STR', 'DEX', 'INT', 'WIS', 'CHA']
stat_dict = {'CON': 5, 'STR': 6, 'DEX': 7, 'INT': 8, 'WIS': 9, 'CHA': 10}

class stat_roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Stat Roller COG loaded.')

    def error_embed_creator(self, error_message):
        error_embed = discord.Embed(
                title = '⚠️ \a ERROR',
                description = error_message,
                color = 16436582,
            )
        error_embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/newsfeed/001/690/562/921.png")
        return error_embed
    
    def calc_embed_creator(self, charaname, result, command_txt, calc_txt):
        calc_embed = discord.Embed(
            title = f'🎲 \a **` {charaname} `** \a ROLLED \a ' + f'**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a {command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a {calc_txt}',
            color = 15252813,
        )
        return calc_embed
    
    async def select_character(self, userid, guildid, charaname):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM characters WHERE user_id = ? AND guild_id = ? AND character_name = ?', (str(userid), str(guildid), str(charaname)))
                chara_info = await cursor.fetchone()
                return chara_info

    @discord.slash_command(name='roll_stat', description='ROLL WITH YOUR STATS.')
    async def roll_stat(self, ctx, character: Option(str, 'for which character?', required=True), stat: Option(str, 'for which stat?', choices=stat_array, required=True), amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), modifier: Option(int, 'modify the result?', required=False)):
        charaname_upper = character.upper()
        selected_character = await self.select_character(ctx.author.id, ctx.guild.id, charaname_upper)

        if not selected_character:
            error_embed = self.error_embed_creator('**` THIS CHARACTER COULD NOT BE FOUND. `**' + '\n\n' + f'❓ **` {charaname_upper} `** ` DOES NOT EXIST. `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)

        else:
            stat_column = stat_dict[stat]
            stat_modifier = selected_character[stat_column]
            if amount == 1:
                number = random.randint(1, sides)
                if not modifier:
                    result = number + stat_modifier
                    command_txt = f'**` D{sides} + ({stat_modifier}) `**'
                    calc_txt = f'` ({number}) + ({stat_modifier}) ` ` = ` **` ({result}) `**'

                    no_mod_embed = self.calc_embed_creator(charaname_upper, result, command_txt, calc_txt)
                    no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    no_mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=no_mod_embed)
                else:
                    result = number + stat_modifier + modifier
                    command_txt = f'**` D{sides} + ({stat_modifier}) `** **` + `** **` ({modifier}) `**'
                    calc_txt = f'` ({number}) + ({stat_modifier}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                    mod_embed = self.calc_embed_creator(charaname_upper, result, command_txt, calc_txt)
                    mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=mod_embed)
            else:
                rolled_dice = [random.randint(1, sides) for die in range(amount)]
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                sum_dice = sum(rolled_dice)
                if not modifier:
                    result = sum_dice + stat_modifier
                    command_txt = f'**` {amount} D{sides} + ({stat_modifier}) `**'
                    calc_txt = f'` ({rolled_dice_txt}) + ({stat_modifier}) ` ` = ` **` ({result}) `**'

                    no_mod_embed = self.calc_embed_creator(charaname_upper, result, command_txt, calc_txt)
                    no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    no_mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=no_mod_embed)
                else:
                    result = sum_dice + stat_modifier + modifier
                    command_txt = f'**` {amount} D{sides} + ({stat_modifier}) `** **` + `** **` ({modifier}) `**'
                    calc_txt = f'` ({rolled_dice_txt}) + ({stat_modifier}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                    mod_embed = self.calc_embed_creator(charaname_upper, result, command_txt, calc_txt)
                    mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=mod_embed)

def setup(bot):
    bot.add_cog(stat_roller(bot))