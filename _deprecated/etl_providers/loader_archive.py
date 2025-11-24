import pandas as pd
from typing import Tuple, Dict, Any

def load(source: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Placeholder for archive loader."""
    meta = {"source": source, "loader": "archive", "status": "unimplemented"}
    df = pd.DataFrame()
    return df, meta
