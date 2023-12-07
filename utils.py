import discord

def error_embed_creator(error_message):
    error_embed = discord.Embed(
            title = '⚠️ \a ERROR',
            description = error_message,
            color = 16436582,
        )
    error_embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/newsfeed/001/690/562/921.png")
    return error_embed