""" Various event handlers """

import re
import logging

from discord.ext import commands
from _helpers import embedder, Color

log = logging.getLogger("discord")


class Handlers(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot

    ### Events ###
    @commands.Cog.listener()
    async def on_ready(self):
        """ What happens when the bot is ready """
        bot_commands = self.bot.settings.get("channels", {}).get("bot_commands")
        if bot_commands:
            ctx = self.bot.guild.get_channel(bot_commands)
            if self.bot.debug:
                await ctx.send(embed=embedder("CosmoGolem is in Debug mode!", color=Color.YELLOW))
            else:
                await ctx.send(embed=embedder("CosmoGolem is Online!", color=Color.GREEN))
        log.info("*** Client ready! ***")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ What happens when a bad command is invoked """
        if re.match(r"\d+.*", ctx.invoked_with):  # Started sentence with a price
            return
        log.error(
            "%s issued command but got an error: %s", ctx.message.author, str(error)
        )  # For regular command errors
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                embed=embedder(
                    f"Type `{self.bot.command_prefix}help` to see a list of available commands.",
                    title=str(error),
                    error=True,
                )
            )

        elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
            # For when using wrong arguments
            await ctx.send(
                embed=embedder(
                    f"Error: ```{str(error)}```\nType `{self.bot.command_prefix}help {ctx.invoked_with}` to get help.",
                    title=f"That's not how you `{ctx.invoked_with}`!",
                    error=True,
                )
            )

        else:  # IF you're here, the bot is broken.
            await ctx.send(
                embed=embedder(
                    description=f"Error: ```{str(error)}```\nSee logs for more details.",
                    title="Unexpected error!",
                    error=True,
                )
            )
            raise error


def setup(bot):
    """ Cog init """
    bot.add_cog(Handlers(bot))
