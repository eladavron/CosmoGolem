""" Module repsonsible for reading and writing settings to the settings json file """

import os
import sys
import json
import logging

log = logging.getLogger("Settings")

class Settings(dict):
    def __init__(self):
        dict.__init__(self)
        if not os.path.isfile("settings.json"):
            self.update({
                "bot_token": None,
                "server_id": None,
                "imgur": {
                    "id": None,
                    "secret": None,
                },
                "owners": [
                ],
                "users": {
                },
                "channels": {
                }
            })
            self.save()
            log.info("As this is the first run, a settings file has been created!")
            log.info("Please fill up the bot_token, imgur API keys, and add at least a single owner ID to the list,")
            log.info("then run the bot again.")
            sys.exit(0)

        with open("settings.json", "r") as settings_file:
            self.update(json.loads(settings_file.read()))

    def increase_counter(self, counter, amount):
        if "counters" not in self:
            self["counters"] = {}
        counters = self["counters"]

        if counter not in counters:
            counters[counter] = 0

        counters[counter] += amount
        self.save()

    def get_counter(self, counter):
        if "counters" not in self:
            self["counters"] = {}
        counters = self["counters"]

        if counter not in counters:
            counters[counter] = 0

        return counters[counter]

    def save(self):
        with open("settings.json", "w") as settings_file:
            settings_file.write(json.dumps(self, indent=4))