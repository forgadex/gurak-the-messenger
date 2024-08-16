# help_command.py

from discord.ext import commands
import discord

class MyHelpCommand(commands.MinimalHelpCommand):
    """Custom help command class that lists all commands with respect to permissions and groups by category."""

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        """Sends help for all commands the user has permission to access, grouped by category."""
        ctx = self.context
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        embed.description = "Here is a list of all available commands:"

        for cog, commands in mapping.items():
            # Filter commands based on the user's permissions
            filtered_commands = await self.filter_commands(commands, sort=True)
            command_list = [command.name for command in filtered_commands if not command.hidden]
            
            if command_list:
                cog_name = cog.qualified_name if cog else "General"
                embed.add_field(name=cog_name, value=", ".join(command_list), inline=False)

        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        """Sends help for all commands in a specific Cog (category)."""
        ctx = self.context
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=discord.Color.green())
        embed.description = cog.description

        filtered_commands = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered_commands:
            if not command.hidden:
                embed.add_field(name=command.name, value=command.help or "No description provided", inline=False)

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        """Sends help for a specific command."""
        ctx = self.context
        embed = discord.Embed(title=command.name, color=discord.Color.purple())
        embed.add_field(name="Description", value=command.help or "No description provided", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        await ctx.send(embed=embed)

    async def send_group_help(self, group):
        """Sends help for a group of commands."""
        ctx = self.context
        embed = discord.Embed(title=group.name, color=discord.Color.orange())
        embed.description = group.help or "No description provided"

        filtered_commands = await self.filter_commands(group.commands, sort=True)
        for command in filtered_commands:
            if not command.hidden:
                embed.add_field(name=command.name, value=command.help or "No description provided", inline=False)

        await ctx.send(embed=embed)
