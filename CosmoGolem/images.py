""" All image related commands """

import random
import logging
import emoji

from imgurpython import ImgurClient

from discord import PartialEmoji
from discord.ext import commands
from _settings import Settings
from _helpers import Color, embedder, save_file_and_send


log = logging.getLogger("Images")


class Images(commands.Cog):
    """ A cog to handle all image commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Followed by a search term, fetches a random image from Imgur.")
    async def image(self, ctx, *, query):
        """ Search a random image from imgur that matches the give query """
        await ctx.typing()
        await self.imgur_fetcher(ctx, query)

    @commands.command(help="Show a user's avatar in full.")
    async def avatar(self, ctx):
        """ Show a user's avatar """
        for member in ctx.message.mentions:
            url = str(member.display_avatar.url)
            embed = embedder(
                description="",
                title="Here's %s%s avatar:"
                % (
                    member.display_name,
                    "'" if member.display_name.endswith("s") else "'s",
                ),
                url=url,
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)

    @commands.command(help="Show a random catto.", aliases=["cat", "catto", "kitty"])
    async def meow(self, ctx):
        """ Show a random cat """
        await ctx.typing()
        await self.imgur_fetcher(ctx, query="cat", name="catto")

    @commands.command(help="Show a random doggo.", aliases=["dog", "doggo", "doggy", "puppy", "pupper", "pup"])
    async def woof(self, ctx):
        """ Show a random dog """
        await ctx.typing()
        await self.imgur_fetcher(ctx, query="dog", name="doggo")

    @commands.command(help="Make an emoji bigger.")
    async def embiggen(self, ctx, query):
        """ Embiggen an emoji """
        await ctx.typing()
        if emoji.is_emoji(query) :
            path = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(query):x}.png"
            await save_file_and_send(ctx, path)
        elif url := PartialEmoji.from_str(query).url:
            await save_file_and_send(ctx, url)
        else:
            await ctx.send(embed=embedder(f'"{query}" is not a recognized emoji.', error=True))

    async def imgur_fetcher(self, ctx, query, name=None):
        """ A utility function that fetches images from imgur and posts them """
        imgur_settings = Settings.static_settings.get("imgur")
        if not all(x in imgur_settings for x in ["id", "secret"]):
            await ctx.channel.send(embed=embedder("Imgur API Key not set up correctly, can't show images!", error=True))
            log.error("Imgur API Key not set up, can't show images!")

        img_client = ImgurClient(imgur_settings["id"], imgur_settings["secret"])
        reult_list = img_client.gallery_search(query)
        if not reult_list:
            await ctx.send(embed=embedder(f"Sorry, no results found for `{query}`"))
            return

        selected_image = random.choice(reult_list)
        if selected_image.is_album:
            album_id = selected_image.id
            image_list = img_client.get_album_images(album_id)
            selected_image = random.choice(image_list)

        is_nsfw = selected_image.nsfw
        if ctx.channel.is_nsfw():
            is_nsfw = False  # Override NSFW setting if channel allows NSFW

        url = selected_image.gifv if selected_image.animated else selected_image.link
        message = 'Here\'s a random image of "%s":\n%s' % (
            query,
            "***Warning: NSFW image!***\n<%s>" % (url) if is_nsfw else "",
        )
        color = Color.RED if is_nsfw else Color.DEFAULT
        embed = embedder(description=message, url=selected_image.link, color=color)
        if not is_nsfw:
            embed.set_image(url=selected_image.link)
        log.info("Attempting to embed %s as an %s", url, "animation" if selected_image.animated else "image")
        if name:
            embed.description = f"Here's a {name}:"
            count = self.bot.settings.get_counter(name) + 1
            embed.set_footer(text=f"{count} {name}s served!")
            self.bot.settings.increase_counter(name, 1)
        await ctx.send(embed=embed)


async def setup(bot):
    """ Cog init """
    await bot.add_cog(Images(bot))
