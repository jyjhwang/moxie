import discord
import random
from discord.ext import commands
from discord.commands import Option

class randomizer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Randomizer COG loaded.')

    def error_embed_creator(self, error_message):
        error_embed = discord.Embed(
                title = '⚠️ \a ERROR',
                description = error_message,
                color = 16436582,
            )
        error_embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/newsfeed/001/690/562/921.png")
        return error_embed
    
    def choice_embed_creator(self, result_txt, choices_txt):
        choice_embed = discord.Embed(
                title = '🎯 \a YOU CHOSE \a ' + f'**` {result_txt} `**',
                description = f'🏹 \a **FROM THE CHOICES** \a {choices_txt}',
                color = 13580881,
            )
        choice_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
        return choice_embed

    @discord.slash_command(name='choose', description='CHOOSE WISELY.')
    async def choose(self, ctx, choices: Option(str, 'separate out choices with semicolons ( ; )', required=True)):
        if ';' not in choices:
            error_embed = self.error_embed_creator('**` SEPARATE OUT CHOICES WITH SEMICOLONS. `**' + '\n\n' + '❌ ` /choose choice1 choice2            `' + '\n' + '✅ ` /choose choice1;choice2            `' + '\n' + '✅ ` /choose choice1 ; choice2          `' + '\n' + '✅ ` /choose choice1; choice2; choice3  `')
            await ctx.send_response('_ _', embed=error_embed, ephemeral=True)
        else:
            choices = choices.split(';')
            choices_array = [f'**` {choice.strip().upper()} `**' for choice in choices]
            result_txt = random.choice(choices).strip().upper()
            choices_txt = ' \a '.join(choices_array)

            choice_embed = self.choice_embed_creator(result_txt, choices_txt)
            choice_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
            await ctx.send('_ _', embed=choice_embed)

    def no_calc_embed_creator(self, result, command_txt):
        no_calc_embed = discord.Embed(
            title = '🎲 \a YOU ROLLED \a ' + f'**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a {command_txt}',
            color = 15252813,
        )
        no_calc_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
        return no_calc_embed
    
    def calc_embed_creator(self, result, command_txt, calc_txt):
        calc_embed = discord.Embed(
            title = '🎲 \a YOU ROLLED \a ' + f'**` {result} `**',
            description = f'🎰 \a **FROM THE ROLL** \a {command_txt}' + '\n' + f'🧮 \a **CALCULATED AS** \a {calc_txt}',
            color = 15252813,
        )
        calc_embed.set_thumbnail(url="https://i.pinimg.com/474x/66/a2/f1/66a2f1f57f17bd300d250a0cfc8e0baf.jpg")
        return calc_embed

    @discord.slash_command(name='roll', description='ROLL A DIE.')
    async def roll(self, ctx, amount: Option(int, 'how many dice?', min_value=1, required=True), sides: Option(int, 'how many sides to each die?', min_value=1, required=True), modifier: Option(int, 'modify the result?', required=False)):
        
        if amount == 1:
            number = random.randint(1, sides)
            if not modifier:
                command_txt = f'**` D{sides} `**'

                no_mod_embed = self.no_calc_embed_creator(number, command_txt)
                no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send('_ _', embed=no_mod_embed)
            else:
                result = number + modifier
                command_txt = f'**` D{sides} `** **` + `** **` ({modifier}) `**'
                calc_txt = f'` ({number}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send('_ _', embed=mod_embed)
        else:
            rolled_dice = [random.randint(1, sides) for die in range(amount)]
            rolled_dice_txt = ' + '.join([f'{num}' for num in rolled_dice])
            result = sum(rolled_dice)
            if not modifier:
                command_txt = f'**` {amount} D{sides} `**'
                calc_txt = f'` ({rolled_dice_txt}) ` ` = ` **` ({result}) `**'

                no_mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                no_mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send('_ _', embed=no_mod_embed)
            else:
                result += modifier
                command_txt = f'**` {amount} D{sides} `** **` + `** **` ({modifier}) `**'
                calc_txt = f'` ({rolled_dice_txt}) ` ` + ` ` ({modifier}) ` ` = ` **` ({result}) `**'

                mod_embed = self.calc_embed_creator(result, command_txt, calc_txt)
                mod_embed.add_field(name='', value=f'🆔 \a {ctx.author.mention}')
                await ctx.send('_ _', embed=mod_embed)

def setup(bot):
    bot.add_cog(randomizer(bot))