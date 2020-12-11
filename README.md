# CosmoQuestX Bot
A bot for the CosmoQuestX Discord Server.  
***Both the bot and this readme file are still under construciton!***

## Running the Bot
You will need one of these two to get started:
* Docker
* Python3.9 with `pip`

### Docker
The `Dockerfile` can be built like a regular docker file, using `docker build .`
Howerver it is highly recommended to
use `docker-compose`:
* [Download and Install Docker](https://www.docker.com/get-started)
* Install `docker-compose` using `pip install docker-compose`
* Build and start the bot using `docker-compose up`

### Python3.9
* [Downlad and Install Python3.9](https://www.python.org/downloads/release/python-390/)  
  (Make sure you install pip as well)
* Once installed, navigate to the root of the repository and type:  
  `pip install -r requirements.txt`
* Start the bot using `python CQXBot/cqxbot.py`

### The Settings File
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
* **server_id**: `int` - Found in the server's settings under `Widget`.  
This doesn't determined where the bot is connected to (that is determined by the bot-token), but rather teaches the bot what server it's in.  
There's probably a better way to do this, but for now we do it manually.
* **mod_role_id**: `int` - Found by typing `\@role_name` in Discord
* **owners**: `list<int>` - List of user IDs for users considered `owners` (basically bot admins).

### The Data Folder
The bot uses a folder called `data` to both store its logs to and read settings form.  
By default, this is the folder `data` in the repository, which contains an empty settings file and will also be mounted by `docker-compose` as a volume so that its data will persist if you use docker locally.

If you want to use a differnet folder, simply set that path in the `CQXBOT_DATAPATH` environment variable.  

## Developing
It's not recommended to develop IN Docker, instead - use a regular good 'ol localized installation of Python3.9.  
Note that starting the bot will cause it to conenct to whatever it was invited to, so maybe keep a spare debug-only bot-token and use that for development.