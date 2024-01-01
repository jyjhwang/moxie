import discord
import re
import aiosqlite
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup
from discord.ui import View, Button, Select
from utils import basic_embed_creator, error_embed_creator, get_postID, get_channelID

def message_link_found(message):
    return re.fullmatch('(https:\/\/discord\.com\/channels\/\d+\/\d+\/\d+)', message)

class RoleButton(Button):
    def __init__(self, role: discord.Role, styletype):
        super().__init__(style=styletype, label=role.name, custom_id=str(role.id))

    async def callback(self, ctx):
        role = ctx.guild.get_role(int(self.custom_id))
        if role is None:
            return
        elif role not in ctx.user.roles:
            await ctx.user.add_roles(role)
            await ctx.response.send_message(f'You added the role {role.mention}', ephemeral=True)
        else:
            await ctx.user.remove_roles(role)
            await ctx.response.send_message(f'You removed the role {role.mention}', ephemeral=True)

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
                )
                quote_embed.add_field(name='\a', value=f'[` JUMP TO MESSAGE `]({quoted_message.jump_url})')
                quote_embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
                if message.channel != quoted_message.channel:
                    quote_embed.set_footer(text=f'#{quoted_message.channel}')
                if quoted_message.attachments:
                    for attachment in quoted_message.attachments:
                        if attachment.content_type.startswith('image'):
                            print('Image')
                    # images = []
                    # files = []
                    # if quoted_message.attachments.content_type.startswith('image'):
                    #     file = quoted_message.attachments
                await message.delete()
                await message.channel.send('_ _', embed=quote_embed)

    @discord.slash_command(name='prune', description='PRUNE MESSAGES.')
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
            prune_embed = basic_embed_creator(f'❌\a ` PRUNED `  {amount} ' + message_txt)
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)
        else:
            await ctx.channel.purge(limit=limit, check=lambda msg: msg.author == user and not msg.pinned)
            prune_embed = basic_embed_creator(f'❌\a ` PRUNED ` \a{amount} ' + message_txt)
            prune_embed.add_field(name='', value=f'🆔\a ` FROM ` \a{user.mention}')
            await ctx.respond('_ _', embed=prune_embed, ephemeral=True)

    async def select_rolegroup(self, guildid, rolegroupname):
        async with aiosqlite.connect('rolegroups.db') as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT * FROM rolegroups_table WHERE guild_id = ? AND rolegroup_name = ?', (guildid, rolegroupname))
                rolegroup_info = await cursor.fetchone()
                return rolegroup_info

    @discord.slash_command(name='button_roles', description='CREATE AN EMBED FOR SELF-ASSIGNING ROLES.')
    @commands.has_permissions(manage_roles=True)
    async def button_roles(self, ctx, rolegroup: Option(str, 'for which role group?', required=True)):
        button_roles_view = View(timeout=None)
        selected_rolegroup = await self.select_rolegroup(ctx.guild.id, rolegroup.upper())
        if not selected_rolegroup:
            error_embed = error_embed_creator('**` THIS ROLE GROUP COULD NOT BE FOUND. `**' + '\n\n' + f'❓\a **{rolegroup.upper()}** \a` DOES NOT EXIST IN `\a **{ctx.guild.name}**')
            await ctx.respond('_ _', embed=error_embed, ephemeral=True)
        else:
            role_ids = selected_rolegroup[3].replace(' ', '').split(',')
            button_styles = [discord.ButtonStyle.blurple, discord.ButtonStyle.green, discord.ButtonStyle.red, discord.ButtonStyle.green]
            for i, role_id in enumerate(role_ids):
                remainder = i % len(button_styles)
                role = ctx.guild.get_role(int(role_id))
                button_roles_view.add_item(RoleButton(role, button_styles[remainder]))

            button_roles_embed = basic_embed_creator(f'⬇️\a Click these buttons to get your roles!')
            await ctx.respond('_ _', ephemeral=True, delete_after=1)
            await ctx.send('_ _', embed=button_roles_embed, view=button_roles_view)

def setup(bot):
    bot.add_cog(Moderation(bot))