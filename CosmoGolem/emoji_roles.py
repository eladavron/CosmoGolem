""" Emoji Roles functionality """

import logging
import re
import emoji
from discord import NotFound, utils
from discord.ext import commands
from _settings import Settings
from _helpers import embedder

log = logging.getLogger("EmojiRoles")


class EmojiRoles(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Bind an emoji to a role in a specific channel.", aliases=["bind"])
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def bind_emoji(self, ctx, *args):
        """
        Bind an emoji to a message id and a role, so that reacting to that message will give that user that role.

        Args:
            A role name, a message ID, and an emoji - in no particular order.
        """
        await ctx.trigger_typing()
        server_roles = [x.name for x in self.bot.get_guild(self.bot.settings["server_id"]).roles]
        server_emojis = [x.id for x in self.bot.get_guild(self.bot.settings["server_id"]).emojis]
        emoji_string = None
        role = None
        message = None
        for arg in args:
            if emoji_id := resolve_emoji_id(arg):
                if not (emoji_id in server_emojis or arg in emoji.UNICODE_EMOJI):
                    log.error(
                        "%s tried binding a custom emoji from another server!",
                        ctx.message.author,
                    )
                    await ctx.send(
                        embed=embedder(f"emoji {arg} is neither in UNICODE nor in the current server!", error=True)
                    )
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
                    embed=embedder(
                        f"Couldn't recognize type of argument '{arg}'! It is not a channel, a role, or an emoji!",
                        error=True,
                    )
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
        if "emoji_roles" not in self.bot.settings:
            self.bot.settings["emoji_roles"] = {}
        if message.id not in self.bot.settings["emoji_roles"]:
            self.bot.settings["emoji_roles"][str(message.id)] = {}
        self.bot.settings["emoji_roles"][str(message.id)][emoji_string] = role
        await ctx.send(embed=embedder(f"Reacting {emoji_string} on {message.id} will now grant the role {role}"))
        self.bot.settings.save()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ If a reaction is added, checks if it's bount to that message and a role and grats it if so """
        # Check if this channel has any bindings
        message_reactions = self.bot.settings.get("emoji_roles", {}).get(str(payload.message_id), {})
        if str(payload.emoji) in message_reactions:  # If it does, check if this reaction is one of them
            role_name = message_reactions.get(str(payload.emoji))
            role = utils.get(self.bot.guild.roles, name=role_name)
            if role not in payload.member.roles:
                log.info(
                    "User %s has reacted with %s in %s and will be granted the role %s",
                    payload.member,
                    str(payload.emoji),
                    payload.message_id,
                    role_name,
                )
                await payload.member.add_roles(role)
                await payload.member.send(
                    embed=embedder(
                        title="Role Granted",
                        description=f"You have been granted the role {role_name} on {self.bot.guild.name}.",
                    )
                )
            else:
                log.info(
                    "User %s has reacted with %s in %s but already has the role %s",
                    payload.member,
                    str(payload.emoji),
                    payload.message_id,
                    role_name,
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """ If a reaction is added, checks if it's bount to that message and a role and removes it if so """
        # Check if this channel has any bindings
        message_reactions = self.bot.settings.get("emoji_roles", {}).get(str(payload.message_id), {})
        if str(payload.emoji) in message_reactions:  # If it does, check if this reaction is one of them
            role_name = message_reactions.get(str(payload.emoji))
            role = utils.get(self.bot.guild.roles, name=role_name)
            member = await self.bot.guild.fetch_member(payload.user_id)
            if role in member.roles:
                log.info(
                    "User %s has removed reaction %s from %s and the role %s will be removed from them.",
                    member.name,
                    str(payload.emoji),
                    payload.message_id,
                    role_name,
                )
                await member.remove_roles(role)
                await member.send(
                    embed=embedder(
                        title="Role Removed",
                        description=f"You no longer have the `{role_name}` on {self.bot.guild.name}.",
                    )
                )

    def resolve_emoji_id(query):
        """
        Resolve an emoji to either the Unicode set or a custom emoji in this server.

        Args:
            query (str): The emoji to try to resolve.

        Returns:
            int|str: Emoji ID (int) if custom, or ASCII code.
        """
        if unicode_emoji := emoji.UNICODE_EMOJI.get(query):
            return unicode_emoji
        custom_emoji_pattern = r"^\<a?\:(\S+)\:(\d+)\>$"
        if match := re.match(custom_emoji_pattern, query):
            return int(match.group(2))
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
