"""
The module responsible for judging the trustworthiness of sources.
"""

import re
import logging
from discord import Message
from discord.ext import commands
from _helpers import embedder, Color

log = logging.getLogger("Trusty")


class Trusty(commands.Cog):
    """ The Trustworthiness module class """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """
        Trustworthiness of links to be evaluated upon "on_message"
        """
        # Regular expression to find URLs in the message
        url_pattern = re.compile(r'https?://\S+|www\.\S+')

        # Check if the message contains a URL
        if url_pattern.search(message.content):
            for pattern, trust_settings in self.bot.settings["trustworthiness"].items():
                if re.search(rf'https?://\S*{re.escape(pattern)}\S*', message.content, re.IGNORECASE):
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

    #TODO: Add commands to add, edit, and remove trustworthiness settings

async def setup(bot):
    """ Cog Definition """
    await bot.add_cog(Trusty(bot))
