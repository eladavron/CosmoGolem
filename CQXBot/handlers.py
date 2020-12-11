""" Various event handlers """

import os
import re
import logging

from discord.ext import commands
from _helpers import Color, embedder

log = logging.getLogger("discord")


class Handlers(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot

    ### Events ###
    @commands.Cog.listener()
    async def on_ready(self):
        """ What happens when the bot is ready """
        log.info("*** Client ready! ***")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ What happens when a bad command is invoked """
        if re.match(
            r"\.", ctx.invoked_with
        ):  # If a double-dot (or more than one) was used, it'll be part of the "command"
            return
        log.error(
            "%s issued command but got an error: %s", ctx.message.author, str(error)
        )  # For regular command errors
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                embed=embedder("Type `.help` to see a list of available commands.", title=str(error), error=True)
            )

        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(
            error, commands.BadArgument
        ):  # For when using wrong arguments
            await ctx.send(
                embed=embedder(
                    f"Error: ```{str(error)}```\nType `.help {ctx.invoked_with}` to get help.",
                    title=f"That's not how you `{ctx.invoked_with}`!",
                    error=True,
                )
            )

        else:  # Technically shouldn't get here.
            await ctx.send(embed=embedder(description=f"Error: ```{str(error)}```", title=f"Unexpected error!", error=True))


def setup(bot):
    bot.add_cog(Handlers(bot))
