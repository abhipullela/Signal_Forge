"""Signal ranking utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def rank_signals(df: pd.DataFrame, score_column: str = "signal_score") -> pd.DataFrame:
    """Rank clusters from strongest to weakest signal."""
    if df.empty:
        return df.copy()

    out = df.copy()
    out = out.sort_values(
        [score_column, "cluster_id"],
        ascending=[False, True],
        kind="mergesort",
    ).reset_index(drop=True)
    out["signal_rank"] = np.arange(1, len(out) + 1)
    return out


def top_signals(
    df: pd.DataFrame,
    n: int = 20,
    score_column: str = "signal_score",
) -> pd.DataFrame:
    return rank_signals(df, score_column=score_column).head(n).copy()
