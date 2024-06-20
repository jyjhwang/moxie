import discord
import re
import aiosqlite
import discord.utils as dutils
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

        async with aiosqlite.connect('starboard_setup.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS starboard_setup_table (
                    guild_id INT UNIQUE,
                    guild_name TEXT,
                    starboard_channel_id INT
                )''')
            await db.commit()

        async with aiosqlite.connect('starboard_messages.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS starboard_messages_table (
                    guild_id INT,
                    guild_name TEXT,
                    starboard_channel_id INT,
                    starred_message_id INT,
                    starboard_message_id INT
                )''')
            await db.commit()
    
    async def select_starboard_channel(self, guild_id):
        async with aiosqlite.connect('starboard_setup.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT starboard_channel_id FROM starboard_setup_table WHERE guild_id = ?', (guild_id,))
                return await cursor.fetchone()
            
    async def select_starboard_ids(self, starred_message_id):
        async with aiosqlite.connect('starboard_messages.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT starboard_channel_id, starboard_message_id FROM starboard_messages_table WHERE starred_message_id = ?', (starred_message_id,))
                starboard_ids = await cursor.fetchone()
                return starboard_ids
    
    def img_attachment_finder(self, message):
        img_link = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image'):
                    img_link = message.attachments[0].url
        return img_link

    def quote_embed_creator(self, description_txt, role_color, timestamp_txt, display_name, display_avatar, footer_txt=None, img_link=None):
        quote_embed = discord.Embed(
            description = description_txt,
            color = role_color,
            timestamp = timestamp_txt,
        )
        quote_embed.set_author(name=display_name, icon_url=display_avatar)
        if footer_txt:
            quote_embed.set_footer(text=f'#{footer_txt}')
        if img_link:
            quote_embed.set_image(url=img_link)
        return quote_embed

    @commands.Cog.listener('on_message')
    async def quote(self, message):
        if not message.author.bot:
            if message_link_found(message.clean_content):
                postID = get_postID(message.clean_content)
                channelID = get_channelID(message.clean_content)
                quoted_channel = await dutils.get_or_fetch(self.bot, 'channel', channelID)
                quoted_message = await quoted_channel.fetch_message(postID)
                img_link = self.img_attachment_finder(quoted_message)
                quote_embed = self.quote_embed_creator(quoted_message.clean_content, quoted_message.author.color, quoted_message.created_at, quoted_message.author.display_name, quoted_message.author.display_avatar.url, quoted_message.channel, img_link)
                quote_embeds = [quote_embed]
                if quoted_message.embeds:
                    for embed in quoted_message.embeds:
                        quote_embeds.append(embed)
                await message.delete()
                await message.channel.send('_ _', embeds=quote_embeds, view=QuoteLink(quoted_message.jump_url))
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot:
            starred_channel = await dutils.get_or_fetch(self.bot, 'channel', payload.channel_id)
            starred_message = await starred_channel.fetch_message(payload.message_id)
            if str(payload.emoji) == '\U00002B50' and starred_message.author != payload.member:
                guild = await dutils.get_or_fetch(self.bot, 'guild', payload.guild_id)
                starboard_channel_id = await self.select_starboard_channel(payload.guild_id)
                if starboard_channel_id:
                    starboard_channel = await dutils.get_or_fetch(guild, 'channel', starboard_channel_id[0])
                    for reaction in starred_message.reactions:
                        if reaction.emoji == '⭐' and reaction.count == 1:
                            img_link = self.img_attachment_finder(starred_message)
                            quote_embed = self.quote_embed_creator(starred_message.clean_content, starred_message.author.color, starred_message.created_at, starred_message.author.display_name, starred_message.author.display_avatar.url, starred_message.channel, img_link)
                            quote_embeds = [quote_embed]
                            if starred_message.embeds:
                                for embed in starred_message.embeds:
                                    quote_embeds.append(embed)
                            starboard_message = await starboard_channel.send('_ _\n' + '⭐ **1**' + '\n_ _', embeds=quote_embeds, view=QuoteLink(starred_message.jump_url))
                            async with aiosqlite.connect('starboard_messages.db') as db:
                                async with db.cursor() as cursor:
                                    await cursor.execute('INSERT INTO starboard_messages_table VALUES (?, ?, ?, ?, ?)', (payload.guild_id, guild.name, starboard_channel_id[0], payload.message_id, starboard_message.id))
                                await db.commit()
                        if reaction.emoji == '⭐' and reaction.count > 1:
                            starboard_ids = await self.select_starboard_ids(payload.message_id)
                            starboard_channel = await dutils.get_or_fetch(self.bot, 'channel', starboard_ids[0])
                            starboard_message = await starboard_channel.fetch_message(starboard_ids[1])
                            await starboard_message.edit('_ _\n' + f'⭐ **{reaction.count}**' + '\n_ _')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        payload_user = await dutils.get_or_fetch(self.bot, 'user', payload.user_id)
        if not payload_user.bot:
            unstarred_channel = await dutils.get_or_fetch(self.bot, 'channel', payload.channel_id)
            unstarred_message = await unstarred_channel.fetch_message(payload.message_id)
            if str(payload.emoji) == '\U00002B50' and unstarred_message.author != payload_user:
                guild = await dutils.get_or_fetch(self.bot, 'guild', payload.guild_id)
                starboard_channel_id = await self.select_starboard_channel(payload.guild_id)
                if starboard_channel_id:
                    starboard_channel = await dutils.get_or_fetch(guild, 'channel', starboard_channel_id[0])
                    for reaction in unstarred_message.reactions:
                        if reaction.emoji == '⭐' and reaction.count >= 1:
                            starboard_ids = await self.select_starboard_ids(payload.message_id)
                            starboard_channel = await dutils.get_or_fetch(self.bot, 'channel', starboard_ids[0])
                            starboard_message = await starboard_channel.fetch_message(starboard_ids[1])
                            await starboard_message.edit('_ _\n' + f'⭐ **{reaction.count}**' + '\n_ _')
                    if '⭐' not in [reaction.emoji for reaction in unstarred_message.reactions]:
                        starboard_ids = await self.select_starboard_ids(payload.message_id)
                        starboard_channel = await dutils.get_or_fetch(self.bot, 'channel', starboard_ids[0])
                        starboard_message = await starboard_channel.fetch_message(starboard_ids[1])
                        async with aiosqlite.connect('starboard_messages.db') as db:
                            async with db.cursor() as cursor:
                                await cursor.execute('DELETE FROM starboard_messages_table WHERE starboard_message_id = ?', (starboard_message.id,))
                            await db.commit()
                        await starboard_message.delete()

    @discord.slash_command(name='starboard', description='Set the starboard channel.')
    @commands.has_permissions(manage_guild=True)
    async def starboard(self, ctx, channel: Option(discord.TextChannel, 'in which channel?', required=True)):
        starboard_channel_id = await self.select_starboard_channel(ctx.guild.id)
        if starboard_channel_id:
            if starboard_channel_id[0] != channel.id:
                async with aiosqlite.connect('starboard_setup.db') as db:
                    async with db.cursor() as cursor:
                        await cursor.execute('UPDATE starboard_setup_table SET starboard_channel_id = ? WHERE guild_id = ?', (channel.id, ctx.guild.id))
                    await db.commit()
                update_embed = basic_embed_creator(f'⭐\a **THE STARBOARD CHANNEL HAS BEEN SET TO** \a{channel.mention}', None)
                await ctx.respond('_ _', embed=update_embed, ephemeral=True)
        else:
            async with aiosqlite.connect('starboard_setup.db') as db:
                async with db.cursor() as cursor:
                    await cursor.execute('INSERT INTO starboard_setup_table VALUES (?, ?, ?)', (ctx.guild.id, ctx.guild.name, channel.id))
                await db.commit()
            update_embed = basic_embed_creator(f'⭐\a **THE STARBOARD CHANNEL HAS BEEN SET TO** \a{channel.mention}', None)
            await ctx.respond('_ _', embed=update_embed, ephemeral=True)

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
            prune_embed = basic_embed_creator(f'❌\a **YOU PRUNED** \a**` {amount} {message_txt} `**', None)
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)
        else:
            await ctx.channel.purge(limit=limit, check=lambda msg: msg.author == user and not msg.pinned)
            prune_embed = basic_embed_creator(f'❌\a **YOU PRUNED** \a**` {amount} {message_txt} `**', f'📝\a **FROM** \a{user.mention}')
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Moderation(bot))