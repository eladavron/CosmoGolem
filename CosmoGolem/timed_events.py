"""
Periodic tasks
"""
import re
import logging
import threading
import time
from datetime import datetime
from discord.ext import commands
from _helpers import embedder, WEEKDAYS

log = logging.getLogger("Reminders")


class TimedEvents(commands.Cog):
    """
    Execute all periodic tasks
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_tick = datetime.utcnow()
        thread = threading.Thread(target=self.timed_event_loop)
        thread.daemon = True
        thread.start()
        self.thread = thread

    async def timed_event_loop(self):
        while True:
            log.debug("Checking for timed events...")
            self.bot.settings.reload()
            now = datetime.utcnow()
            for event in self.bot.settings.get("timed_events", {}).get(str(now.weekday)):
                if (
                    self.last_tick.hour() <= event["hour"] <= now.hour()
                    and self.last_tick.minute() <= event["minute"] <= now.minute()
                ):
                    ctx = self.bot.guild.get_channel(event["channel"])
                    await ctx.send(embed=embedder(event["message"]))
            self.last_tick = now
            time.sleep(60)

    @commands.command()
    async def set_timed_event(self, ctx, day: str, time: str, channel_name: str, *, message: str):
        self.bot.settings.lo
        days = []
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
                timed_event = {
                    "hour": int(time_match.group(1)),
                    "minute": int(time_match.group(2)),
                    "message": message,
                    "channel": channel_name
                }
                self.bot.settings["timed_events"][WEEKDAYS[weekday_index]] = timed_event
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