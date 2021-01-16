"""
Periodic tasks
"""
import re
import logging
import asyncio
from datetime import datetime
from discord.ext import commands
from _helpers import embedder, WEEKDAYS
from _settings import Settings

log = logging.getLogger("Reminders")


class TimedEvents(commands.Cog):
    """
    Execute all periodic tasks
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_tick = datetime.utcnow()
        asyncio.get_event_loop().create_task(self.timed_event_loop())

    async def timed_event_loop(self):
        while True:
            if self.bot.ready:
                self.bot.settings.reload()
                now = datetime.utcnow()
                for event in self.bot.settings.get("timed_events", {}).get(WEEKDAYS[now.weekday()], []):
                    if (
                        self.last_tick.hour <= event["hour"] <= now.hour
                        and self.last_tick.minute <= event["minute"] <= now.minute
                        and self.last_tick.minute != now.minute
                    ):
                        ctx = self.bot.guild.get_channel(event["channel"])
                        await ctx.send(embed=embedder(event["message"]))
                self.last_tick = now
            await asyncio.sleep(5)

    @commands.command()
    @commands.has_role(Settings.static_settings["mod_role_id"])
    async def set_timed_event(self, ctx, day: str, time: str, utc_offset: int, channel_name: str, *, message: str):
        if not -12 <= utc_offset <= 12:
            await ctx.send(embed=embedder("UTC offset must bet between -12 and +12!", error=True))
            log.info("%s tried to set a UTC Offset of %s for their bedtime", ctx.message.author.name, str(utc_offset))
            return
        weekdays = list(map(lambda x: x.lower(), WEEKDAYS))
        # Prase time
        time_match = re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$", time)
        if not time_match:
            await ctx.send(
                embed=embedder(f"{time} is not a valid time format! Please use HH:MM 24-hour format!", error=True)
            )
            return
        # Parse channel
        if not ctx.message.channel_mentions:
            log.error(
                '%s tried sending an echo to a non-existing or not-found channel "%s"',
                ctx.message.author,
                channel_name,
            )
            await ctx.send('Error! Could not find channel "%s"!', channel_name)
            return
        for day_ in day.split(","):
            try:
                weekday_index = weekdays.index(day_.lower())
                if not self.bot.settings.get("timed_events"):
                    self.bot.settings["timed_events"] = {
                        "Monday": [],
                        "Tuesday": [],
                        "Wednesday": [],
                        "Thursday": [],
                        "Friday": [],
                        "Saturday": [],
                        "Sunday": [],
                    }
                hour_in_tz = (int(time_match.group(1)) - utc_offset)
                if hour_in_tz >= 24:
                    hour_in_tz -= 24
                    weekday_index = (weekday_index + 1) % 7
                timed_event = {
                    "hour": hour_in_tz,
                    "minute": int(time_match.group(2)),
                    "message": message,
                    "channel": ctx.message.channel_mentions[0].id
                }
                self.bot.settings["timed_events"][WEEKDAYS[weekday_index]].append(timed_event)
                self.bot.settings.save()
                await ctx.send("Timed even saved.")
            except ValueError:
                await ctx.send(
                    embed=embedder(
                        f"{day_} is not a valid weekday! Valid options are: {', '.join(WEEKDAYS)}", error=True
                    )
                )
                return

def setup(bot):
    """ Cog Init """
    bot.add_cog(TimedEvents(bot))
