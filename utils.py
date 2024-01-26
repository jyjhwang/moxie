import discord

def basic_embed_creator(title_txt, description_txt):
        basic_embed = discord.Embed(
            title = title_txt,
            description = description_txt,
            color = int('2B2D31', base=16),
        )
        return basic_embed

def error_embed_creator(error_message):
    error_embed = discord.Embed(
            title = '⚠️\a ERROR',
            description = error_message,
            color = int('FACD66', base=16),
        )
    error_embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/newsfeed/001/690/562/921.png")
    return error_embed

def get_postID(link):
    return link.split('/')[-1]

def get_channelID(link):
    return link.split('/')[-2]