import sqlite3
from datetime import datetime

DATABASE = 'bot_data.db'

def init_db():
    """Initialize the database with both VIP and tag tables."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create VIP Subscriptions Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            expiry_date TEXT
        )
    ''')

    # Create User Tags Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_tags (
            user_id INTEGER,
            tag TEXT,
            UNIQUE(user_id, tag)
        )
    ''')

    # Create Role-Based Rules Table for Tags
    c.execute('''
        CREATE TABLE IF NOT EXISTS tag_role_rules (
            tag TEXT PRIMARY KEY,
            roles TEXT  -- A comma-separated string of roles allowed to manage the tag
        )
    ''')

    # Create User Presence Table to track total online time
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_presence (
            user_id INTEGER PRIMARY KEY,
            total_presence REAL  -- Total online presence in seconds
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------------
# VIP Subscription Functions
# -------------------------------

def add_subscription(user_id, expiry_date):
    """Adds or updates a VIP subscription for a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('REPLACE INTO subscriptions (user_id, expiry_date) VALUES (?, ?)', (user_id, expiry_date))
    conn.commit()
    conn.close()

def get_subscription(user_id):
    """Gets the VIP subscription for a specific user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT expiry_date FROM subscriptions WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def remove_subscription(user_id):
    """Removes a VIP subscription for a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_vip_status():
    """Gets the VIP status (active and expired VIPs)."""
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

# -------------------------------
# Tag Management Functions
# -------------------------------

def add_tag_to_user(user_id, tag):
    """Adds a tag to a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO user_tags (user_id, tag) VALUES (?, ?)', (user_id, tag))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def remove_tag_from_user(user_id, tag):
    """Removes a tag from a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM user_tags WHERE user_id = ? AND tag = ?', (user_id, tag))
    conn.commit()
    deleted_rows = c.rowcount
    conn.close()
    return deleted_rows > 0

def get_user_tags(user_id):
    """Gets all tags for a specific user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT tag FROM user_tags WHERE user_id = ?', (user_id,))
    tags = [row[0] for row in c.fetchall()]
    conn.close()
    return tags

def get_all_tags():
    """Gets all unique tags."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT DISTINCT tag FROM user_tags')
    tags = [row[0] for row in c.fetchall()]
    conn.close()
    return tags

# -------------------------------
# Role-Based Tag Rules Functions
# -------------------------------

def get_tag_roles(tag):
    """Get roles allowed to manage a specific tag."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT roles FROM tag_role_rules WHERE tag = ?', (tag,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0].split(',')  # Split the roles by comma
    else:
        return ["Survivor"]  # Default role is 'Survivor'

def set_tag_roles(tag, roles):
    """Set roles allowed to manage a specific tag."""
    roles_str = ','.join(roles)  # Store roles as a comma-separated string
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('REPLACE INTO tag_role_rules (tag, roles) VALUES (?, ?)', (tag, roles_str))
    conn.commit()
    conn.close()

def get_all_tag_role_rules():
    """Get all tag-role rules."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT tag, roles FROM tag_role_rules')
    rules = {row[0]: row[1].split(',') for row in c.fetchall()}  # Convert comma-separated roles to list
    conn.close()
    return rules


# -------------------------------
# User Presence Functions
# -------------------------------
def store_user_presence(user_id, presence_duration):
    """Stores the total online presence of a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Check if the user already has some recorded presence
    c.execute('SELECT total_presence FROM user_presence WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        total_presence = result[0] + presence_duration
        c.execute('UPDATE user_presence SET total_presence = ? WHERE user_id = ?', (total_presence, user_id))
    else:
        total_presence = presence_duration
        c.execute('INSERT INTO user_presence (user_id, total_presence) VALUES (?, ?)', (user_id, total_presence))

    conn.commit()
    conn.close()

def get_user_total_presence(user_id):
    """Get the total online presence of a user."""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT total_presence FROM user_presence WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0
