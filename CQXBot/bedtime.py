""" Emoji Roles functionality """

import logging
import discord
import re
import datetime
from discord import NotFound
from discord.ext import commands
from _helpers import embedder, check_timer

log = logging.getLogger("EmojiRoles")


class Bedtime(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot
        self.timers = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if user_bedtime := self.bot.settings.get("bedtime", {}).get(str(message.author.id)):
            utc_now = datetime.datetime.utcnow()
            time_in_tz = utc_now + datetime.timedelta(hours=user_bedtime["utc_offset"])
            bedtime = user_bedtime["bedtime"]
            morning = user_bedtime["morning"]
            if Bedtime.check_if_between_times(bedtime, morning, time_in_tz):
                if check_timer(self, "bedtime_" + str(message.author.id)):
                    log.info("%s has been told to go to bed!", message.author.name)
                    await message.channel.send(
                        embed=embedder(
                            f"Hey {message.author.mention}, it's past your bedtime! Go to bed! 🛌💤", title="Bedtime!"
                        )
                    )
                else:
                    log.info("%s was up past his betdime but already warned recently", message.author)

    @commands.command(help="Set a bedtime, during which if the user posts, they'll be scolded.")
    async def set_bedtime(self, ctx, bedtime: int, morning: int, utc_offset: int):
        await ctx.trigger_typing()
        if not -12 <= utc_offset <= 12:
            await ctx.send(embed=embedder("UTC offset must bet between -12 and +12!", error=True))
            log.info("%s tried to set a UTC Offset of %s for their bedtime", ctx.message.author.name, str(utc_offset))
            return
        if not 0 <= bedtime <= 23:
            log.info("%s tried to set bedtime %s", ctx.message.author.name, str(bedtime))
            await ctx.send(embed=embedder("Bedtime and morning must be integers between 0 and 23", error=True))
            return
        if not 0 <= morning <= 23:
            log.info("%s tried to set morning time of %s", ctx.message.author.name, str(morning))
            await ctx.send(embed=embedder("Bedtime and morning must be integers between 0 and 23", error=True))
            return
        if morning == bedtime:
            log.info("%s tried to set morning equal to bedtime", ctx.message.author.name)
            await ctx.send(embed=embedder("Bedtime and morning must be different!", error=True))
            return
        user_bedtime = {"utc_offset": utc_offset, "bedtime": bedtime, "morning": morning}
        log.info("Settings bedtime for %s (%s): %s", ctx.message.author.name, str(ctx.message.author.id), user_bedtime)
        if not self.bot.settings.get("bedtime"):
            self.bot.settings["bedtime"] = {}
        self.bot.settings["bedtime"][str(ctx.message.author.id)] = user_bedtime
        self.bot.settings.save()
        await self.get_bedtime(ctx)

    @commands.command(help="Gets the user bedtime")
    async def get_bedtime(self, ctx):
        await ctx.trigger_typing()
        if user_bedtime := self.bot.settings.get("bedtime", {}).get(str(ctx.message.author.id)):
            utc_offset = user_bedtime["utc_offset"]
            await ctx.send(
                embed=embedder(
                    "%s's bedtime is set between %s and %s in %s"
                    % (
                        ctx.message.author.mention,
                        str(user_bedtime["bedtime"]),
                        str(user_bedtime["morning"]),
                        "UTC" + str(utc_offset) if utc_offset < 0 else "UTC+" + str(utc_offset),
                    )
                )
            )
        else:
            await ctx.send(embed=embedder(f"{ctx.message.author.mention} does not have a bedtime set."))

    @commands.command(help="A bedtime helper")
    async def bedtime(self, ctx):
        await ctx.send(
            embed=embedder(
                "To set your bedtime, type `.set_bedtime <bedtime> <morning> <utc_offset>`\n"
                "with `<bedtime>` and `<morning>` being integers between 0 and 23, and `<utc_offset>` being between -12 and 12.\n"
                "\nTo check your bedtime, type `.get_bedtime`\nTo remove your bedtime, type `.remove_bedtime`"
            )
        )

    @commands.command(help="Removes the user's bedtime")
    async def remove_bedtime(self, ctx):
        await ctx.trigger_typing()
        if self.bot.settings.get("bedtime", {}).get(str(ctx.message.author.id)):
            del self.bot.settings["bedtime"][str(ctx.message.author.id)]
            self.bot.settings.save()
            log.info("Removing bedtime for %s (%s)", ctx.message.author.name, str(ctx.message.author.id))
            await ctx.send(embed=embedder(f"{ctx.message.author.mention}'s bedtime has been removed."))
        else:
            await ctx.send(embed=embedder(f"{ctx.message.author.mention} does not have a bedtime set."))

    @staticmethod
    def check_if_between_times(start: int, end: int, time_to_check: datetime.datetime):
        if start < end:  # If 'morning' is not after midnight comapred to bedtime
            return start <= time_to_check.hour <= end
        return start <= time_to_check.hour or time_to_check.hour < end


def setup(bot):
    """ Cog Init """
    bot.add_cog(Bedtime(bot))
