import discord
from discord.ext import commands
from db import get_subscription, remove_subscription
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # For handling months

class VIPManager:
    """Manages VIP roles and related operations."""

    def __init__(self, bot, messaging):
        self.bot = bot
        self.messaging = messaging
        self.vip_role_name = 'VIP'

    def parse_duration(self, duration_str):
        """Parse a duration string into a timedelta or relativedelta object."""
        try:
            amount = int(duration_str[:-1])
            unit = duration_str[-1]
        except (ValueError, IndexError):
            raise ValueError("Invalid duration format. Please specify as <number><unit>, e.g., 10d, 2h.")

        if unit == 'm':
            return timedelta(minutes=amount)
        elif unit == 'h':
            return timedelta(hours=amount)
        elif unit == 'd':
            return timedelta(days=amount)
        elif unit == 'M':  # Handle months with relativedelta
            return relativedelta(months=amount)
        else:
            raise ValueError("Invalid duration unit. Use 'm' for minutes, 'h' for hours, 'd' for days, or 'M' for months.")

    async def manage_vip_role(self, member):
        """Assigns or removes the VIP role based on subscription status."""
        vip_role = discord.utils.get(member.guild.roles, name=self.vip_role_name)
        if not vip_role:
            # Create the VIP role if it doesn't exist
            vip_role = await member.guild.create_role(name=self.vip_role_name, color=discord.Color.gold())

        expiry_date_str = get_subscription(member.id)
        if expiry_date_str:
            expiry_date = datetime.fromisoformat(expiry_date_str)
            if expiry_date > datetime.now():
                if vip_role not in member.roles:
                    await member.add_roles(vip_role)
                    await self.messaging.send_private_message(member, "You have been granted the VIP role!")
            else:
                await self.handle_expired_vip(member)
        else:
            if vip_role in member.roles:
                await member.remove_roles(vip_role)
                await self.messaging.send_private_message(member, "Your VIP subscription has expired.")

    async def handle_expired_vip(self, member):
        """Handles the expiration of a VIP subscription."""
        vip_role = discord.utils.get(member.guild.roles, name=self.vip_role_name)
        if vip_role and vip_role in member.roles:
            await member.remove_roles(vip_role)
            await self.messaging.send_private_message(member, "Your VIP subscription has expired.")
        remove_subscription(member.id)
