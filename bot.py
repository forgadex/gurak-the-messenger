import os
import discord
import asyncio
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # To handle month addition
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GENERAL_CHANNEL_ID = int(os.getenv('GENERAL_CHANNEL_ID'))  # Add your general channel ID in the .env file
NOTIFY_USER_ID = 410856786816663553  # User ID to notify when someone is added to VIP

# Enabling the privileged intents
intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
DATABASE = 'vip_subscriptions.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            expiry_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Decorator to retry on permission denied
def retry_on_permission_denied(retries=3, delay=5):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except discord.errors.Forbidden as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1} failed: Permission Denied. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry_on_permission_denied(retries=3, delay=5)
async def send_private_message(member, message):
    try:
        await member.send(message)
    except discord.errors.Forbidden:
        general_channel = bot.get_channel(GENERAL_CHANNEL_ID)
        if general_channel:
            await general_channel.send(f"{member.mention}, {message}")

@retry_on_permission_denied(retries=3, delay=5)
async def send_embed_message(member, embed):
    try:
        await member.send(embed=embed)
    except discord.errors.Forbidden:
        general_channel = bot.get_channel(GENERAL_CHANNEL_ID)
        if general_channel:
            await general_channel.send(f"{member.mention}", embed=embed)

@retry_on_permission_denied(retries=3, delay=5)
async def notify_user(message):
    user = await bot.fetch_user(NOTIFY_USER_ID)
    await user.send(message)

# Database functions
def add_subscription(user_id, expiry_date):
    print(f"Adding VIP subscription for user_id {user_id} until {expiry_date}.")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('REPLACE INTO subscriptions (user_id, expiry_date) VALUES (?, ?)', (user_id, expiry_date))
    conn.commit()
    conn.close()

def get_subscription(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT expiry_date FROM subscriptions WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def remove_subscription(user_id):
    print(f"Removing VIP subscription for user_id {user_id}.")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_vip_status():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT user_id, expiry_date FROM subscriptions')
    subscriptions = c.fetchall()
    conn.close()
    
    now = datetime.now()
    active_vips = []
    expired_vips = []
    
    for user_id, expiry_date_str in subscriptions:
        expiry_date = datetime.fromisoformat(expiry_date_str)
        if expiry_date > now:
            active_vips.append(user_id)
        else:
            expired_vips.append(user_id)
    
    return active_vips, expired_vips



# Ensure VIP role exists
async def ensure_vip_role_exists(guild):
    vip_role = discord.utils.get(guild.roles, name="VIP")
    if vip_role is None:
        print(f"VIP role not found in guild {guild.name}. Creating the role.")
        vip_role = await guild.create_role(name="VIP", reason="Creating VIP role for VIP subscriptions")
    return vip_role

# VIP role management
async def manage_vip_role(member):
    expiry_date_str = get_subscription(member.id)
    if not expiry_date_str:
        return

    expiry_date = datetime.fromisoformat(expiry_date_str)
    vip_role = await ensure_vip_role_exists(member.guild)

    if expiry_date > datetime.now():
        if vip_role not in member.roles:
            print(f"Granting VIP role to {member.name} ({member.id}).")
            await member.add_roles(vip_role)
            embed = discord.Embed(
                title="Welcome to the VIP Club!",
                description="You have been granted the VIP role! Enjoy your exclusive benefits and stay connected.",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Thank you for being a valued member!")
            await send_embed_message(member, embed)
    else:
        if vip_role in member.roles:
            print(f"Removing VIP role from {member.name} ({member.id}).")
            await member.remove_roles(vip_role)
            await send_private_message(member, "Your VIP subscription has expired, and the VIP role has been removed.")
        remove_subscription(member.id)

# VIP role removal
async def remove_vip_role(member):
    vip_role = discord.utils.get(member.guild.roles, name="VIP")
    if vip_role in member.roles:
        print(f"Removing VIP role from {member.name} ({member.id}).")
        await member.remove_roles(vip_role)
        await send_private_message(member, "Your VIP role has been removed.")
        remove_subscription(member.id)

# Parse duration function
def parse_duration(duration_str):
    amount = int(duration_str[:-1])
    unit = duration_str[-1]

    if unit == 'm':
        return timedelta(minutes=amount)
    elif unit == 'h':
        return timedelta(hours=amount)
    elif unit == 'd':
        return timedelta(days=amount)
    elif unit == 'M':  # Changed to 'M' to differentiate between minutes and months
        return relativedelta(months=amount)
    else:
        raise ValueError("Invalid duration unit. Use 'm' for minutes, 'h' for hours, 'd' for days, or 'M' for months.")


# Events
@bot.event
async def on_member_join(member):
    await manage_vip_role(member)

@bot.event
async def on_ready():
    print('My bot is ready')
    for guild in bot.guilds:
        for member in guild.members:
            await manage_vip_role(member)

# Command to add VIP subscription
@bot.command(name='addvip')
async def addvip(ctx, member: discord.Member, duration_str: str):
    try:
        duration = parse_duration(duration_str)
    except ValueError as e:
        await ctx.send(str(e))
        return

    expiry_date = datetime.now() + duration
    add_subscription(member.id, expiry_date.isoformat())
    await manage_vip_role(member)
    await ctx.send(f'VIP subscription added for {member.mention} for {duration_str}.')
    await notify_user(f'{member.mention} has been added to VIP for {duration_str}.')

# Command to remove VIP subscription
@bot.command(name='removevip')
async def removevip(ctx, member: discord.Member):
    await remove_vip_role(member)
    await ctx.send(f'VIP subscription removed for {member.mention}.')
    await notify_user(f'{member.mention} has been removed from VIP.')

# Command to check VIP status
@bot.command(name='checkvip')
async def checkvip(ctx, member: discord.Member):
    expiry_date_str = get_subscription(member.id)
    if expiry_date_str:
        expiry_date = datetime.fromisoformat(expiry_date_str)
        await ctx.send(f'{member.mention}\'s VIP subscription is valid until {expiry_date}.')
    else:
        await ctx.send(f'{member.mention} does not have an active VIP subscription.')


async def handle_expired_vip(member):
    vip_role = discord.utils.get(member.guild.roles, name="VIP")
    if vip_role in member.roles:
        print(f"Removing VIP role from {member.name} ({member.id}) due to expired subscription.")
        await member.remove_roles(vip_role)
        await send_private_message(member, "Your VIP subscription has expired, and the VIP role has been removed.")
        remove_subscription(member.id)



@bot.command(name='checkexpiredvip')
@commands.has_permissions(administrator=True)
async def checkexpiredvip(ctx):
    guild = ctx.guild
    active_vips, expired_vips = get_vip_status()

    for user_id in expired_vips:
        member = guild.get_member(user_id)
        if member:
            await handle_expired_vip(member)
    
    await ctx.send(f'Checked for expired VIPs and updated roles accordingly.')




# Command to get VIP status of all members
@bot.command(name='listvip')
async def listvip(ctx):
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


bot.run(TOKEN)
