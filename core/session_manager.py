import os
import json
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class SessionManager:
    def __init__(self, storage_dir="workspace/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_dir / "memory.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                updated_at DATETIME
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp DATETIME,
                json_data TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()

    def list_sessions(self):
        """Returns a list of all existing sessions, sorted by modification time."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC")
        rows = cur.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            # Parse datetime correctly for Streamlit's required mod_time formatting
            try:
                mod_time = datetime.fromisoformat(row[2]).timestamp()
            except:
                mod_time = datetime.now().timestamp()

            sessions.append({
                "id": row[0],
                "title": row[1] or "New Conversation",
                "mod_time": mod_time
            })
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a specific session and its messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cur.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[SessionManager] Error deleting session {session_id}: {e}")
            return False

    def clear_sessions(self) -> bool:
        """Delete all sessions and messages"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM messages")
            cur.execute("DELETE FROM sessions")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[SessionManager] Error clearing sessions: {e}")
            return False

    def load_session(self, session_id):
        """Loads a session's chat history array from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT json_data FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        rows = cur.fetchall()
        conn.close()
        
        chat_history = []
        for row in rows:
            try:
                chat_history.append(json.loads(row[0]))
            except Exception:
                continue
        return chat_history

    def save_session(self, session_id, chat_history):
        """Overwrites a session's chat history in SQLite."""
        if not session_id or not chat_history:
            return
            
        title = "New Conversation"
        for msg in chat_history:
            if msg.get("role") == "user":
                title_text = str(msg.get("content", ""))[:40]
                if len(str(msg.get("content", ""))) > 40:
                    title_text += "..."
                title = title_text
                break
                
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Upsert session
        cur.execute("INSERT OR REPLACE INTO sessions (id, title, updated_at) VALUES (?, ?, ?)", (session_id, title, now))
        
        # Refresh messages for the session
        cur.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        for msg in chat_history:
            role = msg.get("role", "unknown")
            content = str(msg.get("content", ""))
            json_blob = json.dumps(msg)
            cur.execute("INSERT INTO messages (session_id, role, content, timestamp, json_data) VALUES (?, ?, ?, ?, ?)",
                        (session_id, role, content, now, json_blob))
                        
        conn.commit()
        conn.close()

    def create_new_session_id(self):
        """Creates a new session in SQL to ensure list_sessions finds it immediately."""
        sess_id = f"session_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO sessions (id, title, updated_at) VALUES (?, ?, ?)", (sess_id, "New Conversation", now))
        conn.commit()
        conn.close()
        
        return sess_id
