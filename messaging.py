# messaging.py

import discord
import asyncio
from config import GENERAL_CHANNEL_ID

class Messaging:
    """Handles messaging functionalities for the bot."""

    def __init__(self, bot):
        self.bot = bot

    def retry_on_permission_denied(retries=3, delay=5):
        """Decorator to retry a function upon encountering a Permission Denied error."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(retries):
                    try:
                        return await func(*args, **kwargs)
                    except discord.errors.Forbidden as e:
                        last_exception = e
                        print(f"Attempt {attempt + 1} failed: Permission Denied. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                raise last_exception
            return wrapper
        return decorator

    @retry_on_permission_denied(retries=3, delay=5)
    async def send_private_message(self, member, message):
        """Sends a private message to a member."""
        try:
            await member.send(message)
        except discord.errors.Forbidden:
            general_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
            if general_channel:
                await general_channel.send(f"{member.mention}, {message}")

    @retry_on_permission_denied(retries=3, delay=5)
    async def send_embed_message(self, member, embed):
        """Sends an embedded message to a member."""
        try:
            await member.send(embed=embed)
        except discord.errors.Forbidden:
            general_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
            if general_channel:
                await general_channel.send(f"{member.mention}", embed=embed)

    async def notify_admin(self, guild, message):
        """Notifies the guild administrator with a message."""
        admin = guild.owner  # Retrieves the guild owner
        if admin:
            try:
                await admin.send(message)
            except discord.errors.Forbidden:
                # Fallback to sending the message in the general channel if DM is not possible
                general_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
                if general_channel:
                    await general_channel.send(f"{admin.mention}, {message}")
