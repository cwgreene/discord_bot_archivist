import discord
from discord.ext import commands

import supersecret
import re
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
        "emoji": r.emoji,
        "count": r.count,
        "users": users,
        "is_custom": r.custom_emoji,
    }

class Archivist(discord.Client):
    async def on_ready(self):
        try:
            print('Logged on as {0}!'.format(self.user))
            for guild in self.guilds:
                for category in guild.categories:
                    for channel in category.text_channels:
                        if channel.name == "general":
                            async for message in channel.history(limit=20):
                                print(json.dumps({
    "message": message.content,
    "author": dictMember(message.author),
    "created_at": str(message.created_at),
    "edited_at": str(message.edited_at),
    "embeds": [embed.to_dict() for embed in message.embeds],
    "attachments": [dictAsset(asset) for asset in message.attachments],
    "reactions": [await dictReaction(reaction) for reaction in message.reactions],
                                }))
        except Exception as e:
            traceback.print_exc()
        finally:
            await self.close() # Code past this point never gets called.

client = Archivist()
client.run(BOT_TOKEN)
