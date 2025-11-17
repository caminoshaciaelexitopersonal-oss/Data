import pandas as pd
import pickle
from pathlib import Path
from typing import Optional

class SessionManager:
    """
    Manages the persistence of session data (DataFrames) to the filesystem.
    """
    _base_path = Path("data/sessions")

    def __init__(self):
        self._base_path.mkdir(parents=True, exist_ok=True)

    def save_dataframe(self, session_id: str, df: pd.DataFrame):
        """
        Saves a DataFrame to a file using the session_id.
        """
        session_file = self._base_path / f"{session_id}.pkl"
        with open(session_file, "wb") as f:
            pickle.dump(df, f)

    def load_dataframe(self, session_id: str) -> Optional[pd.DataFrame]:
        """
        Loads a DataFrame from a file using the session_id.
        Returns None if the session file does not exist.
        """
        session_file = self._base_path / f"{session_id}.pkl"
        if not session_file.exists():
            return None

        with open(session_file, "rb") as f:
            return pickle.load(f)

# Create a singleton instance for easy dependency injection
session_manager = SessionManager()
