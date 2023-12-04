import discord
import random
import aiosqlite
from discord.ext import commands
from discord.commands import Option

stat_array = ['CON', 'STR', 'DEX', 'INT', 'WIS', 'CHA']
stat_dict = {'CON': 7, 'STR': 8, 'DEX': 9, 'INT': 10, 'WIS': 11, 'CHA': 12}

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
    
    def no_comment_embed_creator(self, charaname, characolor, charaimg, result, command_txt, calc_txt):
        no_comment_embed = discord.Embed(
            title = f'🎲 \a {charaname} ROLLED \a**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = characolor,
        )
        no_comment_embed.set_thumbnail(url=charaimg)
        return no_comment_embed
    
    def comment_embed_creator(self, charaname, characolor, charaimg, comment_txt, result, command_txt, calc_txt):
        comment_embed = discord.Embed(
            title = f'🎲 \a {charaname} ROLLED \a**`{result} `**' + '\n' + f'💬 \a **` {comment_txt} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = characolor,
        )
        comment_embed.set_thumbnail(url=charaimg)
        return comment_embed
    
    async def select_character(self, userid, guildid, charaname):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM characters WHERE user_id = ? AND guild_id = ? AND character_name = ?', (str(userid), str(guildid), str(charaname)))
                chara_info = await cursor.fetchone()
                return chara_info
            
    def stat_roll_helper(self, stat_modifier, amount, sides, modifier):
        if amount == 1:
            number = random.randint(1, sides)
            if not modifier:
                result = number + stat_modifier
                command_txt = f'**` D{sides} + ({stat_modifier}) `**'
                calc_txt = f'` ({number}) + ({stat_modifier}) ` ` = ` **` ({result}) `**'
                return result, command_txt, calc_txt
            else:
                result = number + stat_modifier + modifier
                command_txt = f'**` D{sides} + ({stat_modifier}) `** **` + `** **` ({modifier}) `**'
                calc_txt = f'` ({number}) + ({stat_modifier}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'
                return result, command_txt, calc_txt
        else:
            rolled_dice = [random.randint(1, sides) for die in range(amount)]
            rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
            sum_dice = sum(rolled_dice)
            if not modifier:
                result = sum_dice + stat_modifier
                command_txt = f'**` {amount} D{sides} + ({stat_modifier}) `**'
                calc_txt = f'` ({rolled_dice_txt}) + ({stat_modifier}) ` ` = ` **` ({result}) `**'
                return result, command_txt, calc_txt
            else:
                result = sum_dice + stat_modifier + modifier
                command_txt = f'**` {amount} D{sides} + ({stat_modifier}) `** **` + `** **` ({modifier}) `**'
                calc_txt = f'` ({rolled_dice_txt}) + ({stat_modifier}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'
                return result, command_txt, calc_txt

    @discord.slash_command(name='stat_roll', description='ROLL WITH YOUR STATS.')
    async def stat_roll(self, ctx, character: Option(str, 'for which character?', required=True), stat: Option(str, 'for which stat?', choices=stat_array, required=True), amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), modifier: Option(int, 'modify the result?', required=False), comment: Option(str, 'what are you rolling for?', required=False)):
        selected_character = await self.select_character(ctx.author.id, ctx.guild.id, character.upper())
        if not selected_character:
            error_embed = self.error_embed_creator('**` THIS CHARACTER COULD NOT BE FOUND. `**' + '\n\n' + f'❓ **` {character.upper()} `** ` DOES NOT EXIST. `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True, delete_after=10)
        else:
            stat_column = stat_dict[stat]
            stat_modifier = selected_character[stat_column]
            hex_str = selected_character[5]
            hex_int = int(hex_str, base=16)
            chara_img = selected_character[6]
            output_array = self.stat_roll_helper(stat_modifier, amount, sides, modifier)
            if not comment:
                no_comment_embed = self.no_comment_embed_creator(character.upper(), hex_int, chara_img, output_array[0], output_array[1], output_array[2])
                no_comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=no_comment_embed)
            else:
                comment_embed = self.comment_embed_creator(character.upper(), hex_int, chara_img, comment.upper(), output_array[0], output_array[1], output_array[2])
                comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=comment_embed)

def setup(bot):
    bot.add_cog(stat_roller(bot))