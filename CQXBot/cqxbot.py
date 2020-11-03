"""
cqxbot's main module
"""

import os
import sys
import asyncio
import argparse
import logging
import traceback
import importlib
from tendo import singleton

from _settings import Settings
from discord.ext import commands
from discord import Intents, utils

import _helpers as helpers
from _helpers import Color

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s][%(name)s] %(message)s')
handler = logging.FileHandler('discord.log', encoding='utf-8', mode='a')
log = logging.getLogger()
log.addHandler(handler)

settings = Settings()

### Global Variables ##
bot = commands.Bot(
    command_prefix='.',
    description='CosmoQuestX Bot 1.0',
    owner_ids=settings["owners"],
    pm_help=True
    )

def startup(debug):
    """
    Startup function
    """
    startup_extensions = ['handlers', 'commands', 'eggs', 'images', 'emoji_roles']
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except:
            log.error("Failed to load extension %s!\n%s", extension, traceback.format_exc())

    if not debug:
        bot.loop.create_task(looper())

    bot.run(settings.get("bot_token")) # This halts until the bot shuts down

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


@bot.event
async def on_raw_reaction_add(payload):
    # Check if this channel has any bindings
    channel_reactions = settings.get("emoji_roles", {}).get(str(payload.channel_id), {})
    if str(payload.emoji) in channel_reactions:  # If it does, check if this reaction is one of them
        role_name = channel_reactions.get(payload.emoji.name)
        log.info(
            "User %s has reacted with %s in %s and will be granted the role %s",
            payload.member,
            str(payload.emoji),
            payload.channel_id,
            role_name
        )
        guild = bot.get_guild(settings["server_id"])
        role = utils.get(guild.roles, name=role_name)
        await payload.member.add_roles(role)
        await guild.get_channel(payload.channel_id).send(f"```{payload.member.name} has been granted the role {role_name}```")


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
    startup(args.debug)