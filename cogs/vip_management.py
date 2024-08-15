# cogs/vip_management.py

import discord
from discord.ext import commands
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from db import add_subscription, get_vip_status, get_subscription

class VIPManagement(commands.Cog):
    """Cog for managing VIP subscriptions."""

    def __init__(self, bot, vip_manager, messaging):
        self.bot = bot
        self.vip_manager = vip_manager
        self.messaging = messaging

    @staticmethod
    def parse_duration(duration_str):
        """Parses duration strings into timedelta or relativedelta objects."""
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
        elif unit == 'M':
            return relativedelta(months=amount)
        else:
            raise ValueError("Invalid duration unit. Use 'm' for minutes, 'h' for hours, 'd' for days, or 'M' for months.")

    @commands.command(name='addvip', help='Add a VIP subscription to a member for a specified duration (e.g., 10d, 2h).')
    async def add_vip(self, ctx, member: discord.Member, duration_str: str):
        """Adds a VIP subscription to a member."""
        try:
            duration = self.parse_duration(duration_str)
        except ValueError as e:
            await ctx.send(str(e))
            return

        expiry_date = datetime.now() + duration
        add_subscription(member.id, expiry_date.isoformat())
        await self.vip_manager.manage_vip_role(member)
        await ctx.send(f'VIP subscription added for {member.mention} for {duration_str}.')
        await self.messaging.notify_admin(ctx.guild, f'{member.mention} has been added to VIP for {duration_str}.')

    @commands.command(name='removevip', help='Remove a VIP subscription from a member.')
    async def remove_vip(self, ctx, member: discord.Member):
        """Removes a VIP subscription from a member."""
        await self.vip_manager.remove_vip_role(member)
        await ctx.send(f'VIP subscription removed for {member.mention}.')
        await self.messaging.notify_admin(ctx.guild, f'{member.mention} has been removed from VIP.')

    @commands.command(name='checkvip', help='Check the VIP status of a member.')
    async def check_vip(self, ctx, member: discord.Member):
        """Checks the VIP status of a member."""
        expiry_date_str = get_subscription(member.id)
        if expiry_date_str:
            expiry_date = datetime.fromisoformat(expiry_date_str)
            await ctx.send(f'{member.mention}\'s VIP subscription is valid until {expiry_date}.')
        else:
            await ctx.send(f'{member.mention} does not have an active VIP subscription.')

    @commands.command(name='checkexpiredvip', help='Check and update expired VIP subscriptions.')
    @commands.has_permissions(administrator=True)
    async def check_expired_vip(self, ctx):
        """Checks for expired VIP subscriptions and updates roles accordingly."""
        guild = ctx.guild
        active_vips, expired_vips = get_vip_status()

        for user_id in expired_vips:
            member = guild.get_member(user_id)
            if member:
                await self.vip_manager.handle_expired_vip(member)
        
        await ctx.send('Checked for expired VIPs and updated roles accordingly.')

    @commands.command(name='listvip', help='List all VIP subscriptions.')
    async def list_vip(self, ctx):
        """Lists all VIP subscriptions."""
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
