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
    
    def choice_embed_creator(self, result_txt, choices_txt, embed_link):
        choice_embed = discord.Embed(
                title = '🎯\a YOU CHOSE \a' + f'**` {result_txt} `**',
                description = f'🏹\a **FROM THE CHOICES** \a{choices_txt}',
                color = int('2B2D31', base=16),
                url = embed_link,
            )
        return choice_embed

    @discord.slash_command(name='choose', description='CHOOSE WISELY.')
    async def choose(self, ctx, choices: Option(str, 'separate out choices with vertical bars ( | )', required=True)):
        if '|' not in choices:
            error_embed = error_embed_creator('**` SEPARATE OUT CHOICES WITH VERTICAL BARS. `**' + '\n\n' + '❌\a ` /choose choice1 choice2            `' + '\n' + '✅\a ` /choose choice1|choice2            `' + '\n' + '✅\a ` /choose choice1 | choice2          `' + '\n' + '✅\a ` /choose choice1| choice2| choice3  `')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            choices_array = choices.split('|')
            choices_format = [f'**` {choice.strip().upper()} `**' for choice in choices_array]
            result_txt = random.choice(choices_array).strip().upper()
            choices_txt = ' \a'.join(choices_format)
            embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}'

            choice_embed = self.choice_embed_creator(result_txt, choices_txt, embed_link)
            choice_embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.respond('_ _', embed=choice_embed)

    def pos_or_neg(self, value):
        if value >= 0:
            return f'+{value}'
        else:
            return f'{value}'
    
    def dice_embed_creator(self, result, command_txt, embed_link, comment_txt=None, calc_txt=None):
        title_txt = f'🎲\a YOU ROLLED \a**` {result} `**'
        if comment_txt:
            title_txt += '\n' + f'💬\a **` {comment_txt} `**'
        description_txt = f'🎰\a **FROM THE ROLL** \a{command_txt}'
        if calc_txt:
            description_txt += '\n' + f'🧮\a **CALCULATED AS** \a{calc_txt}'
        dice_embed = discord.Embed(
            title = title_txt,
            description = description_txt,
            color = int('2B2D31', base=16),
            url = embed_link,
        )
        return dice_embed
    
    def roll_dice_helper(self, amount, sides, apply, modifier):
        if amount == 1:
            number = random.randint(1, sides)
            if modifier:
                modifier_str = self.pos_or_neg(modifier)
                result = number + modifier
                command_txt = f'` D{sides} ` ` {modifier_str} `'
                calc_txt = f'` ({number}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {modifier_str} `'
                return result, command_txt, None, calc_txt
            else:
                command_txt = f'` D{sides} `'
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
                    command_txt = f'` {amount} D{sides} ` ` {apply} ` ` {modifier_str} `'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {modifier_str} `'
                    return result, command_txt, None, calc_txt
                else:
                    command_txt = f'**` {amount} D{sides} `** **` {apply} `**'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `'
                    return apply_roll, command_txt, None, calc_txt
            else:
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result += modifier
                    command_txt = f'` {amount} D{sides} ` ` {modifier_str} `'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {modifier_str} `'
                    return result, command_txt, None, calc_txt
                else:
                    command_txt = f'` {amount} D{sides} `'
                    calc_txt = f'` ({rolled_dice_txt}) `'
                    return result, command_txt, None, calc_txt

    @roll.command(name='dice', description='ROLLS DICE.')
    async def dice(self, ctx, amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), apply: Option(str, 'advantage or disdvantage?', choices=['ADVANTAGE', 'DISADVANTAGE'], required=False), modifier: Option(int, 'modify the result?', required=False), comment: Option(str, 'what are you rolling for?', required=False)):
        output_array = self.roll_dice_helper(amount, sides, apply, modifier)
        embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}'
        if amount == 1 and not modifier:
            dice_embed = self.dice_embed_creator(output_array[0], output_array[1], embed_link, comment)
        else:
            dice_embed = self.dice_embed_creator(output_array[0], output_array[1], embed_link, comment, output_array[3])
        dice_embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.respond('_ _', embed=dice_embed)
    
    def stat_embed_creator(self, charaname, characolor, charaimg, charastat, result, command_txt, calc_txt, embed_link, comment_txt=None):
        title_txt = f'🎲\a {charaname} ROLLED \a**` {result} {charastat} `**'
        if comment_txt:
            title_txt += '\n' + f'💬\a **` {comment_txt} `**'
        stat_embed = discord.Embed(
            title = title_txt,
            description = f'🎰\a **FROM THE ROLL** \a{command_txt}' + '\n' + f'🧮\a **CALCULATED AS** \a{calc_txt}',
            color = characolor,
            url = embed_link,
        )
        stat_embed.set_thumbnail(url=charaimg)
        return stat_embed
    
    async def select_character(self, userid, guildid, charaname):
        async with aiosqlite.connect('roster.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM roster_table WHERE user_id = ? AND guild_id = ? AND character_name = ?', (str(userid), str(guildid), str(charaname)))
                chara_info = await cursor.fetchone()
                return chara_info
            
    def roll_stat_helper(self, stat, stat_modifier, amount, sides, apply, modifier):
        stat_modifier_str = self.pos_or_neg(stat_modifier)
        if amount == 1:
            number = random.randint(1, sides)
            if modifier:
                modifier_str = self.pos_or_neg(modifier)
                result = number + stat_modifier + modifier
                command_txt = f'` D{sides} ` ` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                calc_txt = f'` ({number}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                return result, command_txt, calc_txt
            else:
                result = number + stat_modifier
                command_txt = f'` D{sides} ` ` {stat_modifier_str} {stat} `'
                calc_txt = f'` ({number}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} `'
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
                    command_txt = f'` {amount} D{sides} ` ` {apply} ` ` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                    return result, command_txt, calc_txt
                else:
                    result = apply_roll + stat_modifier
                    command_txt = f'` {amount} D{sides} ` ` {apply} ` ` {stat_modifier_str} {stat} `'
                    calc_txt = f'` {rolled_dice_txt} ` ` {apply} `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} `'
                    return result, command_txt, calc_txt
            else:
                rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
                if modifier:
                    modifier_str = self.pos_or_neg(modifier)
                    result = sum_dice + stat_modifier + modifier
                    command_txt = f'` {amount} D{sides} ` ` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} ` ` {modifier_str} `'
                    return result, command_txt, calc_txt
                else:
                    result = sum_dice + stat_modifier
                    command_txt = f'` {amount} D{sides} ` ` {stat_modifier_str} {stat} `'
                    calc_txt = f'` ({rolled_dice_txt}) `' + '\n' + f'🧩\a **MODIFIED WITH** \a` {stat_modifier_str} {stat} `'
                    return result, command_txt, calc_txt

    @roll.command(name='stat', description='ROLLS DICE WITH YOUR STATS.')
    async def stat(self, ctx, character: Option(str, 'for which character?', required=True), stat: Option(str, 'for which stat?', choices=stat_array, required=True), amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), apply: Option(str, 'advantage or disdvantage?', choices=['ADVANTAGE', 'DISADVANTAGE'], required=False), modifier: Option(int, 'modify the result?', required=False), comment: Option(str, 'what are you rolling for?', required=False)):
        selected_character = await self.select_character(ctx.author.id, ctx.guild.id, character.upper())
        if not selected_character:
            error_embed = error_embed_creator('**` THIS CHARACTER COULD NOT BE FOUND. `**' + '\n\n' + f'❓\a **{character.upper()}** \a` DOES NOT EXIST FOR ` {ctx.author.mention}')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            stat_column = stat_dict[stat]
            stat_modifier = selected_character[stat_column]
            hex_str = selected_character[5]
            hex_int = int(hex_str, base=16)
            chara_img = selected_character[6]
            output_array = self.roll_stat_helper(stat, stat_modifier, amount, sides, apply, modifier)
            embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}'
            stat_embed = self.stat_embed_creator(character.upper(), hex_int, chara_img, stat, output_array[0], output_array[1], output_array[2], embed_link, comment)
            await ctx.respond('_ _', embed=stat_embed)

def setup(bot):
    bot.add_cog(Randomizer(bot))