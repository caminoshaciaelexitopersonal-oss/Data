import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# --- Configuration ---
DB_STORAGE_PATH = Path("backend/data")
DB_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_STORAGE_PATH / "sadi_state.db"

# --- StateStore Service ---

class StateStore:
    """
    A unified, persistent state management service using SQLite.
    This store replaces all previous in-memory state mechanisms.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StateStore, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._initialize_db()

    def _initialize_db(self):
        """
        Creates the necessary tables if they don't exist.
        """
        cursor = self.conn.cursor()
        # Table for sessions (replaces MCP in-memory store)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # Table for execution steps (replaces logger in-memory store)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS execution_steps (
            step_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            description TEXT NOT NULL,
            code TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        """)
        # Table for visualizations (replaces visualizations in-memory store)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS visualizations (
            viz_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            name TEXT NOT NULL,
            data TEXT, -- Storing data as JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        """)
        self.conn.commit()

    # --- Methods to replace legacy state management ---

    def create_session(self, session_id: str) -> Dict:
        """Creates and persists a new session."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sessions (session_id) VALUES (?)", (session_id,))
        self.conn.commit()
        return {"session_id": session_id}

    def log_step(self, session_id: str, description: str, code: str) -> int:
        """Logs a new execution step to the persistent store."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO execution_steps (session_id, description, code) VALUES (?, ?, ?)",
            (session_id, description, code)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_steps(self, session_id: str) -> List[Dict]:
        """Retrieves all steps for a given session."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM execution_steps WHERE session_id = ?", (session_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_visualization(self, session_id: str, name: str, data: Any):
        """Adds or updates a visualization in the persistent store."""
        cursor = self.conn.cursor()
        # Simple upsert logic: delete existing entry for the name, then insert new.
        cursor.execute("DELETE FROM visualizations WHERE session_id = ? AND name = ?", (session_id, name))
        cursor.execute(
            "INSERT INTO visualizations (session_id, name, data) VALUES (?, ?, ?)",
            (session_id, name, json.dumps(data))
        )
        self.conn.commit()

    def get_visualizations(self, session_id: str) -> Dict[str, Any]:
        """Retrieves all visualizations for a given session."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, data FROM visualizations WHERE session_id = ?", (session_id,))
        viz_data = {}
        for row in cursor.fetchall():
            viz_data[row['name']] = json.loads(row['data'])
        return viz_data

# --- Dependency Injector ---

def get_state_store() -> StateStore:
    """Returns a singleton instance of the StateStore."""
    return StateStore()
