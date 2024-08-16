# cogs/user_status.py

import discord
from discord.ext import commands, tasks
import logging
from db import store_user_presence, get_user_total_presence  # Ensure this is imported correctly
from datetime import timedelta

# Set up logging for status changes
logging.basicConfig(filename='user_status.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class UserStatus(commands.Cog):
    """Cog to monitor and track user presence time for role promotion."""

    def __init__(self, bot):
        self.bot = bot
        self.user_presence_times = {}  # Track when users go online
        self.check_role_promotion.start()  # Start the background task for promotions

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Tracks user status changes and calculates presence time."""
        before_status = before.status
        after_status = after.status

        logging.info(f"User {after.name} ({after.id}) presence change: {before_status} -> {after_status}")
        
        # Log when a user comes online or goes offline
        if before_status != after_status:
            if after_status in (discord.Status.online, discord.Status.idle, discord.Status.dnd):
                self.user_presence_times[after.id] = discord.utils.utcnow()  # Store when they went online
                logging.info(f"User {after.name} ({after.id}) went online at {self.user_presence_times[after.id]}")
            elif after_status == discord.Status.offline and after.id in self.user_presence_times:
                # Calculate presence duration
                start_time = self.user_presence_times.pop(after.id, None)
                if start_time:
                    presence_duration = (discord.utils.utcnow() - start_time).total_seconds()
                    await store_user_presence(after.id, presence_duration)
                    logging.info(f"User {after.name} ({after.id}) was online for {presence_duration} seconds.")
                else:
                    logging.warning(f"User {after.name} ({after.id}) went offline, but no start time found.")


    @tasks.loop(hours=24)
    async def check_role_promotion(self):
        """Background task to check for role promotions every 24 hours."""
        for guild in self.bot.guilds:
            for member in guild.members:
                total_presence_time = get_user_total_presence(member.id)  # Remove `await` here
                membership_duration = (discord.utils.utcnow() - member.joined_at).total_seconds()

                # Example thresholds for promotions
                if membership_duration > 30 * 24 * 3600 and total_presence_time > 100 * 3600:  # 30 days, 100 hours online
                    new_role = discord.utils.get(guild.roles, name="Veteran")
                    if new_role and new_role not in member.roles:
                        await member.add_roles(new_role)
                        logging.info(f"User {member.name} ({member.id}) promoted to Veteran role.")
                elif membership_duration > 60 * 24 * 3600 and total_presence_time > 200 * 3600:  # 60 days, 200 hours online
                    new_role = discord.utils.get(guild.roles, name="Elite")
                    if new_role and new_role not in member.roles:
                        await member.add_roles(new_role)
                        logging.info(f"User {member.name} ({member.id}) promoted to Elite role.")

    @commands.command(name='user_level', help="Check the user's current level and promotion progress.")
    async def user_level(self, ctx, member: discord.Member = None):
        """Check the current roles and promotion progress of a user."""
        if not member:
            member = ctx.author

        # Fetch the user's roles
        roles = [role.name for role in member.roles if role.name not in ("@everyone")]
        role_str = ', '.join(roles) if roles else "No special roles assigned."

        # Fetch the user's total active time and membership duration
        total_presence_time = get_user_total_presence(member.id)  # Remove `await` here
        membership_duration = (discord.utils.utcnow() - member.joined_at).total_seconds()

        # Calculate remaining time for the next promotion
        next_promotion_hours = 100 * 3600 - total_presence_time  # Assuming promotion at 100 hours

        await ctx.send(f"{member.mention}'s current roles: {role_str}\n"
                       f"Active Time: {str(timedelta(seconds=total_presence_time))} (HH:MM:SS)\n"
                       f"Membership Duration: {str(timedelta(seconds=membership_duration))} (HH:MM:SS)\n"
                       f"Time until next promotion: {str(timedelta(seconds=max(0, next_promotion_hours)))} (HH:MM:SS)")

    @commands.command(name='active_time', help="Check the user's total active (online) time.")
    async def active_time(self, ctx, member: discord.Member = None):
        """Check the total time a user has been actively online."""
        if not member:
            member = ctx.author

        total_presence_time = get_user_total_presence(member.id)  # Remove `await` here

        # Format the time into hours, minutes, and seconds
        formatted_time = str(timedelta(seconds=total_presence_time))
        
        await ctx.send(f"{member.mention}'s total active time: {formatted_time} (HH:MM:SS)")
