import os
import traceback
import logging
import time
import configparser
from enum import Enum
import requests
import discord

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

log = logging.getLogger('helpers')

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

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

def increase_counter(counter, amount):
    config.read(CONFIG_PATH)
    try:
        current = int(config.get('counters', counter))

    except configparser.NoSectionError:
        config.add_section('counters')
        current = 0

    config.set('counters', counter, value=str(current + amount))
    with open(CONFIG_PATH, 'w') as configWriter:
        config.write(configWriter)

def get_counter(counter):
    config.read(CONFIG_PATH)
    if config.has_section('counters') and config.has_option('counters', counter):
        return int(config['counters'][counter])
    else:
        if not config.has_section('counters'):
            config.add_section('counters')
        config.set('counters', counter, '0')
        with open(CONFIG_PATH, 'w') as configWriter:
            config.write(configWriter)
        return 0

def check_timer(self, timer_name):
    if (timer_name not in self.timers) or self.timers[timer_name] == 0:
        self.timers[timer_name] = time.time()
        return True
    else:
        if (time.time() - self.timers[timer_name]) < (60 * 5):
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
    print(path)
    open(LOCAL_PATH + '/temp.png', 'wb').write(r.content)
    await ctx.send(file=discord.File(LOCAL_PATH + '/temp.png'))
    os.remove(LOCAL_PATH + '/temp.png')

log.info('Helpers loaded!')
