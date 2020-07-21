"""
cqxbot's main module
"""

import os, sys
import argparse
import asyncio
import logging
import traceback
import importlib
from tendo import singleton
from discord.ext import commands

import helpers

LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
SETTINGS = os.path.join(LOCAL_PATH, "settings.py")

if not os.path.isfile(SETTINGS):
    with open(SETTINGS, "w") as settings_file:
        settings_file.write("""# API Keys
bot_token = None  # REPLACE WITH BOT TOKEN
imgur_id = None  # REPLACE WITH IMGUR_ID
imgur_secret = None  # REPLACE WITH IMGUR_SECRET

# Channels
archive = None  # IF/WHEN there's an archive channel, put its ID here

# Users
Ambious = 194082034514132992  # Not really a secret
""")
    print("A settings file has been created!")
    print("Please edit it, fill in the blanks, and run the bot again.")
    sys.exit(0)

import settings

if not settings.bot_token:
    print("A bot token has not been set (hint: in settings.py). Can not continue!")
    sys.exit(1)

### Global Variables ##
bot = commands.Bot(command_prefix='.', description='CosmoQuestX Bot 1.0', owner_ids=[settings.Ambious], pm_help=True)

### Logging ###
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s][%(name)s] %(message)s')
handler = logging.FileHandler(os.path.join(LOCAL_PATH, 'discord.log'), encoding='utf-8', mode='a')
log = logging.getLogger('Main')
log.addHandler(handler)

def startup():
    """
    Startup function
    """
    startup_extensions = ['handlers', 'commands', 'eggs', 'images']
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except:
            log.error("Failed to load extension %s!\n%s", extension, traceback.format_exc())

    if not args.debug:
        bot.loop.create_task(looper())

    bot.run(settings.bot_token) # This halts until the bot shuts down

    # Here the bot is shutting down
    bot.loop.close()
    log.info('Done. Goodbye!')


### General Commands ###
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, module):
    """Loads an extension

    Args:
        module (str): The name of the module to load.
    """
    try:
        bot.load_extension(module)
    except:
        log.error("Failed to load extension %s\n%s", module, traceback.format_exc())
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        log.info("Module %s loaded!", module)
        await ctx.send('\N{OK HAND SIGN}')

@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, module):
    """Unloads a module

    Args:
        module (str): The name of the module to unload.
    """
    try:
        bot.unload_extension(module)
    except:
        log.error("Failed to unload extension %s\n%s", module, traceback.format_exc())
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        log.info("Module %s unloaded!", module)
        await ctx.send('\N{OK HAND SIGN}')

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, module):
    """Reloads a module

    Args:
        module (str): Name of module to reload.
    """
    try:
        if module == 'helpers':
            importlib.reload(helpers)
        else:
            bot.unload_extension(module)
            bot.load_extension(module)
    except:
        log.error("Failed to reload extension %s\n%s", module, traceback.format_exc())
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        log.info("Module %s reloaded!", module)
        await ctx.send('\N{OK HAND SIGN}')

async def looper():
    """
    Handles timed tasks
    """
    while True:
        await bot.wait_until_ready()

        import loopers
        await loopers.loopers(bot)
        del loopers

        await asyncio.sleep(300) # Wait 5 minutes

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()

    singleton.SingleInstance()
    startup()
