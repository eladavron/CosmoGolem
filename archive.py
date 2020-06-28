""" Methods related to the Archive command """

import os
import json
import tempfile
import logging
import discord

log = logging.getLogger('Archive')

def parse_message(msg: discord.Message):
    message_metadata = {
        'channel': str(msg.channel),
        'author': msg.author.display_name,
        'content': msg.content,
        }
    if msg.embeds:
        message_metadata['embeds'] = [e.to_dict() for e in msg.embeds]

    if msg.attachments:
        message_metadata['attachments'] = []
        for at in msg.attachments:
            message_metadata['attachments'].append(at.url)
            # await at.save(f"{at.id}_{at.filename}")

    message_metadata['meta'] = {
        'id': msg.id,
        'timestamp': msg.created_at.isoformat(),
        'authordata': (msg.author.id, str(msg.author), msg.author.display_name),
        'channel_id': msg.channel.id
    }

    return message_metadata

async def archive(channel_to_archive: discord.TextChannel, where_to_upload: discord.TextChannel):
    full_log = []
    async for message in channel_to_archive.history(limit=None, oldest_first=True):
        full_log.append(parse_message(message))

    temp_file = os.path.join(tempfile.gettempdir(), channel_to_archive.name + ".json")
    with open(temp_file, 'w') as f:
        f.write(json.dumps(full_log, indent=4))

    await where_to_upload.send(f"#{channel_to_archive.name} has been archived!", file=discord.File(temp_file))
