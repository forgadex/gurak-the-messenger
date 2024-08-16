# cogs/vip_management.py

import discord
from discord.ext import commands
from datetime import datetime
import logging
from db import add_subscription, remove_subscription, get_subscription, get_vip_status

# Set up logging for permission checks and actions
logging.basicConfig(filename='bot_permissions.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class VIPManagement(commands.Cog, name="VIP Management"):
    """Cog for managing VIP subscriptions."""

    def __init__(self, bot, vip_manager, messaging):
        self.bot = bot
        self.vip_manager = vip_manager
        self.messaging = messaging

    @commands.command(name='addvip', help='Add a VIP subscription to a member for a specified duration.')
    @commands.has_permissions(administrator=True)  # Require administrator permission
    async def add_vip(self, ctx, member: discord.Member, duration_str: str):
        """Adds a VIP subscription to a member."""
        logging.info(f"Admin {ctx.author} ({ctx.author.id}) attempted to add VIP to {member.name} ({member.id})")
        
        # Validate the duration and add the subscription
        try:
            duration = self.vip_manager.parse_duration(duration_str)
            expiry_date = datetime.now() + duration
            add_subscription(member.id, expiry_date.isoformat())
            await self.vip_manager.manage_vip_role(member)
            await ctx.send(f'VIP subscription added for {member.mention} for {duration_str}.')
            await self.messaging.notify_admin(ctx.guild, f'{member.mention} has been added to VIP for {duration_str}.')
            logging.info(f"VIP subscription added for {member.name} ({member.id}) by {ctx.author.name} ({ctx.author.id})")
        except ValueError as e:
            await ctx.send(str(e))
            logging.warning(f"Failed VIP addition by {ctx.author.name} ({ctx.author.id}): {str(e)}")

    @add_vip.error
    async def add_vip_error(self, ctx, error):
        """Handle permission error for the add_vip command."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission to add VIP roles.")
            logging.warning(f"Permission denied for {ctx.author.name} ({ctx.author.id}) to add VIP roles.")

    @commands.command(name='removevip', help='Remove a VIP subscription from a member.')
    @commands.has_permissions(administrator=True)  # Require administrator permission
    async def remove_vip(self, ctx, member: discord.Member):
        """Removes a VIP subscription from a member."""
        logging.info(f"Admin {ctx.author} ({ctx.author.id}) attempted to remove VIP from {member.name} ({member.id})")
        
        await self.vip_manager.remove_vip_role(member)
        await ctx.send(f'VIP subscription removed for {member.mention}.')
        await self.messaging.notify_admin(ctx.guild, f'{member.mention} has been removed from VIP.')
        logging.info(f"VIP subscription removed for {member.name} ({member.id}) by {ctx.author.name} ({ctx.author.id})")

    @remove_vip.error
    async def remove_vip_error(self, ctx, error):
        """Handle permission error for the remove_vip command."""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission to remove VIP roles.")
            logging.warning(f"Permission denied for {ctx.author.name} ({ctx.author.id}) to remove VIP roles.")

    @commands.command(name='listvip', help='List all active and expired VIP subscriptions.')
    async def list_vip(self, ctx):
        """Lists all VIP subscriptions."""
        logging.info(f"User {ctx.author} ({ctx.author.id}) requested VIP list.")
        
        active_vips, expired_vips = get_vip_status()
        active_vip_list = []
        expired_vip_list = []

        for user_id in active_vips:
            expiry_date = datetime.fromisoformat(get_subscription(user_id))
            active_vip_list.append(f'<@{user_id}> - Expires on {expiry_date.strftime("%Y-%m-%d %H:%M:%S")}')

        for user_id in expired_vips:
            expiry_date = datetime.fromisoformat(get_subscription(user_id))
            expired_vip_list.append(f'<@{user_id}> - Expired on {expiry_date.strftime("%Y-%m-%d %H:%M:%S")}')

        active_vip_list_str = '\n'.join(active_vip_list) if active_vip_list else "None"
        expired_vip_list_str = '\n'.join(expired_vip_list) if expired_vip_list else "None"

        embed = discord.Embed(title="VIP List", color=discord.Color.gold())
        embed.add_field(name="Active VIPs", value=active_vip_list_str, inline=False)
        embed.add_field(name="Expired VIPs", value=expired_vip_list_str, inline=False)

        await ctx.send(embed=embed)
