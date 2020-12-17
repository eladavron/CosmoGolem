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
from discord.ext import commands
from discord import Intents, utils, Embed
from _settings import Settings
from _helpers import Color, LOG_PATH, embedder

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s][%(name)s] %(message)s")
handler = logging.FileHandler(LOG_PATH, encoding="utf-8", mode="a")
log = logging.getLogger()
log.addHandler(handler)

### Global Variables ##
class Bot(commands.Bot):
    def __init__(self, **kwargs):
        self.settings = Settings()
        super().__init__(owner_ids=self.settings["owners"], **kwargs)

    @property
    def guild(self):
        return self.get_guild(self.settings["server_id"])


bot = Bot(command_prefix="$", description="CosmoQuestX Bot 1.0", pm_help=True)


def startup(debug):
    """
    Startup function
    """
    startup_extensions = [
        "handlers",
        "commands",
        "eggs",
        "images",
        "emoji_roles",
        "bedtime",
    ]
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except:
            log.error("Failed to load extension %s!\n%s", extension, traceback.format_exc())

    if not debug:
        bot.loop.create_task(looper())

    bot.run(bot.settings.get("bot_token"))  # This halts until the bot shuts down

    # Here the bot is shutting down
    bot.loop.close()
    log.info("Done. Goodbye!")


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
        await ctx.send(f"```py\n{traceback.format_exc()}\n```")
    else:
        log.info("Module %s loaded!", module)
        await ctx.send("\N{OK HAND SIGN}")


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
        await ctx.send(f"```py\n{traceback.format_exc()}\n```")
    else:
        log.info("Module %s unloaded!", module)
        await ctx.send("\N{OK HAND SIGN}")


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, module):
    """Reloads a module

    Args:
        module (str): Name of module to reload.
    """
    try:
        bot.unload_extension(module)
        bot.load_extension(module)
    except:
        log.error("Failed to reload extension %s\n%s", module, traceback.format_exc())
        await ctx.send(f"```py\n{traceback.format_exc()}\n```")
    else:
        log.info("Module %s reloaded!", module)
        await ctx.send("\N{OK HAND SIGN}")


@bot.event
async def on_raw_reaction_add(payload):
    # Check if this channel has any bindings
    message_reactions = bot.settings.get("emoji_roles", {}).get(str(payload.message_id), {})
    if str(payload.emoji) in message_reactions:  # If it does, check if this reaction is one of them
        role_name = message_reactions.get(str(payload.emoji))
        log.info(
            "User %s has reacted with %s in %s and will be granted the role %s",
            payload.member,
            str(payload.emoji),
            payload.message_id,
            role_name,
        )
        role = utils.get(bot.guild.roles, name=role_name)
        await payload.member.add_roles(role)
        await payload.member.send(
            embed=embedder(
                title="Role Granted",
                description=f"{payload.member.name} has been granted the role {role_name}",
            )
        )


async def looper():
    """
    Handles timed tasks
    """
    while True:
        await bot.wait_until_ready()

        import loopers

        await loopers.loopers(bot)
        del loopers

        await asyncio.sleep(300)  # Wait 5 minutes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    singleton.SingleInstance()
    startup(args.debug)
