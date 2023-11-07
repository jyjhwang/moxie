import discord
import random
import aiosqlite
from discord.ext import commands
from discord.commands import Option

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
    
    def calc_embed_creator(self, result, command_txt, calc_txt):
        calc_embed = discord.Embed(
            title = '🎲 \a YOU ROLLED \a ' + f'**` {result} `**',
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

    @discord.slash_command(name='roll_con', description='ROLL CONSTITUTION.')
    async def roll_con(self, ctx, character: Option(str, 'for which character?', required=True), amount: Option(int, 'how many dice?', required=True), sides: Option(int, 'how many sides to each die?', required=True), modifier: Option(int, 'modify the result?', required=False)):
        charaname_upper = character.upper()
        selected_character = await self.select_character(ctx.author.id, ctx.guild.id, charaname_upper)
        
        if amount == 0:
            error_embed = self.error_embed_creator('**` YOU ROLLED ZERO DICE. `**' + '\n\n' + '❌ ` /roll 0d20 `' + '\n' + '✅ ` /roll 1d20 `' + '\n' + '✅ ` /roll 2d20 `' + '\n' + '✅ ` /roll 3d20 `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        elif sides == 0:
            error_embed = self.error_embed_creator('**` A DIE CANNOT HAVE ZERO SIDES. `**' + '\n\n' + '❌ ` /roll 1d0  `' + '\n' + '✅ ` /roll 1d1  `' + '\n' + '✅ ` /roll 1d2  `' + '\n' + '✅ ` /roll 1d20 `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        elif not selected_character:
            error_embed = self.error_embed_creator('**` CHARACTER INFO COULD NOT BE FOUND. `**' + '\n\n' + '❓ ` PLEASE ASK FOR HELP `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)

        else:
            stat_modifier = selected_character[5]
            if abs(amount) == 1:
                number = random.randint(1, abs(sides))
                if not modifier:
                    result = number + stat_modifier
                    command_txt = f'**` D{abs(sides)} `** **` + `** **` ({stat_modifier}) `**'
                    calc_txt = f'` ({number}) ` ` + ` ` ({stat_modifier}) ` ` = ` **` ({result}) `**'

                    no_mod_embed = self.calc_embed_creator(result, command_txt)
                    no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    no_mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=no_mod_embed)
                else:
                    result = number + modifier
                    command_txt = f'**` D{abs(sides)} `** **` + `** **` ({modifier}) `**'
                    calc_txt = f'` ({number}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                    mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                    mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=mod_embed)
            else:
                rolled_dice = [random.randint(1, abs(sides)) for die in range(abs(amount))]
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                result = sum(rolled_dice)
                if not modifier:
                    command_txt = f'**` {abs(amount)} `** **` D{abs(sides)} `**'
                    calc_txt = f'` ({rolled_dice_txt}) ` ` = ` **` ({result}) `**'

                    no_mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                    no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    no_mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=no_mod_embed)
                else:
                    command_txt = f'**` {abs(amount)} `** **` D{abs(sides)} `** **` + `** **` ({modifier}) `**'
                    calc_txt = f'` ({rolled_dice_txt}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                    mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                    mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                    mod_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
                    await ctx.send('_ _', embed=mod_embed)

def setup(bot):
    bot.add_cog(stat_roller(bot))