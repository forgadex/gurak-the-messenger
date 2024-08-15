import sqlite3
from datetime import datetime

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

def add_subscription(user_id, expiry_date):
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
