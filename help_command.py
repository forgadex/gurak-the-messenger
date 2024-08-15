# help_command.py

from discord.ext import commands
import discord

class MyHelpCommand(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        """Custom help command for all commands."""
        ctx = self.context
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        embed.description = "Here is a list of all available commands:"

        for cog, commands in mapping.items():
            command_list = [command.name for command in commands if not command.hidden]
            if command_list:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value=", ".join(command_list), inline=False)

        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        """Custom help command for a specific cog."""
        ctx = self.context
        embed = discord.Embed(title=f"{cog.qualified_name} Commands", color=discord.Color.green())
        embed.description = cog.description

        for command in cog.get_commands():
            if not command.hidden:
                embed.add_field(name=command.name, value=command.help or "No description provided", inline=False)

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        """Custom help command for a specific command."""
        ctx = self.context
        embed = discord.Embed(title=command.name, color=discord.Color.purple())
        embed.add_field(name="Description", value=command.help or "No description provided", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        await ctx.send(embed=embed)

    async def send_group_help(self, group):
        """Custom help command for a group of commands."""
        ctx = self.context
        embed = discord.Embed(title=group.name, color=discord.Color.orange())
        embed.description = group.help or "No description provided"

        for command in group.commands:
            if not command.hidden:
                embed.add_field(name=command.name, value=command.help or "No description provided", inline=False)

        await ctx.send(embed=embed)
