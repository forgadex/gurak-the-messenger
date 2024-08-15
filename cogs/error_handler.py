# cogs/error_handler.py

import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    """Cog for handling command errors globally."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handles errors raised during command execution and provides user feedback."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument. Please check your command and try again.')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send('Command not found. Please check the available commands and try again.')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the required permissions to execute this command.')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('Member not found. Please ensure the member is in the server and try again.')
        else:
            await ctx.send('An unexpected error occurred. Please contact the administrator.')
            # Optionally log the error details for debugging
            print(f'Unhandled error: {error}')
