# config.py

import os
import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Token and other configurations
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GENERAL_CHANNEL_ID = os.getenv('GENERAL_CHANNEL_ID')

# Ensure these variables are set
if not TOKEN:
    raise ValueError("DISCORD_TOKEN is not set in the environment variables.")
if not GUILD:
    raise ValueError("GUILD is not set in the environment variables.")
if not GENERAL_CHANNEL_ID:
    raise ValueError("GENERAL_CHANNEL_ID is not set in the environment variables.")

# Convert GENERAL_CHANNEL_ID to an integer
GENERAL_CHANNEL_ID = int(GENERAL_CHANNEL_ID)

# Setup intents
intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  # Ensure the message content intent is enabled

# Function to get the bot's prefix (now accepts bot and message parameters)
def get_prefix(bot, message):
    return '!'
