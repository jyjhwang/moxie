import discord
import re
import datetime
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from discord.ui import View, Button, Select
from utils import basic_embed_creator, error_embed_creator, get_postID, get_channelID

def message_link_found(message):
    return re.fullmatch('(https:\/\/discord\.com\/channels\/\d+\/\d+\/\d+)', message)

class QuoteLink(View):
    def __init__(self, url):
        super().__init__(Button(style=discord.ButtonStyle.link, label="Go to Message", url=url))

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation COG loaded.')

    @commands.Cog.listener('on_message')
    async def quote(self, message):
        if not message.author.bot:
            if message_link_found(message.clean_content):
                postID = get_postID(message.clean_content)
                channelID = get_channelID(message.clean_content)
                quoted_channel = await self.bot.fetch_channel(channelID)
                quoted_message = await quoted_channel.fetch_message(postID)
                quote_embed = discord.Embed(
                    description = quoted_message.clean_content,
                    color = int('2B2D31', base=16),
                    timestamp = quoted_message.created_at,
                )
                quote_embed.set_author(name=quoted_message.author.display_name, icon_url=quoted_message.author.display_avatar.url)
                if message.channel != quoted_message.channel:
                    quote_embed.set_footer(text=f'#{quoted_message.channel}')
                if quoted_message.attachments:
                    for attachment in quoted_message.attachments:
                        if attachment.content_type.startswith('image'):
                            quote_embed.set_image(url=str(quoted_message.attachments[0]))
                quote_embeds = [quote_embed]
                if quoted_message.embeds:
                    for embed in quoted_message.embeds:
                        quote_embeds.append(embed)
                await message.delete()
                await message.channel.send('_ _', embeds=quote_embeds, view=QuoteLink(quoted_message.jump_url))

    @discord.slash_command(name='top', description='Get a link to the top!')
    async def top(self, ctx):
        embed_link = f'https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/0'
        top_embed = discord.Embed(
                title = '⬆️\a Go to the top!',
                color = int('2B2D31', base=16),
                url = embed_link,
                )
        await ctx.respond('_ _', embed=top_embed, ephemeral=True)

    @discord.slash_command(name='prune', description='Prune messages.')
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: Option(int, 'how many messages?', min_value=1, required=True), user: Option(discord.User, 'from a specific user?', required=False)):
        limit = amount
        messages = await ctx.channel.history(limit=amount).flatten()
        for msg in messages:
            if msg.pinned:
                limit += 1
        message_txt = 'MESSAGES'
        if amount == 1:
            message_txt = 'MESSAGE'
        if not user:
            await ctx.channel.purge(limit=limit, check=lambda msg: not msg.pinned)
            prune_embed = basic_embed_creator(f'❌\a ` PRUNED `  {amount} ' + message_txt, None)
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)
        else:
            await ctx.channel.purge(limit=limit, check=lambda msg: msg.author == user and not msg.pinned)
            prune_embed = basic_embed_creator(f'❌\a ` PRUNED ` \a{amount} ' + message_txt, None)
            prune_embed.add_field(name='', value=f'🆔\a ` FROM ` \a{user.mention}')
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Moderation(bot))