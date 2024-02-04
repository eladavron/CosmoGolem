""" Generic Bot Commands """

import io
import sys
import logging

import discord
from discord.ext import commands
from _settings import Settings
from _helpers import Color, LOG_PATH, embedder, exception_handler
from archive import archive, archive_server

log = logging.getLogger("Commands")


class Commands(commands.Cog):
    """ The Commands cog class """

    def __init__(self, bot):
        self.bot = bot

    ### Ownder Commands ###
    @commands.command(aliases=["quit"])
    @commands.is_owner()
    async def exit(self, ctx):
        """ Quits the bot """
        log.info("Quitting!")
        await ctx.typing()
        await ctx.send(embed=embedder(description="Quitting, goodbye!"))
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx):
        """ Sends the log files to the user. TODO: Cycle logs? Send only recent? """
        await ctx.send(embed=embedder("Sending logs..."))
        await ctx.typing()
        await ctx.message.author.send(file=discord.File(LOG_PATH))

    @commands.command()
    @commands.is_owner()
    async def clear_logs(self, ctx):
        """ Clears the log files """
        try:
            with open(LOG_PATH, "w") as log_file:
                log_file.write("\n=========\n")
            log.info("Log cleared!")
            await ctx.send("🤘")
        except Exception as ex:
            await exception_handler(ex, ctx)
        else:
            await ctx.send("🤘")

    # Mod Commands
    @commands.command(help="Posts the given message or image to the given channel as the bot.")
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def echo(self, ctx, channel_name, *, echo_string=None):
        """ Allows puppeteering the bot by having it send commands or images to other channels """
        if not ctx.message.channel_mentions:
            log.error(
                '%s tried sending an echo to a non-existing or not-found channel "%s"',
                ctx.message.author,
                channel_name,
            )
            await ctx.send('Error! Could not find channel "%s"!', channel_name)
        else:
            channel = ctx.message.channel_mentions[0]
            log.info('%s echoed "%s" to "%s"', ctx.message.author, echo_string, channel_name)
            if ctx.message.attachments:
                for att in ctx.message.attachments:
                    file_attach = io.BytesIO()
                    filename = att.filename
                    await att.save(file_attach)
                    file_attach.seek(0)
                    await channel.send(file=discord.File(file_attach, filename=filename))
            elif echo_string is None:
                await ctx.send("Cannot echo an empty message!")
            await channel.send(embed=embedder(echo_string))

    ### Generic Commands ###
    @commands.command(help="Gives generic details about the bot.")
    async def info(self, ctx):
        """ Handles the "info" command """
        await ctx.typing()
        await ctx.send(
            embed=embedder(
                f"Written in Python {sys.version_info.major}.{sys.version_info.minor} by Ambious"
                "\nSource code available at: https://github.com/eladavron/CosmoGolem",
                title="CosmoGolem",
                color=Color.AQUA
            )
        )

    @commands.command(help="Archives a channel to a file then uploads to the where you request.")
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def archive(self, ctx, channel_name):
        """ Archives an entire channel into a json and uploads it to the archive channel """
        if not ctx.message.channel_mentions:
            log.error("%s tried archiving a non-existing channel %s", ctx.message.author, channel_name)
            await ctx.send(embed=embedder(f'Could not find channel "{channel_name}"', error=True))
            return

        if len(ctx.message.channel_mentions) >= 1:
            channel = ctx.message.channel_mentions[0]

        if len(ctx.message.channel_mentions) >= 2:
            where_to_upload = ctx.message.channel_mentions[1]
        else:
            where_to_upload = ctx.channel

        await archive(channel, where_to_upload)

    @commands.command(help="Archives the entire server.")
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def archive_server(self, ctx):
        """ Archives an entire server into a jsons and uploads it to a zip """
        if ctx.message.channel_mentions:
            where_to_upload = ctx.message.channel_mentions[0]
        else:
            where_to_upload = ctx.channel

        await archive_server(where_to_upload)


async def setup(bot):
    """ Cog Init """
    await bot.add_cog(Commands(bot))
