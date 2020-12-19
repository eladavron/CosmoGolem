""" A collection of global variables, functions, and enumgs """

import os
import traceback
import logging
import time
import tempfile
from enum import Enum
import requests
import discord

log = logging.getLogger("helpers")

DATA_FOLDER = os.environ.get("CQXBOT_DATAPATH", os.path.join(os.getcwd(), "data"))
LOG_PATH = os.path.join(DATA_FOLDER, "cxqbot.log")
SETTINGS_PATH = os.path.join(DATA_FOLDER, "settings.json")

### Enum Classes ###
class Color(Enum):
    """ Predefined Colors """
    RED = 0xFF0000
    NAVY = 0x000080
    AQUA = 0x00FFFF
    GREEN = 0x00FF00
    YELLOW = 0xFFFF00
    DEFAULT = 0x9B59B6


def get_channel_name(channel):
    """Given a channel, returns its name as a string.
    This is better than `ctx.channel.name` because DMChannel doesn't have `.name` as a proeprty.

    Args:
        channel (discord.TextChannel|discord.DMChannel): The channel to parse

    Returns:
        str: The channel name or "private message" if it's private.
    """
    if isinstance(channel, discord.TextChannel):
        return channel.name
    if isinstance(channel, discord.DMChannel):
        return "a private message"
    return "an unknown channel type"


def embedder(description: str, color:Color=None, title:str=None, error=False, **kwargs):
    """Wraps the given message in an embed with the given color.

    Args:
        message (str): The message to embed
        color (Color): The Color enum
        title (str, optional): The title of the embed. Defaults to "CosmoquestX Bot".
        error (bool, optional): Whether to apply error styling. Defaults to False.

    Returns:
        em: A discord embed obect
    """
    if not color:
        color = Color.RED if error else Color.DEFAULT
    if not title:
        title = "Error!" if error else None

    return discord.Embed(title=title, description=description, colour=color.value, **kwargs)


def check_timer(self, timer_name, runtime: int = 60 * 5):
    """
    Acts like a lock check.
    If the give timer name is not running (or finished)  returns True and starts the timer from 0.
    Otherwise returns False.

    Args:
        timer_name (str): The name of the timer to check.
        timeout (int): The number of seconds to run the timer for.

    Returns:
        bool: True if the timer is
    """
    if (timer_name not in self.timers) or self.timers[timer_name] == 0:
        self.timers[timer_name] = time.time()
        return True
    if (time.time() - self.timers[timer_name]) < runtime:
        return False
    self.timers[timer_name] = time.time()
    return True


async def exception_handler(exception, ctx=None):
    """ In case of an exception, print it to the user """
    if exception is discord.Forbidden:
        log.error("ERROR: Attempted to write to a forbidden channel")
    else:
        log.error("UNEXPECTED ERROR!")

    if ctx is not None:
        await ctx.send(f"```py\n{traceback.format_exc()}\n```")

    log.error(str(exception))
    log.error(traceback.format_exc())


async def save_file_and_send(ctx, path):
    """ A utility function to save a file and send it to the user """
    request = requests.get(path, allow_redirects=True)
    filename = os.path.basename(path)
    local_path = os.path.join(tempfile.gettempdir(), filename)
    with open(local_path, "wb") as temp:
        temp.write(request.content)
    await ctx.send(file=discord.File(local_path))
    os.remove(local_path)


log.info("Helpers loaded!")
