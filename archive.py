""" Methods related to the Archive command """

import os
import json
import tempfile
from zipfile import ZipFile
import logging
import discord

log = logging.getLogger('Archive')

def parse_message(msg: discord.Message):
    """Parses a single discord message into a dictionary.

    Args:
        msg (discord.Message): A discord message to parse.

    Returns:
        dict: The message and its metadata
    """
    message_metadata = {
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
    }

    return message_metadata


def parse_channel_role_overrides(which_channel: discord.TextChannel):
    dic = {}
    for role in which_channel.changed_roles:
        dic[role.name] = {x[0]: x[1] for x in list(filter(lambda f: f[1] is not None, which_channel.overwrites[role]))}
    return dic


async def archive(channel_to_archive: discord.TextChannel, where_to_upload: discord.TextChannel = None, files_to_archive=None):
    """Archive a single channel into a file

    Args:
        channel_to_archive (discord.TextChannel): The channel to archive
        where_to_upload (discord.TextChannel): Where to upload the archive to
    """
    metadata = {
        "channel_name": channel_to_archive.name,
        "channel_id": channel_to_archive.id,
        "is_channel_nsfw": channel_to_archive.is_nsfw(),
        "category": channel_to_archive.category.name if channel_to_archive.category else None,
        "role_overwrites": parse_channel_role_overrides(channel_to_archive)
    }
    full_log = []
    async for message in channel_to_archive.history(limit=None, oldest_first=True):
        full_log.append(parse_message(message))

    metadata["message_log"] = full_log

    temp_file = os.path.join(tempfile.gettempdir(), channel_to_archive.name + ".json")
    with open(temp_file, 'w') as f:
        f.write(json.dumps(metadata, indent=4))

    if where_to_upload:
        await where_to_upload.send(file=discord.File(temp_file))

    if files_to_archive is not None:
        files_to_archive.append(temp_file)


async def archive_server(where_to_upload: discord.TextChannel):
    guild = where_to_upload.guild
    files_to_archive = []
    for channel in guild.text_channels:
        await archive(channel, None, files_to_archive)

    zip_file_path = os.path.join(tempfile.gettempdir(), guild.name + ".zip")
    with ZipFile(zip_file_path, "w") as zip_file:
        for file_to_archive in files_to_archive:
            log.info("Adding %s", file_to_archive)
            zip_file.write(file_to_archive, arcname=os.path.basename(file_to_archive))

    await where_to_upload.send(file=discord.File(zip_file_path))

