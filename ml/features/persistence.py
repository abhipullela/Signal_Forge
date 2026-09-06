"""Persistence features for emerging signals."""
from __future__ import annotations
import numpy as np
import pandas as pd

def calculate_persistence(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    baseline_available = out.get("baseline_available", out["baseline_volume"] > 0)
    out["above_baseline"] = baseline_available.astype(bool) & (out["volume"] > out["baseline_volume"])
    persistence = pd.Series(0.0, index=out.index)
    for _, indices in out.groupby("cluster_id").groups.items():
        count = 0
        for idx in indices:
            count = count + 1 if bool(out.loc[idx, "above_baseline"]) else 0
            persistence.loc[idx] = count
    out["persistence_windows"] = persistence
    out["persistence_score"] = persistence.clip(0, 3) / 3.0
    return out

def persistence_multiplier(windows: pd.Series) -> pd.Series:
    windows = pd.to_numeric(windows, errors="coerce").fillna(0)
    return np.select(
        [windows <= 0, windows == 1, windows == 2, windows >= 3],
        [0.85, 0.90, 0.95, 1.00],
        default=0.85,
    )
