""" Generic Bot Commands """

import os
import io
import re
import logging

import pprint

import urbandictionary as ud

import discord
from discord.ext import commands

import helpers
from helpers import embed_wrapper, Color

from archive import archive, archive_server, parse_channel_role_overrides

import settings

log = logging.getLogger('Commands')

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

class Commands(commands.Cog):
    """ The Commands cog class """
    def __init__(self, bot):
        self.bot = bot

    ### Ownder Commands ###
    @commands.command()
    @commands.is_owner()
    async def exit(self, ctx):
        """ Quits the bot """
        log.info('Quitting!')
        await ctx.trigger_typing()
        await ctx.send(embed=embed_wrapper('Quitting, goodbye!', Color.RED))
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx):
        """ Sends the log files to the user. TODO: Cycle logs? Send only recent? """
        await ctx.send('```Sending logs...```')
        await ctx.trigger_typing()
        await ctx.message.author.send(file=discord.File(os.path.join(LOCAL_PATH, 'discord.log')))

    @commands.command()
    @commands.is_owner()
    async def clear_logs(self, ctx):
        """ Clears the log files """
        try:
            with open(os.path.join(LOCAL_PATH, 'discord.log'), 'w') as log_file:
                log_file.write("\n=========\n")
            log.info("Log cleared!")
            await ctx.send('\N{OK HAND SIGN}')
        except Exception as ex:
            helpers.exception_handler(ex, ctx)
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(help='Get the UrbanDictionary definition(s) for your query.')
    async def ud(self, ctx, *, query):
        """ Urban Dictionary search """
        compiled = re.search(r'(\d+)\s(.+)', query)
        if compiled is not None:
            query = compiled.group(2)
            max_lines = int(compiled.group(1))
        else:
            max_lines = 3
        log.info('Searching UrbanDictionary for \'%s\'', query)
        defList = ud.define(query)
        log.info('Found %d items!', len(defList))
        if defList:
            await ctx.send(embed=embed_wrapper('No UrbanDictionary definition found for `%s`' % query, Color.RED))
        else:
            await ctx.send('Found `%d` UrbanDictionary definition%s for `%s`:' % (len(defList), 's' if len(defList) > 1 else '', query))
            shown = 0
            for defin in defList:
                shown += 1
                if shown > max_lines:
                    break
                em = embed_wrapper('%s\n\n**Usage Example:**\n*%s*' % (defin.definition, defin.example), color=Color.cqxbot, title=defin.word)
                em.url = 'https://www.urbandictionary.com/define.php?term="%s"' % query.replace(' ', '+')
                em.set_footer(text='\N{THUMBS UP SIGN}: %d\t\t\N{THUMBS DOWN SIGN}: %d' % (defin.upvotes, defin.downvotes))
                await ctx.send(embed=em)
            if len(defList) > max_lines:
                await ctx.send('%d definitions not displayed.' % (len(defList) - max_lines))

    #Mod Commands
    @commands.command(help='Posts the given message or image to the given channel as the bot.')
    @commands.has_role('mods')
    async def echo(self, ctx, channel_name, *, echoString=None):
        """ Allows puppeteering the bot by having it send commands or images to other channels """
        if not ctx.message.channel_mentions:
            log.error('%s tried sending an echo to a non-existing or not-found channel "%s"', ctx.message.author, channel_name)
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
                await ctx.send('Cannot echo an empty message!')
            await channel.send(echoString)

    ### Generic Commands ###
    @commands.command(help='Gives generic details about the bot.')
    async def info(self, ctx):
        """ Handles the "info" command """
        await ctx.trigger_typing()
        await ctx.send(embed=embed_wrapper(message='Written in Python 3.8 by Ambious.', color=Color.AQUA))

    @commands.command(help='Archives a channel to a file then uploads to the where you request.')
    @commands.has_role('Moderator')
    async def archive(self, ctx, channel_name):
        """ Archives an entire channel into a json and uploads it to the archive channel """
        if not ctx.message.channel_mentions:
            log.error('%s tried archiving a non-existing channel %s', ctx.message.author, channel_name)
            await ctx.send('```Error! Could not find channel "%s"!```' % channel_name)
            return

        if len(ctx.message.channel_mentions) >= 1:
            channel = ctx.message.channel_mentions[0]

        if len(ctx.message.channel_mentions) >= 2:
            where_to_upload = ctx.message.channel_mentions[1]
        else:
            where_to_upload = ctx.channel

        await archive(channel, where_to_upload)

    @commands.command(help='Archives the entire server.')
    @commands.has_role('Moderator')
    async def archive_server(self, ctx):
        """ Archives an entire server into a jsons and uploads it to a zip """
        if ctx.message.channel_mentions:
            where_to_upload = ctx.message.channel_mentions[0]
        else:
            where_to_upload = ctx.channel

        await archive_server(where_to_upload)

    @commands.command(help='Archives the entire server.')
    @commands.has_role('Moderator')
    async def channel_roles(self, ctx):
        """ Archives an entire server into a jsons and uploads it to a zip """
        if ctx.message.channel_mentions:
            which_channel = ctx.message.channel_mentions[0]
        else:
            which_channel = ctx.channel

        await ctx.channel.send(f"```\n{pprint.pformat(parse_channel_role_overrides, indent=4)}\n```")


def setup(bot):
    """ Cog Init """
    bot.add_cog(Commands(bot))
