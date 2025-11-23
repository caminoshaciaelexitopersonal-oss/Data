import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

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
        # Table for jobs (part of MCP structure)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            job_type TEXT NOT NULL,
            status TEXT DEFAULT 'running',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        """)
        # Table for steps (part of MCP structure)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mcp_steps (
            step_id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            description TEXT NOT NULL,
            payload TEXT, -- Storing payload as JSON string
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (job_id)
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
        cursor.execute("INSERT OR IGNORE INTO sessions (session_id) VALUES (?)", (session_id,))
        self.conn.commit()
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieves a full session, including its jobs and steps."""
        cursor = self.conn.cursor()

        # Fetch session details
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        session_row = cursor.fetchone()
        if not session_row:
            return None

        session = dict(session_row)
        session['jobs'] = {}

        # Fetch associated jobs
        cursor.execute("SELECT * FROM jobs WHERE session_id = ?", (session_id,))
        job_rows = cursor.fetchall()

        for job_row in job_rows:
            job = dict(job_row)
            job['steps'] = {}

            # Fetch associated steps for each job
            cursor.execute("SELECT * FROM mcp_steps WHERE job_id = ?", (job['job_id'],))
            step_rows = cursor.fetchall()
            for step_row in step_rows:
                step = dict(step_row)
                if step.get('payload'):
                    step['payload'] = json.loads(step['payload'])
                job['steps'][step['step_id']] = step

            session['jobs'][job['job_id']] = job

        return session

    def create_job(self, session_id: str, job_id: str, job_type: str) -> Optional[Dict]:
        """Creates a new job within a session."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO jobs (job_id, session_id, job_type) VALUES (?, ?, ?)",
            (job_id, session_id, job_type)
        )
        self.conn.commit()
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Retrieves a job by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        job_row = cursor.fetchone()
        return dict(job_row) if job_row else None

    def create_mcp_step(self, step_id: str, job_id: str, description: str, payload: Optional[Dict]) -> Optional[Dict]:
        """Creates a new step for a job in the MCP context."""
        cursor = self.conn.cursor()
        payload_str = json.dumps(payload) if payload else None
        cursor.execute(
            "INSERT INTO mcp_steps (step_id, job_id, description, payload) VALUES (?, ?, ?, ?)",
            (step_id, job_id, description, payload_str)
        )
        self.conn.commit()
        return self.get_mcp_step(step_id)

    def get_mcp_step(self, step_id: str) -> Optional[Dict]:
        """Retrieves an MCP step by its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM mcp_steps WHERE step_id = ?", (step_id,))
        step_row = cursor.fetchone()
        if not step_row:
            return None
        step = dict(step_row)
        if step.get('payload'):
            step['payload'] = json.loads(step['payload'])
        return step

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

    def save_dataframe(self, session_id: str, df: pd.DataFrame):
        """Saves a DataFrame to a Parquet file in the session's directory."""
        session_dir = DB_STORAGE_PATH / session_id
        session_dir.mkdir(exist_ok=True)
        df.to_parquet(session_dir / "data.parquet")

    def load_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """Loads a DataFrame from a Parquet file in the session's directory."""
        session_dir = DB_STORAGE_PATH / session_id
        parquet_file = session_dir / "data.parquet"
        if parquet_file.exists():
            return pd.read_parquet(parquet_file)
        return None

# --- Dependency Injector ---

def get_state_store() -> StateStore:
    """Returns a singleton instance of the StateStore."""
    return StateStore()
