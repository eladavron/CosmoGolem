import os
import traceback
import logging
import time
import tempfile
from enum import Enum
import requests
import discord

log = logging.getLogger('helpers')

### Enum Classes ###
class Color(Enum):
    RED = 0xFF0000
    NAVY = 0x000080
    AQUA = 0x00FFFF
    LIME = 0x00FF00
    YELLOW = 0xFFFF00
    cqxbot = 0x9b59b6

def get_channel_name(channel):
    if isinstance(channel, discord.TextChannel):
        return channel.name
    elif isinstance(channel, discord.DMChannel):
        return 'a private message'
    else:
        return 'an unknown channel type'

def embed_wrapper(message, color, title='CosmoquestX Bot'):
    em = discord.Embed(title=title, description=message, colour=color.value)
    return em


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
    else:
        if (time.time() - self.timers[timer_name]) < runtime:
            return False
        else:
            self.timers[timer_name] = time.time()
            return True

async def exception_handler(exception, ctx=None):
    if exception is discord.Forbidden:
        log.error('ERROR: Attempted to write to a forbidden channel')
    else:
        log.error('UNEXPECTED ERROR!')

    if ctx is not None:
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')

    log.error(str(exception))
    log.error(traceback.format_exc())

async def save_file_and_send(ctx, path):
    r = requests.get(path, allow_redirects=True)
    filename = os.path.basename(path)
    local_path = os.path.join(tempfile.gettempdir(), filename)
    with open(tempfile, 'wb') as f:
        f.write(r.content)
    await ctx.send(file=discord.File(local_path))
    os.remove(local_path)

log.info('Helpers loaded!')
