import os
import re
import random
import logging
import emoji

from imgurpython import ImgurClient

import discord
from discord.ext import commands

from _helpers import Color, embedder, save_file_and_send
from _settings import Settings

log = logging.getLogger("Images")

settings = Settings()


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Followed by a search term, fetches a random image from Imgur.")
    async def image(self, ctx, *, query):
        await ctx.trigger_typing()
        if em := await imgur_fetcher(query, ctx):
            await ctx.send(embed=em)

    @commands.command(help="Show a user's avatar in full.")
    async def avatar(self, ctx, query):
        for member in ctx.message.mentions:
            url = str(member.avatar_url)
            em = embedder(
                description="",
                title="Here's %s%s avatar:"
                % (
                    member.display_name,
                    "'" if member.display_name.endswith("s") else "'s",
                ),
                url=url,
            )
            em.set_image(url=url)
            await ctx.send(embed=em)

    @commands.command(help="Show a random catto.")
    async def meow(self, ctx):
        await ctx.trigger_typing()
        if em := await imgur_fetcher("cat", ctx):
            em.description = "Here's a catto:"
            em.set_footer(text="%d cattos served!" % (settings.get_counter("catto") + 1))
            await ctx.send(embed=em)
            settings.increase_counter("catto", 1)

    @commands.command(help="Show a random doggo.")
    async def woof(self, ctx):
        await ctx.trigger_typing()
        if em := await imgur_fetcher("dog", ctx):
            em.description = "Here's a doggo:"
            em.set_footer(text="%d doggos served!" % (settings.get_counter("doggo") + 1))
            await ctx.send(embed=em)
            settings.increase_counter("doggo", 1)

    @commands.command(help="Make an emoji bigger.")
    async def embiggen(self, ctx, query):
        await ctx.trigger_typing()
        if query in emoji.UNICODE_EMOJI:
            string = query.encode("unicode-escape").decode("utf-8").replace("\\", "")
            code = re.match(r"U0+(\S+)", string).group(1)
            path = f"https://github.com/twitter/twemoji/blob/gh-pages/36x36/{code}png?raw=true"
            await save_file_and_send(ctx, path)
        elif re.match(r"^\<\:(\S+)\:(\d+)\>$", query):
            emoji_id = re.match(r"^\<\:(\S+)\:(\d+)\>$", query).group(2)
            await save_file_and_send(ctx, f"https://cdn.discordapp.com/emojis/{emoji_id}.png")
        else:
            await ctx.send(embed=embedder(f'"{query}" is not a recognized emoji.', error=True))


async def imgur_fetcher(query, ctx):
    imgur_settings = settings.get("imgur")
    if not all(x in imgur_settings for x in ["id", "secret"]):
        await ctx.channel.send(embed=embedder("Imgur API Key not set up correctly, can't show images!", error=True))
        log.error("Imgur API Key not set up, can't show images!")
        return None

    img_client = ImgurClient(imgur_settings["id"], imgur_settings["secret"])
    resultList = img_client.gallery_search(query)
    if len(resultList) <= 0:
        return embedder(f'Sorry, no results found for "{query}"')

    selectedImage = random.choice(resultList)
    if selectedImage.is_album:
        album_id = selectedImage.id
        imageList = img_client.get_album_images(album_id)
        selectedImage = random.choice(imageList)

    isNSFW = selectedImage.nsfw
    if ctx.channel.is_nsfw():
        isNSFW = False  # Override NSFW setting if channel allows NSFW

    url = selectedImage.gifv if selectedImage.animated else selectedImage.link
    message = 'Here\'s a random image of "%s":\n%s' % (
        query,
        "***Warning: NSFW image!***\n<%s>" % (url) if isNSFW else "",
    )
    color = Color.RED if isNSFW else Color.DEFAULT
    em = embedder(description=message, url=selectedImage.link, color=color)
    if not isNSFW:
        em.set_image(url=selectedImage.link)
    log.info(
        "Attempting to embed %s as an %s",
        url,
        "animation" if selectedImage.animated else "image",
    )
    return em


def setup(bot):
    bot.add_cog(Images(bot))
