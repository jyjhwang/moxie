import discord
import random
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from utils import error_embed_creator

stat_array = ['CON', 'STR', 'DEX', 'INT', 'WIS', 'CHA']
stat_dict = {'CON': 7, 'STR': 8, 'DEX': 9, 'INT': 10, 'WIS': 11, 'CHA': 12}

class Randomizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    roll = SlashCommandGroup('roll', 'ROLLS DICE.')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Randomizer COG loaded.')
    
    def choice_embed_creator(self, result_txt, choices_txt):
        choice_embed = discord.Embed(
                title = '🎯 \a YOU CHOSE \a' + f'**` {result_txt} `**',
                description = f'🏹 \a **FROM THE CHOICES** \a{choices_txt}',
                color = int('2B2D31', base=16),
            )
        return choice_embed

    @discord.slash_command(name='choose', description='CHOOSE WISELY.')
    async def choose(self, ctx, choices: Option(str, 'separate out choices with vertical bars ( | )', required=True)):
        if '|' not in choices:
            error_embed = error_embed_creator('**` SEPARATE OUT CHOICES WITH VERTICAL BARS. `**' + '\n\n' + '❌ ` /choose choice1 choice2            `' + '\n' + '✅ ` /choose choice1|choice2            `' + '\n' + '✅ ` /choose choice1 | choice2          `' + '\n' + '✅ ` /choose choice1| choice2| choice3  `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        else:
            choices_array = choices.split('|')
            choices_format = [f'**` {choice.strip().upper()} `**' for choice in choices_array]
            result_txt = random.choice(choices).strip().upper()
            choices_txt = ' \a'.join(choices_format)

            choice_embed = self.choice_embed_creator(result_txt, choices_txt)
            choice_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
            choice_embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send_response('_ _', ephemeral=True, delete_after=1)
            await ctx.send('_ _', embed=choice_embed)

    def pos_or_neg(self, value):
        if value >= 0:
            return f'+{value}'
        else:
            return f'{value}'
    
    def simple_embed_creator(self, result, command_txt):
        simple_embed = discord.Embed(
            title = f'🎲 \a YOU ROLLED \a**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}',
            color = int('2B2D31', base=16),
        )
        return simple_embed
    
    def simple_comment_embed_creator(self, comment_txt, result, command_txt):
        simple_comment_embed = discord.Embed(
            title = f'🎲 \a YOU ROLLED \a**` {result} `**' + '\n' + f'💬 \a **` {comment_txt} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}',
            color = int('2B2D31', base=16),
        )
        return simple_comment_embed
    
    def calc_embed_creator(self, result, command_txt, calc_txt):
        calc_embed = discord.Embed(
            title = f'🎲 \a YOU ROLLED \a**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = int('2B2D31', base=16),
        )
        return calc_embed
    
    def calc_comment_embed_creator(self, comment_txt, result, command_txt, calc_txt):
        calc_comment_embed = discord.Embed(
            title = f'🎲 \a YOU ROLLED \a**` {result} `**' + '\n' + f'💬 \a **` {comment_txt} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = int('2B2D31', base=16),
        )
        return calc_comment_embed
    
    def roll_helper(self, amount, sides, apply, modifier):
        if amount == 1:
            number = random.randint(1, sides)
            if modifier:
                modifier_str = self.pos_or_neg(modifier)
                result = number + modifier
                command_txt = f'**` D{sides} `** **` ( {modifier_str} ) `**'
                calc_txt = f'` ({number}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ( {modifier_str} ) `'
                return result, command_txt, calc_txt
            else:
                command_txt = f'**` D{sides} `**'
                return number, command_txt
        else:
            rolled_dice = [random.randint(1, sides) for die in range(amount)]
            result = sum(rolled_dice)
            if apply:
                if apply == 'ADVANTAGE':
                    apply_roll = max(rolled_dice)
                elif apply == 'DISADVANTAGE':
                    apply_roll = min(rolled_dice)
                rolled_dice_txt = ' ` ` '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result = apply_roll + modifier
                    command_txt = f'**` {amount} D{sides} `** **` {apply} `** **` ( {modifier_str} ) `**'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ( {modifier_str} ) `'
                    return result, command_txt, calc_txt
                else:
                    command_txt = f'**` {amount} D{sides} `** **` {apply} `**'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `'
                    return apply_roll, command_txt, calc_txt
            else:
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result += modifier
                    command_txt = f'**` {amount} D{sides} `** **` ( {modifier_str} ) `**'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ( {modifier_str} ) `'
                    return result, command_txt, calc_txt
                else:
                    command_txt = f'**` {amount} D{sides} `**'
                    calc_txt = f'` ({rolled_dice_txt}) ` ` = ` **` ({result}) `**'
                    return result, command_txt, calc_txt

    @roll.command(name='dice', description='ROLLS DICE.')
    async def dice(self, ctx, amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), apply: Option(str, 'advantage or disdvantage?', choices=['ADVANTAGE', 'DISADVANTAGE'], required=False), modifier: Option(int, 'modify the result?', required=False), comment: Option(str, 'what are you rolling for?', required=False)):
        output_array = self.roll_helper(amount, sides, apply, modifier)
        if amount == 1 and not modifier:
            if not comment:
                simple_embed = self.simple_embed_creator(output_array[0], output_array[1])
                simple_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                simple_embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=simple_embed)
            else:
                simple_comment_embed = self.simple_comment_embed_creator(str(comment.upper()), output_array[0], output_array[1])
                simple_comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                simple_comment_embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=simple_comment_embed)
        elif not comment:
            no_comment_embed = self.calc_embed_creator(output_array[0], output_array[1], output_array[2])
            no_comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
            no_comment_embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send_response('_ _', ephemeral=True, delete_after=1)
            await ctx.send('_ _', embed=no_comment_embed)
        else:
            comment_embed = self.calc_comment_embed_creator(str(comment.upper()), output_array[0], output_array[1], output_array[2])
            comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
            comment_embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send_response('_ _', ephemeral=True, delete_after=1)
            await ctx.send('_ _', embed=comment_embed)
    
    def no_comment_embed_creator(self, charaname, characolor, charaimg, charastat, result, command_txt, calc_txt):
        no_comment_embed = discord.Embed(
            title = f'🎲 \a {charaname} ROLLED \a**` {result} `** \aFOR {charastat}',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = characolor,
        )
        no_comment_embed.set_thumbnail(url=charaimg)
        return no_comment_embed
    
    def comment_embed_creator(self, charaname, characolor, charaimg, charastat, comment_txt, result, command_txt, calc_txt):
        comment_embed = discord.Embed(
            title = f'🎲 \a {charaname} ROLLED \a**` {result} `** \aFOR {charastat}' + '\n' + f'💬 \a **` {comment_txt} `**',
            description = f'🎰 \a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a{calc_txt}',
            color = characolor,
        )
        comment_embed.set_thumbnail(url=charaimg)
        return comment_embed
    
    async def select_character(self, userid, guildid, charaname):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM roster_table WHERE user_id = ? AND guild_id = ? AND character_name = ?', (str(userid), str(guildid), str(charaname)))
                chara_info = await cursor.fetchone()
                return chara_info
            
    def stat_roll_helper(self, stat, stat_modifier, amount, sides, apply, modifier):
        stat_modifier_str = self.pos_or_neg(stat_modifier)
        if amount == 1:
            number = random.randint(1, sides)
            if modifier:
                modifier_str = self.pos_or_neg(modifier)
                result = number + stat_modifier + modifier
                command_txt = f'**` D{sides} `** **` ({stat_modifier_str} {stat}) `** **` ( {modifier_str} ) `**'
                calc_txt = f'` ({number}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) ` ` ( {modifier_str} ) `'
                return result, command_txt, calc_txt
            else:
                result = number + stat_modifier
                command_txt = f'**` D{sides} `** **` ({stat_modifier_str} {stat}) `**'
                calc_txt = f'` ({number}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) `'
                return result, command_txt, calc_txt
        else:
            rolled_dice = [random.randint(1, sides) for die in range(amount)]
            sum_dice = sum(rolled_dice)
            if apply:
                if apply == 'ADVANTAGE':
                    apply_roll = max(rolled_dice)
                elif apply == 'DISADVANTAGE':
                    apply_roll = min(rolled_dice)
                rolled_dice_txt = ' ` ` '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result = apply_roll + stat_modifier + modifier
                    command_txt = f'**` {amount} D{sides} `** **` {apply} `** **` ({stat_modifier_str} {stat}) `** **` ( {modifier_str} ) `**'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) ` ` ( {modifier_str} ) `'
                    return result, command_txt, calc_txt
                else:
                    result = apply_roll + stat_modifier
                    command_txt = f'**` {amount} D{sides} `** **` {apply} `** **` ({stat_modifier_str} {stat}) `**'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) `'
                    return result, command_txt, calc_txt
            else:
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result = sum_dice + stat_modifier + modifier
                    command_txt = f'**` {amount} D{sides} `** **` ({stat_modifier_str} {stat}) `** **` ( {modifier_str} ) `**'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) ` ` ( {modifier_str} ) `'
                    return result, command_txt, calc_txt
                else:
                    result = sum_dice + stat_modifier
                    command_txt = f'**` {amount} D{sides} `** **` ({stat_modifier_str} {stat}) `**'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧮 \a **MODIFIED WITH** \a` ({stat_modifier_str} {stat}) `'
                    return result, command_txt, calc_txt

    @roll.command(name='stat', description='ROLLS DICE WITH YOUR STATS.')
    async def stat(self, ctx, character: Option(str, 'for which character?', required=True), stat: Option(str, 'for which stat?', choices=stat_array, required=True), amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), apply: Option(str, 'advantage or disdvantage?', choices=['ADVANTAGE', 'DISADVANTAGE'], required=False), modifier: Option(int, 'modify the result?', required=False), comment: Option(str, 'what are you rolling for?', required=False)):
        selected_character = await self.select_character(ctx.author.id, ctx.guild.id, character.upper())
        if not selected_character:
            error_embed = error_embed_creator('**` THIS CHARACTER COULD NOT BE FOUND. `**' + '\n\n' + f'❓ **` {character.upper()} `** ` DOES NOT EXIST. `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        else:
            stat_column = stat_dict[stat]
            stat_modifier = selected_character[stat_column]
            hex_str = selected_character[5]
            hex_int = int(hex_str, base=16)
            chara_img = selected_character[6]
            output_array = self.stat_roll_helper(stat, stat_modifier, amount, sides, apply, modifier)
            if not comment:
                no_comment_embed = self.no_comment_embed_creator(character.upper(), hex_int, chara_img, stat, output_array[0], output_array[1], output_array[2])
                no_comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=no_comment_embed)
            else:
                comment_embed = self.comment_embed_creator(character.upper(), hex_int, chara_img, stat, comment.upper(), output_array[0], output_array[1], output_array[2])
                comment_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send_response('_ _', ephemeral=True, delete_after=1)
                await ctx.send('_ _', embed=comment_embed)

def setup(bot):
    bot.add_cog(Randomizer(bot))