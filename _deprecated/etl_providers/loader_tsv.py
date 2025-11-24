import pandas as pd
from typing import Tuple, Dict, Any

def load(source: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads a TSV file into a pandas DataFrame."""
    meta = {"source": source, "loader": "tsv"}
    df = pd.read_csv(source, sep='\t')
    return df, meta
