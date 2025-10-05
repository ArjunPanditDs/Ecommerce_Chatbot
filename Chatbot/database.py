import sqlite3
import json
from datetime import datetime
import os

def init_db():
    """Initialize database and create tables"""
    conn = sqlite3.connect('chat_history.db')
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

def save_chat(session_id, user_message, bot_message):
    """Save chat message to database"""
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    
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
    conn.close()

def get_chat_history(session_id, limit=50):
    """Get chat history for a session"""
    conn = sqlite3.connect('chat_history.db')
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
    return messages

def get_all_sessions():
    """Get all chat sessions (for admin view)"""
    conn = sqlite3.connect('chat_history.db')
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
    return sessions

# Initialize database when this module is imported
init_db()