""" Emoji Roles functionality """

import logging
import discord
import re
import emoji
from discord.ext import commands
from cqxbot import settings

log = logging.getLogger('EmojiRoles')

class EmojiRoles(commands.Cog):
    """ The handlers cog class """
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='Bind an emoji to a role in a specific channel.')
    async def bind_emoji(self, ctx, *args):
        await ctx.trigger_typing()
        if not ctx.message.channel_mentions:
            log.error('%s tried binding without specifying a valid channel!', ctx.message.author)
            await ctx.send('```Error! Please specify channel to bind to by mentioning it with the # sign!```')
            return

        channels = ctx.message.channel_mentions
        server_roles = [x.name for x in self.bot.get_guild(settings["server_id"]).roles]
        server_emojis = [x.id for x in self.bot.get_guild(settings["server_id"]).emojis]
        emoji_string = None
        role = None
        for arg in args:
            if emoji_id := self.resolve_emoji_id(arg):
                if not (emoji_id in server_emojis or arg in emoji.UNICODE_EMOJI):
                    log.error("%s tried binding a custom emoji from another server!", ctx.message.author)
                    await ctx.send(
                        '```Error, emoji %s is neither in UNICODE nor in the current server!```'
                        % arg
                    )
                    return
                emoji_string = arg
            elif arg in server_roles:
                role = arg
            elif arg not in [x.mention for x in channels]:
                log.error("%s tried binding an emoji with an unrecognized argument: %s", ctx.message.author, arg)
                await ctx.send(
                    '```Error, couldn\'t recognize type of argument "%s"! It is not a channel, a role, or an emoji!```'
                    % arg
                )
                return
        if not emoji_string:
            log.error("%s tried binding an emoji without an emoji.", ctx.message.author)
            await ctx.send("You must supply an emoji to bind an emoji... If you did, it was not recognized.")
            return
        if not role:
            log.error("%s tried binding an emoji without a role.", ctx.message.author)
            await ctx.send("You must supply a role to bind an emoji to a role... If you did, it was not recognized.")
            return

        log.info("Binding %s to %s in %s", emoji_string, role, ", ".join([x.name for x in channels]))
        for channel in channels:
            if "emoji_roles" not in settings:
                settings["emoji_roles"] = {}
            if channel.id not in settings["emoji_roles"]:
                settings["emoji_roles"][channel.id] = {}
            settings["emoji_roles"][channel.id][emoji_string] = role
            await ctx.send('%s is now bound to the role %s in %s' % (emoji_string, role, channel.name))
        settings.save()


    def resolve_emoji_id(self, query):
        custom_emoji_pattern = r'^\<a?\:(\S+)\:(\d+)\>$'
        if query in emoji.UNICODE_EMOJI:
            string = query.encode('unicode-escape').decode('utf-8').replace('\\', '')
            return re.match(r'U0+(\S+)', string).group(1)
        elif match := re.match(custom_emoji_pattern, query):
            return int(match.group(2))
        else:
            return None

def setup(bot):
    """ Cog Init """
    bot.add_cog(EmojiRoles(bot))
