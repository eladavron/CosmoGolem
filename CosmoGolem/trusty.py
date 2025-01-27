"""
The module responsible for judging the trustworthiness of sources.
"""

import re
import logging
from urllib3.util import parse_url
from discord import Message
from discord.ext import commands
from _helpers import embedder, Color

log = logging.getLogger("Trusty")


class Trusty(commands.Cog):
    """The Trustworthiness module class"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Trustworthiness of links to be evaluated upon "on_message"
        """
        # Regular expression to find URLs in the message
        if message.channel.id in self.bot.settings.get("channels", {}).get("trusted_channels", []):
            log.debug("Skipping trustworthiness check in trusted channel %s", message.channel)
            return
        url_pattern = re.compile(r"https?://\S+|www\.\S+")

        # Check if the message contains a URL
        if (match := url_pattern.search(message.content)):
            for pattern, trust_settings in self.bot.settings["trustworthiness"].items():
                url = parse_url(match[0])
                second_level_domain = ".".join(url.host.split(".")[-2:])
                aliases = [pattern, *trust_settings.get("aliases", [])]
                if any(matched_urls := [second_level_domain.lower() == alias.lower() for alias in aliases]):
                    log.info("Matched %s to %s - Trustworthiness %d", match[0], matched_urls[0], trust_settings["trust"])
                    if trust_settings["trust"] < 0.5:
                        color = Color.RED
                        title = "Trustworthiness Alert"
                    elif trust_settings["trust"] < 0.75:
                        color = Color.YELLOW
                        title = "Trustworthiness Warning"
                    else:
                        color = Color.GREEN
                        title = "Trustworthy Source"
                    await message.channel.send(
                        embed=embedder(
                            description=trust_settings["message"],
                            title=title,
                            color=color,
                        )
                    )

    # TODO: Add commands to add, edit, and remove trustworthiness settings


async def setup(bot):
    """Cog Definition"""
    await bot.add_cog(Trusty(bot))
