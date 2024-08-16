# main.py

import asyncio
from discord.ext import commands
from config import TOKEN, intents, get_prefix
from db import init_db
from messaging import Messaging
from vip_manager import VIPManager
from cogs.vip_management import VIPManagement
from cogs.event_handlers import EventHandlers
from cogs.error_handler import ErrorHandler
from cogs.tag_management import TagManagement
from help_command import MyHelpCommand
from cogs.user_status import UserStatus


class MyBot(commands.Bot):
    """Custom bot class for initializing and running the Discord bot."""

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=MyHelpCommand())
        self.messaging = Messaging(self)
        self.vip_manager = VIPManager(self, self.messaging)

    async def setup_hook(self):
        """Sets up the bot by initializing the database and loading cogs."""
        # Initialize the database (for both VIP and tags)
        init_db()
        # Load cogs
        await self.add_cog(VIPManagement(self, self.vip_manager, self.messaging))
        await self.add_cog(EventHandlers(self, self.vip_manager))
        await self.add_cog(ErrorHandler(self))
        await self.add_cog(TagManagement(self))  # Add the tag management cog
        await self.add_cog(UserStatus(self))

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

def main():
    """Main function to run the bot."""
    bot = MyBot(command_prefix=get_prefix, intents=intents)
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
