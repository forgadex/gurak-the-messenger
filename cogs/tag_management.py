# cogs/tag_management.py

import discord
from discord.ext import commands
import logging
from db import add_tag_to_user, remove_tag_from_user, get_user_tags, get_all_tags, get_tag_roles, set_tag_roles

# Set up logging for permission checks
logging.basicConfig(filename='tag_permissions.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

class TagManagement(commands.Cog, name="Tag Management"):
    """Cog to manage tag assignment, removal, and listing."""

    def __init__(self, bot):
        self.bot = bot

    def validate_tag(self, tag):
        """Validate the tag based on length, characters, and uniqueness."""
        if len(tag) < 1 or len(tag) > 20:
            return False, "Tags must be between 1 and 20 characters long."
        if not tag.isalnum():
            return False, "Tags must contain only alphanumeric characters."
        return True, None

    def check_user_roles(self, member, tag):
        """Check if the user has the required role to assign or modify the tag."""
        required_roles = get_tag_roles(tag)
        member_roles = [role.name for role in member.roles]
        for role in required_roles:
            if role in member_roles:
                return True
        return False

    @commands.command(name='assign_tag', help="Assign a tag to a user. Example: !assign_tag @user tagname")
    async def assign_tag(self, ctx, member: discord.Member, tag: str):
        """Assign a tag to a user, ensuring it's valid and authorized."""
        logging.info(f"User {ctx.author} ({ctx.author.id}) attempted to assign tag {tag} to {member.name} ({member.id})")

        # Validate the tag
        valid, message = self.validate_tag(tag)
        if not valid:
            await ctx.send(message)
            return

        # Check if the author is allowed to assign this tag
        if not self.check_user_roles(ctx.author, tag):
            await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission to assign the tag '{tag}'.")
            logging.warning(f"Unauthorized tag assignment attempt by {ctx.author.name} ({ctx.author.id}) for tag '{tag}'")
            return

        # Add tag to user
        if add_tag_to_user(member.id, tag):
            await ctx.send(f"Successfully assigned tag '{tag}' to {member.mention}.")
            logging.info(f"Tag '{tag}' assigned to {member.name} ({member.id}) by {ctx.author.name} ({ctx.author.id})")
        else:
            await ctx.send(f"Failed to assign tag '{tag}' to {member.mention}. Tag may already be assigned.")
            logging.warning(f"Failed to assign tag '{tag}' by {ctx.author.name} ({ctx.author.id})")

    @commands.command(name='remove_tag', help="Remove a tag from a user. Example: !remove_tag @user tagname")
    async def remove_tag(self, ctx, member: discord.Member, tag: str):
        """Remove a tag from a user, ensuring the author is authorized."""
        logging.info(f"User {ctx.author} ({ctx.author.id}) attempted to remove tag {tag} from {member.name} ({member.id})")

        # Check if the author is allowed to remove this tag
        if not self.check_user_roles(ctx.author, tag):
            await ctx.send(f"Sorry {ctx.author.mention}, you don't have permission to remove the tag '{tag}'.")
            logging.warning(f"Unauthorized tag removal attempt by {ctx.author.name} ({ctx.author.id}) for tag '{tag}'")
            return

        # Remove the tag
        if remove_tag_from_user(member.id, tag):
            await ctx.send(f"Successfully removed tag '{tag}' from {member.mention}.")
            logging.info(f"Tag '{tag}' removed from {member.name} ({member.id}) by {ctx.author.name} ({ctx.author.id})")
        else:
            await ctx.send(f"Tag '{tag}' not found for {member.mention}.")
            logging.warning(f"Tag '{tag}' not found for {member.name} ({member.id}) when {ctx.author.name} ({ctx.author.id}) tried to remove it.")

    @commands.command(name='set_tag_rule', help="Set roles allowed to manage a tag. Example: !set_tag_rule tagname Admin Moderator")
    @commands.has_permissions(administrator=True)
    async def set_tag_rule(self, ctx, tag: str, *roles):
        """Set which roles are allowed to manage a specific tag."""
        set_tag_roles(tag, roles)
        await ctx.send(f"Roles allowed to manage the tag '{tag}': {', '.join(roles)}")
        logging.info(f"Admin {ctx.author} updated roles for tag '{tag}' to: {', '.join(roles)}")

    @commands.command(name='list_tags', help="List all available tags.")
    async def list_tags(self, ctx):
        """List all available tags."""
        tags = get_all_tags()
        if tags:
            await ctx.send(f"Available tags: {', '.join(tags)}")
        else:
            await ctx.send("No tags available.")

    @commands.command(name='user_tags', help="List tags assigned to a user. Example: !user_tags @user")
    async def user_tags(self, ctx, member: discord.Member):
        """List tags assigned to a specific user."""
        tags = get_user_tags(member.id)
        if tags:
            await ctx.send(f"{member.mention} has the following tags: {', '.join(tags)}")
        else:
            await ctx.send(f"{member.mention} has no tags assigned.")
