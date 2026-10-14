"""
The module responsible for banning anyone who posts in a bot-trap channel.
"""

import logging
import discord
from discord import Message, Member
from discord.ext import commands
from _helpers import embedder, Color

log = logging.getLogger("BotTrap")

# Discord's maximum for purging a banned user's messages (7 days)
PURGE_SECONDS = 7 * 24 * 60 * 60


class BotTrap(commands.Cog):
    """The bot-trap module class"""

    def __init__(self, bot):
        self.bot = bot

    def is_exempt(self, member: Member) -> bool:
        """Whether the given member is allowed to post in a bot-trap channel"""
        return (
            member.bot
            or member.id in self.bot.settings.get("owners", [])
            or member.guild_permissions.administrator
            or any(role.id == self.bot.settings.get("mod_role_id") for role in member.roles)
        )

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        """Ban non-exempt members who post in a bot-trap channel"""
        # Skip DMs and webhook messages, whose author is a plain User without roles/permissions
        if message.guild is None or not isinstance(message.author, Member):
            return
        if message.channel.id not in self.bot.settings.get("channels", {}).get("bot_trap", []):
            return
        author = message.author
        if self.is_exempt(author):
            return

        try:
            await message.guild.ban(
                author,
                reason=f"Posted in bot-trap channel #{message.channel.name}",
                delete_message_seconds=PURGE_SECONDS,
            )
        except (discord.Forbidden, discord.HTTPException) as error:
            log.error("Failed to ban %s (%d) from bot-trap channel %s: %s", author, author.id, message.channel, error)
            return

        log.warning("Banned %s (%d) for posting in bot-trap channel %s", author, author.id, message.channel)

        report_channel_id = self.bot.settings.get("channels", {}).get("bot_commands")
        if report_channel := message.guild.get_channel(report_channel_id or 0):
            # Embed descriptions max out at 4096 chars, and escaping markdown can up to double the length
            content = message.content if len(message.content) <= 1000 else message.content[:1000] + "…"
            await report_channel.send(
                embed=embedder(
                    description=(
                        f"Banned {author.mention} (`{author}`, ID `{author.id}`) "
                        f"for posting in {message.channel.mention}.\n\n"
                        f"**Message:**\n{discord.utils.escape_markdown(content) or '*(no text)*'}"
                    ),
                    title="Bot Trap",
                    color=Color.RED,
                )
            )


async def setup(bot):
    """Cog Definition"""
    await bot.add_cog(BotTrap(bot))
