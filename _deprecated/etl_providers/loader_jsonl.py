import pandas as pd
from typing import Tuple, Dict, Any

def load(source: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads a JSONL file into a pandas DataFrame."""
    meta = {"source": source, "loader": "jsonl"}
    df = pd.read_json(source, lines=True)
    return df, meta
