import discord
from discord.ext import commands

import supersecret
import re
import os
import json

import traceback

BOT_TOKEN = supersecret.getSecret('discord_bot_archivist', 'bot_token')

NAME = "Archivist#0846"

def dictMember(member):
    return {
        "name": member.name,
        "id": member.id
    }

def dictAsset(asset):
    return {
        "size": asset.size,
        "height": asset.height,
        "width": asset.width,
        "filename": asset.filename,
        "url": asset.url,
        "proxy_url": asset.proxy_url,
        "is_spoiler": asset.is_spoiler(),
    }

async def dictReaction(r):
    users = await r.users().flatten()
    users = [dictMember(user) for user in users]
    return {
        "emoji": str(r.emoji),
        "count": r.count,
        "users": users,
        "is_custom": r.custom_emoji,
    }

async def save_channel(channel):
    result = []
    async for message in channel.history(limit=20):
        result.append({
            "message": message.content,
            "author": dictMember(message.author),
            "created_at": str(message.created_at),
            "edited_at": str(message.edited_at),
            "embeds": [embed.to_dict() for embed in message.embeds],
            "attachments": [dictAsset(asset) for asset in message.attachments],
            "reactions": [await dictReaction(reaction) for reaction in message.reactions],
        })
    return result

class Archivist(discord.Client):
    def __init__(self, categories, outputdir, delete):
        discord.Client.__init__(self)
        self.categories = categories
        self.outputdir = outputdir
        self.delete = delete

    async def archive_category(self, archive_category):
        filepath="{}/{}".format(self.outputdir, archive_category)
        outputfile = open(filepath, "w")
        result = {}
        for guild in self.guilds:
            for category in guild.categories:
                if category.name.lower() == archive_category:
                    result = {"name": archive_category}
                    chans = []
                    for channel in category.text_channels:
                        messages = await save_channel(channel)
                        chans.append({"name": channel.name, "messages": messages})
                    result["channels"] = chans
                    break
        outputfile.write(json.dumps(result))
        if self.delete:
            for guild in self.guilds:
                for category in guild.categories:
                    if category.name.lower() == archive_category:
                        print("Deleting:{}".format(category.name.lower()))
                        for channel in category.text_channels:
                            print(" Deleting:{}".format(channel.name))
                            await channel.delete(reason="Deleted by archivist")
                        await category.delete(reason="Deleted by archivist")

    async def on_ready(self):
        try:
            for category in self.categories:
                await self.archive_category(category)
        except Exception as e:
            traceback.print_exc()
        finally:
            await self.close() # Code past this point never gets called.

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("categories", nargs="+")
    parser.add_argument("--outputdir")
    parser.add_argument("--delete", action="store_true")
    options = parser.parse_args()
    for category in options.categories:
        filepath="{}/{}".format(options.outputdir, category)
        if os.path.exists(filepath):
            print(f"Refusing to overwrite file {filepath}")
            import sys
            sys.exit(1)
    client = Archivist(options.categories, options.outputdir, options.delete)
    client.run(BOT_TOKEN)

main()
