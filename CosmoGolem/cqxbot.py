"""
CosmoGolem's main module
"""
import logging
import argparse
import traceback
from tendo import singleton
from discord.ext import commands
from _settings import Settings
from _helpers import LOG_PATH

# Logging
format_str = "%(asctime)s [%(levelname)s][%(name)s] %(message)s"
formatter = logging.Formatter(format_str)
logging.basicConfig(level=logging.INFO, format=format_str)
handler = logging.FileHandler(LOG_PATH, encoding="utf-8", mode="a")
handler.setFormatter(formatter)
log = logging.getLogger()
log.addHandler(handler)

### Global Variables ##
class Bot(commands.Bot):
    """ An extension of the Bot command that also holds settings """
    def __init__(self, **kwargs):
        self.settings = Settings()
        self.debug = False
        super().__init__(owner_ids=self.settings["owners"], **kwargs)

    @property
    def guild(self):
        """ A shortcut for getting Guild ID """
        return self.get_guild(self.settings["server_id"])


bot = Bot(command_prefix="$", description="CosmoGolem 1.0", pm_help=True)


def startup(debug: bool):
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

    bot.debug = debug
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
        await ctx.send("🤘")


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
        await ctx.send("🤘")


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
        await ctx.send("🤘")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    singleton.SingleInstance()
    startup(args.debug)
