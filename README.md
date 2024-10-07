# Gurak the Messenger Bot

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Commands](#commands)
- [Database Structure](#database-structure)
- [Error Handling and Logs](#error-handling-and-logs)
- [License](#license)
- [Contributing](#contributing)

## Introduction

**Gurak the Messenger Bot** is a custom Discord bot designed to manage VIP subscriptions, user presence tracking, tag management, and provides a custom help command. It is structured with a modular architecture, using multiple cogs for various features, making it extensible and easy to maintain.

## Features

- **VIP Management**: Adds, removes, and lists VIP subscriptions, allowing administrators to manage VIP statuses with automated role assignments.
- **Presence Tracking**: Tracks user online presence for role promotion based on activity.
- **Tag Management**: Allows users with the appropriate permissions to assign tags to others, useful for organizing users by roles or other criteria.
- **Custom Help Command**: Provides a comprehensive help command that groups available commands by category.
- **Error Handling and Logging**: Logs errors and activities, with retries for certain actions if permissions are denied.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/forgadex/gurak-the-messenger.git
   cd gurak-the-messenger
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Initialization**:
   Ensure the SQLite database (`bot_data.db`) is initialized with the necessary tables:
   ```python
   from db import init_db
   init_db()
   ```

4. **Run the Bot**:
   Start the bot with the main script.
   ```bash
   python main.py
   ```

## Configuration

Configure environment variables by creating a `.env` file in the root directory with the following values:

```plaintext
DISCORD_TOKEN=your_discord_token
DISCORD_GUILD=your_guild_name
GENERAL_CHANNEL_ID=general_channel_id
```

### Permissions

Ensure the bot has permissions for:
- Sending and managing messages
- Managing roles
- Accessing member presence

## Commands

### VIP Management

- `!addvip @member duration`: Adds a VIP subscription with specified duration (e.g., `10d` for 10 days).
- `!removevip @member`: Removes the VIP status from a member.
- `!listvip`: Lists active and expired VIP members.

### Presence Tracking

- `!user_level @member`: Shows a user’s activity level and promotion status.
- `!active_time @member`: Shows the total online time for a user.

### Tag Management

- `!assign_tag @member tag`: Assigns a specified tag to a user if the executor has the required role.
- `!remove_tag @member tag`: Removes a specified tag from a user.
- `!list_tags`: Lists all available tags.
- `!user_tags @member`: Lists tags assigned to a specified user.

### Custom Help Command

- `!help`: Displays all available commands grouped by category.

## Database Structure

- **subscriptions**: Stores VIP subscription information (`user_id`, `expiry_date`).
- **user_tags**: Manages tags associated with users (`user_id`, `tag`).
- **tag_role_rules**: Defines roles allowed to manage specific tags (`tag`, `roles`).
- **user_presence**: Tracks the total online presence of users (`user_id`, `total_presence`).

## Error Handling and Logs

- **Logging**: Logs bot actions, errors, and permission checks.
- **Error Handler**: A cog (`ErrorHandler`) that handles errors raised during command execution and provides feedback to the user.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Make changes and commit (`git commit -m 'Add feature'`).
4. Push to your branch (`git push origin feature-name`).
5. Open a pull request.
