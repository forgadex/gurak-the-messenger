# cogs/event_handlers.py

import discord
from discord.ext import commands

class EventHandlers(commands.Cog):
    """Cog for handling bot events."""

    def __init__(self, bot, vip_manager):
        self.bot = bot
        self.vip_manager = vip_manager

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handles the event when a new member joins and assigns roles if needed."""
        await self.vip_manager.manage_vip_role(member)

    @commands.Cog.listener()
    async def on_ready(self):
        """Handles the event when the bot is ready and initializes roles."""
        print('Bot is online and ready!')
        for guild in self.bot.guilds:
            for member in guild.members:
                await self.vip_manager.manage_vip_role(member)
