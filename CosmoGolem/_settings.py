""" Module repsonsible for reading and writing settings to the settings json file """

import os
import sys
import json
import shutil
import logging
from datetime import datetime, timezone
from _helpers import SETTINGS_PATH

log = logging.getLogger("Settings")

# Resolved relative to the code, not DATA_FOLDER, so it's found even when CQXBOT_DATAPATH is customized.
TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "settings.template.json")

if not os.path.isfile(SETTINGS_PATH):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    shutil.copyfile(TEMPLATE_PATH, SETTINGS_PATH)
    # Logging isn't configured yet at import time, so print directly.
    print(f"As this is the first run, a settings file has been created at {SETTINGS_PATH}")
    print("Please fill up the bot_token, server_id, mod_role_id, imgur API keys, and add at least a single owner ID,")
    print("then run the bot again.")
    sys.exit(0)


class Settings(dict):
    """ A dictionary extension for setting, getting, and saving settings """

    with open(SETTINGS_PATH, "r") as settings_file:
        static_settings = json.loads(settings_file.read())

    def __init__(self):
        dict.__init__(self)

        with open(SETTINGS_PATH, "r") as settings_file:
            loaded_settings = json.loads(settings_file.read())

        required_settings = ["bot_token", "server_id", "mod_role_id", "owners", "command_prefix"]
        if not all(bool(loaded_settings.get(x)) for x in required_settings):
            raise SettingMissing(
                "A required setting is missing from your settings file! The required fields are: "
                + ", ".join(required_settings)
            )
        self.update(loaded_settings)

    def increase_counter(self, counter: str, amount: int):
        """ Increase a counter in the settings by a given amount """

        if "counters" not in self:
            self["counters"] = {}
        counters = self["counters"]

        if counter not in counters:
            counters[counter] = 0

        counters[counter] += amount
        self.save()

    def get_counter(self, counter: str):
        """Gets the current value of a given counter

        Args:
            counter (str): The counter whose value you want

        Returns:
            int: The value of the counter
        """
        if "counters" not in self:
            self["counters"] = {}
        counters = self["counters"]

        if counter not in counters:
            counters[counter] = 0

        return counters[counter]

    def save(self):
        """ Saves the current state of Settings to a file """
        with open(SETTINGS_PATH, "w") as settings_file:
            self.update({"timestamp": datetime.now(timezone.utc).isoformat()})
            settings_file.write(json.dumps(self, indent=4))


class SettingMissing(Exception):
    """ An exception raised when a required key is missing from the settings file """
