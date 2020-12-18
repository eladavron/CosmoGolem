""" Generic Bot Commands """

import os
import io
import re
import logging

import pprint

import urbandictionary as ud

import discord
from discord.ext import commands
from _settings import Settings
from _helpers import Color, LOG_PATH, embedder, exception_handler
from archive import archive, archive_server, parse_channel_role_overrides

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
        await ctx.trigger_typing()
        await ctx.send(embed=embedder(description="Quitting, goodbye!"))
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx):
        """ Sends the log files to the user. TODO: Cycle logs? Send only recent? """
        await ctx.send(embed=embedder("Sending logs..."))
        await ctx.trigger_typing()
        await ctx.message.author.send(file=discord.File(LOG_PATH))

    @commands.command()
    @commands.is_owner()
    async def clear_logs(self, ctx):
        """ Clears the log files """
        try:
            with open(LOG_PATH) as log_file:
                log_file.write("\n=========\n")
            log.info("Log cleared!")
            await ctx.send("\N{OK HAND SIGN}")
        except Exception as ex:
            await exception_handler(ex, ctx)
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.command(help="Get the UrbanDictionary definition(s) for your query.")
    async def ud(self, ctx, *, query):
        """ Urban Dictionary search """
        compiled = re.search(r"(\d+)\s(.+)", query)
        if compiled is not None:
            query = compiled.group(2)
            max_lines = int(compiled.group(1))
        else:
            max_lines = 3
        log.info("Searching UrbanDictionary for '%s'", query)
        defList = ud.define(query)
        log.info("Found %d items!", len(defList))
        if defList:
            await ctx.send(embed=embedder(description=f"No UrbanDictionary definition found for '{query}'", error=True))

        else:
            await ctx.send(
                "Found `%d` UrbanDictionary definition%s for `%s`:"
                % (len(defList), "s" if len(defList) > 1 else "", query)
            )
            shown = 0
            for defin in defList:
                shown += 1
                if shown > max_lines:
                    break
                em = embedder(
                    description=f"{defin.definition}\n\n**Usage Example:**\n*{defin.example}*",
                    title=defin.word,
                )
                em.url = 'https://www.urbandictionary.com/define.php?term="%s"' % query.replace(" ", "+")
                em.set_footer(
                    text="\N{THUMBS UP SIGN}: %d\t\t\N{THUMBS DOWN SIGN}: %d" % (defin.upvotes, defin.downvotes)
                )
                await ctx.send(embed=em)
            if len(defList) > max_lines:
                await ctx.send("%d definitions not displayed." % (len(defList) - max_lines))

    # Mod Commands
    @commands.command(help="Posts the given message or image to the given channel as the bot.")
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def echo(self, ctx, channel_name, *, echoString=None):
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
            log.info('%s echoed "%s" to "%s"', ctx.message.author, echoString, channel_name)
            if ctx.message.attachments:
                for att in ctx.message.attachments:
                    f = io.BytesIO()
                    filename = att.filename
                    await att.save(f)
                    f.seek(0)
                    await channel.send(file=discord.File(f, filename=filename))
            elif echoString is None:
                await ctx.send("Cannot echo an empty message!")
            await channel.send(embed=embedder(echoString))

    ### Generic Commands ###
    @commands.command(help="Gives generic details about the bot.")
    async def info(self, ctx):
        """ Handles the "info" command """
        await ctx.trigger_typing()
        await ctx.send(embed=embedder("Written in Python 3.9 by Ambious", title="CosmoGolem", color=Color.AQUA))

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


def setup(bot):
    """ Cog Init """
    bot.add_cog(Commands(bot))
