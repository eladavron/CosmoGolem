"""
The module responsible for all of the easter eggs.
"""

import re
import os
import logging
import discord
from discord.ext import commands
from _helpers import embedder, check_timer, get_channel_name

log = logging.getLogger("EasterEggs")


class Eggs(commands.Cog):
    """ The Easter Eggs module class """

    def __init__(self, bot):
        self.bot = bot
        self.timers = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        """ All easter eggs are listened to by a single "on_message" - splitting it up would mean multiple files and who has the patience for that """
        if re.search(r"b+\W*e+\W*n+\W*n+\W*u+", message.content, re.IGNORECASE):  # Bennu
            if check_timer(self, "bennu_" + str(message.channel.id)):
                log.info(
                    "%s mentioned Bennu in %s",
                    message.author.name,
                    get_channel_name(message.channel),
                )
                await message.channel.send(embed=embedder(description="F Bennu!"))
            else:
                log.info(
                    "%s mentioned Bennu in %s but the easter egg was on timeout.",
                    message.author.name,
                    get_channel_name(message.channel),
                )


def setup(bot):
    """ Cog Definition """
    bot.add_cog(Eggs(bot))
