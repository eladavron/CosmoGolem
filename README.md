# CosmoGolem
A bot for the CosmoQuestX Discord Server.

## Docker (for deploying)
The `Dockerfile` can be built like a regular docker file, using `docker build .`
Howerver it is highly recommended to
use `docker compose`:
* [Download and Install Docker](https://www.docker.com/get-started)
* For ubuntu, first install docker-compose using `sudo apt update && sudo apg-get install docker-compose-plugin`  
  Docker Desktop for Windows will have it pre-installed.
* Navigate to the root of this repostory and run the bot using `docker compose up -d`  
  (You can remove the `-d` to see the log output in the console, but once you close the console the bot will also close)

## Python 3.12 (for developing)
* [Downlad and Install Python3.12](https://www.python.org/downloads/release/python-3128/)  
  (Make sure you install pip as well)
* (Optional but recommended) Set up an activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html):
    * For Ubuntu, first install venv using `sudo apt update && sudo apg-get install python3-venv`  
      Windows will already have it installed with Python.
    * In any terminal window, type `python3 -m pip install venv`
    * In the root directory of the repository (the same directory where this README.md file was found), type: `python3 -m venv .venv`
    * Activate the virtual evironment using:
      * Linux/Mac: `. .venv/bin/activate`
      * Windows: Either `.venv/Scripts/activate.ps1` in PowerShell or `.venv/Scripts/activate.bat` in CMD.

* Navigate to the root of the repository and type:  
  `pip install -r requirements.txt`
* Start the bot using `python CosmoGolem/cqxbot.py`

## The Settings File
You will have to edit the settings file in the `data` folder before you can actually use the bot.  

You must fill in at least the following:
```json
{
    "bot_token": "BOT_TOKEN",
    "server_id": 1234567890,
    "mod_role_id": 1234567890,
    "owners": [ 9876543210 ]
}
```

* **bot_token**: `string` - Your Bot Token (found at the [Discord Developers' dashboard](https://discord.com/developers/applications))
* **server_id**: `int` - To obtain, with **Developer Mode** active (Settings -> Advanced), right-click the server and select **Copy ID**.  
  > This doesn't determined where the bot is connected to (that is determined by the bot-token), but rather teaches the bot what server it's in.  
There's probably a better way to do this, but for now we do it manually.
* **mod_role_id**: `int` - To obtain, with **Developer Mode** active (Settings -> Advanced), go to **Server Settings** -> **Roles**, click the `...` button nex to the relevant role, and **Copy ID**.
* **owners**: `list<int>` - List of user IDs for users considered `owners` (basically bot admins).

### Optional Settings
You can set the trustworthiness of various sites under the `trustwothiness` key.  
Each entry should look like this:
```jsonc
<pattern>: {
  "trust": double, //Trust level between 0 and 1.
  "aliases": List[string], //An optional list of other strings to use as patterns for this rule.
  "message": string, //The message to display when the pattern is detected in a URL.
}
```
The trust levels are:
* `< 0.5`: Untrustworthy
* `< 0.75`: Questionable
* `>= 0.75`: Trustworthy

For example:
```json
"arxiv.org": {
    "trust": 0.7,
    "message": "arxiv.org might contain pre-published articles which may not have been propertly peer reviewed."
}
```

> 💡 In a future version this will be managed by commands rather than manual editing.

## The Data Folder
The bot uses a folder called `data` to both store its logs to and read settings form.  
By default, this is the folder `data` in the repository, which contains an empty settings file and will also be mounted by `docker-compose` as a volume so that its data will persist if you use docker locally.

If you want to use a differnet folder, simply set that path in the `CQXBOT_DATAPATH` environment variable.
