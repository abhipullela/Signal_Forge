"""Novelty feature hooks.

The supplied V1 source bundle does not contain a validated novelty algorithm,
so this module deliberately provides a conservative, explicit baseline rather
than pretending that novelty has been learned.

For now novelty is measured as inverse historical cluster prevalence.
"""

from __future__ import annotations

import pandas as pd


def calculate_novelty(df: pd.DataFrame, cluster_column: str = "cluster_id") -> pd.DataFrame:
    """Add a bounded prevalence-based novelty score in [0, 1]."""
    out = df.copy()
    counts = out[cluster_column].value_counts()
    if counts.empty:
        out["novelty_score"] = 0.0
        return out
    prevalence = out[cluster_column].map(counts).astype(float)
    out["novelty_score"] = 1.0 / prevalence
    maximum = out["novelty_score"].max()
    if maximum > 0:
        out["novelty_score"] /= maximum
    return out
