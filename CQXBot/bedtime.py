""" Emoji Roles functionality """

import logging
import discord
import re
import datetime
from discord import NotFound
from discord.ext import commands
from _settings import Settings
import _helpers as helpers

log = logging.getLogger("EmojiRoles")

settings = Settings()


class Bedtime(commands.Cog):
    """ The handlers cog class """

    def __init__(self, bot):
        self.bot = bot
        self.timers = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if user_bedtime := settings.get("bedtime", {}).get(str(message.author.id)):
            utc_now = datetime.datetime.utcnow()
            time_in_tz = utc_now + datetime.timedelta(hours=user_bedtime["utc_offset"])
            bedtime = user_bedtime["bedtime"]
            morning = user_bedtime["morning"]
            if Bedtime.check_if_between_times(bedtime, morning, time_in_tz):
                if helpers.check_timer(self, "bedtime_" + str(message.author.id)):
                    log.info("%s has been told to go to bed!", message.author.name)
                    await message.channel.send(
                        f"```Hey {message.author.name}, it's past your bedtime! Go to bed! 🛌💤```"
                    )
                else:
                    log.info("%s was up past his betdime but already warned recently")

    @commands.command(help="Set a bedtime, during which if the user posts, they'll be scolded.")
    async def set_bedtime(self, ctx, bedtime: int, morning: int, utc_offset: int):
        await ctx.trigger_typing()
        if not -12 <= utc_offset <= 12:
            await ctx.send("```UTC offset must bet between -12 and +12!```")
            log.info("%s tried to set a UTC Offset of %s for their bedtime", ctx.message.author.name, str(utc_offset))
            return
        if not 0 <= bedtime <= 23:
            log.info("%s tried to set bedtime %s", ctx.message.author.name, str(bedtime))
            await ctx.send("```Bedtime and morning must be integers between 0 and 23```")
            return
        if not 0 <= morning <= 23:
            log.info("%s tried to set morning time of %s", ctx.message.author.name, str(morning))
            await ctx.send("```Bedtime and morning must be integers between 0 and 23```")
            return
        if morning == bedtime:
            log.info("%s tried to set morning equal to bedtime", ctx.message.author.name)
            await ctx.send("```Bedtime and morning must be different!```")
            return
        user_bedtime = {
            "utc_offset": utc_offset,
            "bedtime": bedtime,
            "morning": morning
        }
        log.info("Settings bedtime for %s (%s): %s", ctx.message.author.name, str(ctx.message.author.id), user_bedtime)
        if not settings.get("bedtime"):
            settings["bedtime"] = {}
        settings["bedtime"][str(ctx.message.author.id)] = user_bedtime
        settings.save()
        await self.get_bedtime(ctx)

    @commands.command(help="Gets the user bedtime")
    async def get_bedtime(self, ctx):
        await ctx.trigger_typing()
        if user_bedtime := settings.get("bedtime", {}).get(str(ctx.message.author.id)):
            utc_offset = user_bedtime["utc_offset"]
            await ctx.send(
                "```%s's bedtime is set between %s and %s in %s```"
                % (
                    ctx.message.author.name,
                    str(user_bedtime["bedtime"]),
                    str(user_bedtime["morning"]),
                    "UTC" + str(utc_offset) if utc_offset < 0 else "UTC+" + str(utc_offset)
                )
            )
        else:
            await ctx.send("```%s does not have a bedtime set.```" % ctx.message.author.name)

    @commands.command(help="A bedtime helper")
    async def bedtime(self, ctx):
        await ctx.send("```To set your bedtime, type .set_bedtime <bedtime> <morning> <utc_offset>\n"
            "with <bedtime> and <morning> being integers between 0 and 23, and <utc_offset> being between -12 and 12.\n"
            "\nTo check your bedtime, type .get_bedtime\nTo remove your bedtime, type .remove_bedtime```"
        )

    @commands.command(help="Removes the user's bedtime")
    async def remove_bedtime(self, ctx):
        await ctx.trigger_typing()
        if settings.get("bedtime", {}).get(str(ctx.message.author.id)):
            del settings["bedtime"][str(ctx.message.author.id)]
            settings.save()
            log.info("Removing bedtime for %s (%s)", ctx.message.author.name, str(ctx.message.author.id))
            await ctx.send("```%s's bedtime has been removed.```" % ctx.message.author.name)
        else:
            await ctx.send("```%s does not have a bedtime set.```" % ctx.message.author.name)

    @staticmethod
    def check_if_between_times(start: int, end: int, time_to_check: datetime.datetime):
        if start < end:  # If 'morning' is not after midnight comapred to bedtime
            return start <= time_to_check.hour <= end
        return start <= time_to_check.hour or time_to_check.hour < end


def setup(bot):
    """ Cog Init """
    bot.add_cog(Bedtime(bot))
