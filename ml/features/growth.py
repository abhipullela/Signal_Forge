"""Growth, velocity and acceleration features.

Raw derivatives are retained for diagnostics, while scoring code should use
bounded/log-compressed representations to prevent sparse windows from
creating extreme scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

EPSILON = 1e-9


def calculate_volume_dynamics(df: pd.DataFrame) -> pd.DataFrame:
    """Add volume velocity, log growth and acceleration per cluster."""
    out = df.copy().sort_values(["cluster_id", "time_window"]).reset_index(drop=True)
    previous_volume = out.groupby("cluster_id")["volume"].shift(1).fillna(0.0)

    # Raw values are preserved for explainability/export.
    out["velocity"] = out["volume"] - previous_volume
    out["growth_rate"] = (
        np.log1p(out["volume"]) - np.log1p(previous_volume)
    ).replace([np.inf, -np.inf], np.nan).fillna(0.0)

    previous_velocity = out.groupby("cluster_id")["velocity"].shift(1).fillna(0.0)
    out["acceleration"] = out["velocity"] - previous_velocity

    # Bounded diagnostic features for downstream scoring.
    out["velocity_log"] = np.sign(out["velocity"]) * np.log1p(np.abs(out["velocity"]))
    out["acceleration_log"] = np.sign(out["acceleration"]) * np.log1p(np.abs(out["acceleration"]))
    return out


def calculate_growth_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compatibility alias for callers that prefer a feature-oriented name."""
    return calculate_volume_dynamics(df)
