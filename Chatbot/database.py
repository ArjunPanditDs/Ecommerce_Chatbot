import sqlite3
import json
from datetime import datetime
import os

def init_db():
    """Initialize database and create tables"""
    try:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        
        # Create chats table
        c.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT,
                bot_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def save_chat(session_id, user_message, bot_message):
    """Save chat message to database"""
    try:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        
        print(f"💾 Saving to database - Session: {session_id}, User: {user_message}, Bot: {bot_message}")
        
        # Insert or update session
        c.execute('''
            INSERT OR REPLACE INTO sessions (session_id, last_activity) 
            VALUES (?, CURRENT_TIMESTAMP)
        ''', (session_id,))
        
        # Insert chat message
        c.execute('''
            INSERT INTO chats (session_id, user_message, bot_message) 
            VALUES (?, ?, ?)
        ''', (session_id, user_message, bot_message))
        
        conn.commit()
        
        # Verify the insert worked
        c.execute('SELECT COUNT(*) FROM chats WHERE session_id = ?', (session_id,))
        count = c.fetchone()[0]
        print(f"✅ Saved successfully! Total messages in session: {count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database save error: {e}")
        return False

def get_chat_history(session_id, limit=50):
    """Get chat history for a session"""
    try:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''
            SELECT user_message, bot_message, timestamp 
            FROM chats 
            WHERE session_id = ? 
            ORDER BY timestamp ASC 
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for user_msg, bot_msg, timestamp in c.fetchall():
            if user_msg:
                messages.append({"sender": "user", "text": user_msg, "timestamp": timestamp})
            if bot_msg:
                messages.append({"sender": "bot", "text": bot_msg, "timestamp": timestamp})
        
        conn.close()
        print(f"📖 Loaded {len(messages)} messages for session: {session_id}")
        return messages
    except Exception as e:
        print(f"❌ Database load error: {e}")
        return []

def get_all_sessions():
    """Get all chat sessions (for admin view)"""
    try:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''
            SELECT s.session_id, s.created_at, s.last_activity, COUNT(c.id) as message_count
            FROM sessions s
            LEFT JOIN chats c ON s.session_id = c.session_id
            GROUP BY s.session_id
            ORDER BY s.last_activity DESC
        ''')
        
        sessions = []
        for session_id, created_at, last_activity, message_count in c.fetchall():
            sessions.append({
                "session_id": session_id,
                "created_at": created_at,
                "last_activity": last_activity,
                "message_count": message_count
            })
        
        conn.close()
        print(f"📊 Found {len(sessions)} total sessions")
        return sessions
    except Exception as e:
        print(f"❌ Database sessions error: {e}")
        return []

def debug_database():
    """Debug function to check database status"""
    try:
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        
        # Check tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        print("📋 Database tables:", tables)
        
        # Check chats count
        c.execute("SELECT COUNT(*) FROM chats")
        chat_count = c.fetchone()[0]
        print(f"💬 Total chat messages: {chat_count}")
        
        # Check sessions count
        c.execute("SELECT COUNT(*) FROM sessions")
        session_count = c.fetchone()[0]
        print(f"👥 Total sessions: {session_count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database debug error: {e}")
        return False

# Initialize database when this module is imported
init_db()
# Run debug to check status
debug_database()