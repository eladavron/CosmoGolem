""" Emoji Roles functionality """

import logging
import discord
import re
import emoji
from discord import NotFound
from discord.ext import commands
from _settings import Settings

log = logging.getLogger("EmojiRoles")

settings = Settings()


class EmojiRoles(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Bind an emoji to a role in a specific channel.")
    @commands.has_role(settings["mod_role_id"])
    async def bind_emoji(self, ctx, *args):
        """
        Bind an emoji to a message id and a role, so that reacting to that message will give that user that role.

        Args:
            A role name, a message ID, and an emoji - in no particular order.
        """
        await ctx.trigger_typing()
        server_roles = [x.name for x in self.bot.get_guild(settings["server_id"]).roles]
        server_emojis = [x.id for x in self.bot.get_guild(settings["server_id"]).emojis]
        emoji_string = None
        role = None
        message = None
        for arg in args:
            if emoji_id := self.resolve_emoji_id(arg):
                if not (emoji_id in server_emojis or arg in emoji.UNICODE_EMOJI):
                    log.error(
                        "%s tried binding a custom emoji from another server!",
                        ctx.message.author,
                    )
                    await ctx.send("```Error, emoji %s is neither in UNICODE nor in the current server!```" % arg)
                    return
                emoji_string = arg
            elif arg in server_roles:
                role = arg
            elif not (message := await self.resolve_message(arg)):
                log.error(
                    "%s tried binding an emoji with an unrecognized argument: %s",
                    ctx.message.author,
                    arg,
                )
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
        if not message:
            log.error(
                "%s tried binding an emoji without a message to bind it to!.",
                ctx.message.author,
            )
            await ctx.send("You must supply a messag eID to bind an emoji to it... If you did, it was not recognized.")
            return

        log.info("Binding %s to role %s and message ID %s", emoji_string, role, message.id)
        if "emoji_roles" not in settings:
            settings["emoji_roles"] = {}
        if message.id not in settings["emoji_roles"]:
            settings["emoji_roles"][message.id] = {}
        settings["emoji_roles"][message.id][emoji_string] = role
        await ctx.send("Reacting %s on %s will now grant the role %s" % (emoji_string, message.id, role))
        settings.save()

    def resolve_emoji_id(self, query):
        """
        Resolve an emoji to either the Unicode set or a custom emoji in this server.

        Args:
            query (str): The emoji to try to resolve.

        Returns:
            int|str: Emoji ID (int) if custom, or ASCII code.
        """
        custom_emoji_pattern = r"^\<a?\:(\S+)\:(\d+)\>$"
        if query in emoji.UNICODE_EMOJI:
            string = query.encode("unicode-escape").decode("utf-8").replace("\\", "")
            return re.match(r"U0+(\S+)", string).group(1)
        elif match := re.match(custom_emoji_pattern, query):
            return int(match.group(2))
        else:
            return None

    async def resolve_message(self, message_id):
        """
        Finds and returns the message from this server this message ID resolves to, if any.

        Args:
            message_id (int): Message ID

        Returns:
            Message: The message if found, None if not
        """
        for channel in self.bot.guild.text_channels:
            try:
                return await channel.fetch_message(message_id)
            except NotFound:
                continue
        return None


def setup(bot):
    """ Cog Init """
    bot.add_cog(EmojiRoles(bot))
